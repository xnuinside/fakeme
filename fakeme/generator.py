import os
import copy
import multiprocessing as mp
from multiprocessing import Queue
from datetime import datetime, timedelta
import pytz
from collections.abc import Iterable
import logging
from typing import Text, List, Dict
from pandas import DataFrame, Series, read_csv, read_json  # noqa F401

from fakeme.fields import FieldRules
from fakeme.values import values_generator

supported_types = ['STRING', 'INTEGER', 'FLOAT', 'LIST']

q = Queue()


class DataGenerator:
    def __init__(self,
                 schema: List,
                 with_data: List = None,
                 settings: Dict = None,
                 chained: Dict = None,
                 table_id: Text = None,
                 alias_chain: Dict = None,
                 appends: Dict = None,
                 cli_path=None,
                 prefix=None
                 ):
        self.schema = self.schema_validation(schema)
        self.settings = settings or {}
        self.chained = chained
        self.table_id = table_id
        self.chains = alias_chain
        self.fr = FieldRules()
        self.chained_df = None
        self.column_df = None
        self.file_format = self.settings['output']['file_format']
        self.appends = appends
        self.with_data = with_data
        self.prefix = prefix if not cli_path else cli_path
        self.table_settings = self.settings.get('tables', {}).get(self.table_id, {})
        self.row_numbers = self.table_settings.get('row_numbers') or self.settings['row_numbers']

    def get_depend_on_file(self):
        """ find depends on other tables (data files)
            TODO: add support for multiple depends on files
        """
        dir_files = []
        if self.chains and self.table_id in self.chains:
            table_chain = self.chains[self.table_id]
            key = list(table_chain.keys())[0]
            file_name = "{}.{}".format(table_chain[key]['table'], self.file_format) if '.' not in table_chain[
                key]['table'] else table_chain[key]['table']
            src_file = os.path.join(self.prefix, file_name)
            if not os.path.isfile(src_file) and self.prefix not in src_file:
                src_file = os.path.join(self.prefix, src_file)
                if not os.path.isfile(src_file):
                    raise ValueError(f'{src_file} is not a file. Current dir {os.getcwd()}')
            dir_files.append(src_file)
        else:
            for item in self.schema:
                if item['name'] in self.chained:
                    chained_tables = [
                        table for table in self.chained[
                            item['name']] if table != self.table_id]
                    [dir_files.append(file_name) if file_name.startswith(table) else None
                     for table in chained_tables for file_name in os.listdir(
                        self.prefix)]
                elif 'all' in self.prefix and item['name'] in self.chains['all']:
                    table_chain = self.chains['all']
                    key = table_chain.keys()[0]
                    if table_chain[key]['table'] != self.table_id:
                        src_file = os.path.join(self.prefix, "{}.{}".format(
                            table_chain[key]['table'], self.file_format))
                        if not os.path.isfile(src_file):
                            raise ValueError
                        dir_files.append(src_file)
        if dir_files:
            print("Depend on: {}".format(dir_files))
            return os.path.join(self.prefix, dir_files[0])
        else:
            return []

    def schema_validation(self, schema):
        for item in schema:
            self.type_validation(item.get('type', 'STRING'))
        return schema

    @staticmethod
    def type_validation(type_name):
        if type_name not in supported_types:
            raise ValueError

    def _settings_validation(self, settings):
        raise NotImplementedError

    def resolve_dependencies(self):
        """ find dependencies on different ways and prepare self.chained_df"""
        depend_on_file = None
        if self.appends and self.table_id in self.appends:
            depend_on_file = [os.path.join(self.prefix, "{}.{}".format(
                name, self.file_format)) for name in self.appends[self.table_id]]
        elif self.chained or self.chains:
            depend_on_file = self.get_depend_on_file()
        if depend_on_file:
            if isinstance(depend_on_file, str):
                self.chained_df = self._read_df_from_file(depend_on_file)
            elif isinstance(depend_on_file, Iterable):
                for file_name in depend_on_file:
                    if self.chained_df is None:
                        self.chained_df = self._read_df_from_file(file_name)
                    else:
                        self.chained_df = self.chained_df.merge(
                            how='outer', right=self._read_df_from_file(file_name))
        return self.chained_df

    def _read_df_from_file(self, depend_on_file):
        """ return correct pandas export method depend on expected file format """
        result = eval(f"read_{self.file_format}(\'{depend_on_file}\')")
        return result

    def init_timestamps_values(self):
        # TODO: need to refactor this
        global current_time, last_time

        timezone = pytz.timezone(self.settings.get('timezone', 'UTC'))
        current_time = datetime.now(timezone).strftime("%Y-%m-%d-%H.%M.%S.%f")
        last_time = (datetime.now(timezone)
                     - timedelta(hours=48)).strftime("%Y-%m-%d-%H.%M.%S.%f")

    def get_data_frame(self):
        """ generate frame with data per table"""
        self.init_timestamps_values()
        logging.info("Start Data Generation")

        data_frame = DataFrame()
        current_obj = copy.deepcopy(self)
        num_cores = mp.cpu_count()
        pool = mp.Pool(num_cores)
        jobs = []

        for num, item in enumerate(self.schema):
            jobs.append(pool.apply_async(column_generation, (current_obj, item)))

            # wait for all jobs to finish
        for job in list(jobs):
            job.get()

        # clean up
        pool.close()

        num = 0
        while not q.empty():
            file_name = q.get()
            with open(file_name, 'r') as column_file:
                column = [line.split('\n')[0] for line in column_file.readlines()]
                data_frame.insert(num, column=file_name.split('tmp_')[1],
                                  value=Series(column))
                num += 1
            os.remove(file_name)
        return data_frame

    def get_field_rule(self, field_name):
        """ method to get field rule """
        field_rule = self.fr.rules.loc[self.fr.rules['field']
                                       == field_name].to_dict()
        if not field_rule.get('field'):
            field_rule = {}
        for elem in field_rule:
            field_rule[elem] = field_rule[elem][list(field_rule[elem].keys())[0]]
        return field_rule

    def get_values_from_chained_column(self, _field_name, _matches_k):
        """ get params reversed and matches_k """
        return self.chains.get(self.table_id, {}).get(_field_name, {}).get(
            'matches'), self.chains.get(self.table_id, {}).get('revers', False)

    def get_dataframe_column(self, _src_column, _matches_k, _revers):
        """ get column for field from chained dataframe """
        df_column = self.chained_df[[_src_column]]
        splited_index = int(max(df_column.index) * _matches_k)
        if _revers:
            df_column = df_column.reindex(index=df_column.index[::-1])
        df_column = df_column.reindex(index=df_column.index[0:splited_index+1])
        df_column = df_column.to_dict()[_src_column].values()
        return df_column

    def get_column_from_chained(self, field_name, matches_k):
        field_chain = self.chains[self.table_id].get(field_name, {})
        if not field_chain:
            return None
        alias = field_chain.get('alias', None)
        src_column = alias or field_name
        df_column = None
        self.chained_df = self.resolve_dependencies()
        if self.chained_df is not None:
            matches_k, revers = self.get_values_from_chained_column(field_name, matches_k)
            if src_column in self.chained_df.columns:
                df_column = self.get_dataframe_column(src_column, matches_k, revers)
        return df_column

    def column_generator(self, field_name):
        """ create column with values """
        print("Generate column {}".format(field_name))
        column, unique_values = [], None
        # get field rule
        field_rule = self.get_field_rule(field_name)

        # get settings
        matches_k = self.settings['matches']

        if self.table_id in self.chains:
            df_column = self.get_column_from_chained(field_name, matches_k)
        else:
            df_column = None
        if self.table_settings:
            if field_name in self.table_settings:
                unique_values = self.table_settings[field_name].get('unique_values') or self.row_numbers
            elif (isinstance(
                    list(self.table_settings.keys())[0], tuple)) and field_name \
                    in list(self.table_settings.keys())[0]:
                unique_values = self.table_settings[list(self.table_settings.keys())[0]].get(
                    'unique_values') or self.row_numbers
        if not unique_values:
            unique_values = self.row_numbers
        if df_column:
            append_times = int(unique_values / len(df_column)) + 1
            column = list(df_column) * append_times
            column = column[:unique_values]

        if len(column) < unique_values:
            unique_values = unique_values - len(column)
        else:
            column = column[:unique_values]
            unique_values = 0
        while unique_values:
            value = values_generator(field_rule)
            column.append(value)
            unique_values -= 1
        total_rows = self.row_numbers - len(column)
        rel_size = total_rows / len(column)
        num_copy = int(rel_size)
        base_column = copy.deepcopy(column)
        for _ in range(num_copy):
            column += base_column
        float_adding = rel_size - num_copy
        column += base_column[:int(len(base_column) * float_adding)]

        return column


def column_generation(current_obj: DataGenerator,
                      _item: dict) -> None:
    file_name = 'tmp_{}'.format(_item['name'])
    with open(file_name, 'w+') as column_tmp:
        for line in current_obj.column_generator(_item['name']):
            column_tmp.write(str(line))
            column_tmp.write(str('\n'))
    q.put(file_name)
