import copy
import logging
import math
import multiprocessing as mp
import os
from collections.abc import Iterable
from datetime import datetime, timedelta
from multiprocessing import Queue
from random import randint
from typing import Dict, List, Text

import pytz
from pandas import DataFrame, Series, read_csv, read_json  # noqa F401

from fakeme import config
from fakeme.fields import FieldRules
from fakeme.utils import log
from fakeme.values import list_generator, values_generator

mp.set_start_method("fork")
q = Queue()

tmp_prefix = "tmp_"


class DataGenerator:
    def __init__(
        self,
        schema: List,
        with_data: List = None,
        chained: Dict = None,
        table_id: Text = None,
        alias_chain: Dict = None,
        appends: Dict = None,
        cli_path=None,
        prefix=None,
    ):
        self.schema = schema
        self.chained = chained
        self.table_id = table_id
        self.chains = alias_chain
        self.fr = FieldRules()
        self.chained_df = None
        self.column_df = None
        self.cfg = config.cfg
        self.file_format = self.cfg.output.file_format
        self.appends = appends
        self.with_data = with_data
        self.prefix = prefix if not cli_path else cli_path
        self.table_settings = self.cfg.tables.get(self.table_id, None)
        self.row_numbers = (
            self.table_settings.row_numbers
            if self.table_settings
            else self.cfg.row_numbers
        )

    def __chain_tables(self, dir_files: List) -> List:
        table_chain = self.chains[self.table_id]
        key = list(table_chain.keys())[0]
        if self.cfg.output.file_name_style:
            # todo: move to method, or store file_name highlevel
            file_name = eval(
                f"'{table_chain[key]['table']}'.{self.cfg.output.file_name_style}()"
            )
        else:
            file_name = table_chain[key]["table"]
        file_name = (
            "{}.{}".format(file_name, self.file_format)
            if "." not in table_chain[key]["table"]
            else table_chain[key]["table"]
        )
        src_file = os.path.join(self.prefix, file_name)
        if not os.path.isfile(src_file) and self.prefix not in src_file:
            src_file = os.path.join(self.prefix, src_file)
            if not os.path.isfile(src_file):
                raise ValueError(f"{src_file} is not a file. Current dir {os.getcwd()}")
        dir_files.append(src_file)
        return dir_files

    def get_depend_on_file(self):
        """find depends on other tables (data files)
        TODO: add support for multiple depends on files
        """
        dir_files = []
        if self.chains and self.table_id in self.chains:
            dir_files = self.__chain_tables(dir_files)
        else:
            for item in self.schema:
                if item["name"] in self.chained:
                    chained_tables = [
                        table
                        for table in self.chained[item["name"]]
                        if table != self.table_id
                    ]
                    [
                        dir_files.append(file_name)
                        if file_name.startswith(table)
                        else None
                        for table in chained_tables
                        for file_name in os.listdir(self.prefix)
                    ]
                elif "all" in self.prefix and item["name"] in self.chains["all"]:
                    table_chain = self.chains["all"]
                    key = table_chain.keys()[0]
                    if table_chain[key]["table"] != self.table_id:
                        src_file = os.path.join(
                            self.prefix,
                            "{}.{}".format(table_chain[key]["table"], self.file_format),
                        )
                        if not os.path.isfile(src_file):
                            raise ValueError
                        dir_files.append(src_file)
        if dir_files:
            log.info("Depend on: {}".format(dir_files))
            return os.path.join(self.prefix, dir_files[0])
        else:
            return []

    def resolve_dependencies(self):
        """find dependencies on different ways and prepare self.chained_df"""
        depend_on_file = None
        if self.appends and self.table_id in self.appends:
            depend_on_file = [
                os.path.join(self.prefix, "{}.{}".format(name, self.file_format))
                for name in self.appends[self.table_id]
            ]
        elif self.chained or self.chains:
            depend_on_file = self.get_depend_on_file()
        if depend_on_file:
            if isinstance(depend_on_file, str):
                if self.table_id in os.path.basename(depend_on_file):
                    return tmp_prefix
                self.chained_df = self._read_df_from_file(depend_on_file)
            elif isinstance(depend_on_file, Iterable):
                for file_name in depend_on_file:
                    if self.chained_df is None:
                        self.chained_df = self._read_df_from_file(file_name)
                    else:
                        self.chained_df = self.chained_df.merge(
                            how="outer", right=self._read_df_from_file(file_name)
                        )
        return self.chained_df

    def _read_df_from_file(self, depend_on_file):
        """return correct pandas export method depend on expected file format"""
        try:
            result = eval(f"read_{self.file_format}('{depend_on_file}')")
        except ValueError:
            try:
                result = eval(
                    f"read_{self.file_format}('{depend_on_file}',  lines=True)"
                )
            except ValueError:
                result = None
        return result

    def _read_values_from_txt(self, path):
        with open(path, "r") as data_file:
            return [x.replace("\n", "") for x in data_file.readlines()]

    def init_timestamps_values(self):
        # TODO: need to refactor this
        global current_time, last_time

        timezone = pytz.timezone(self.cfg.timezone)
        current_time = datetime.now(timezone).strftime("%Y-%m-%d-%H.%M.%S.%f")
        last_time = (datetime.now(timezone) - timedelta(hours=48)).strftime(
            "%Y-%m-%d-%H.%M.%S.%f"
        )

    def get_data_frame(self):
        """generate frame with data per table"""
        self.init_timestamps_values()
        logging.info("Start Data Generation")

        data_frame = DataFrame()
        current_obj = copy.deepcopy(self)
        num_cores = mp.cpu_count()
        with mp.Pool(num_cores) as pool:
            TASKS = [(current_obj, item) for item in self.schema]

            results = [pool.apply_async(column_generation, t) for t in TASKS]

            for r in results:
                r.get()

        num = 0
        while not q.empty():
            file_name = q.get()
            with open(file_name, "r") as column_file:
                column = [
                    line.split("\n")[0] if line != "None\n" else None
                    for line in column_file.readlines()
                ]
                data_frame.insert(
                    num, column=file_name.split(tmp_prefix)[1], value=Series(column)
                )
                num += 1
            os.remove(file_name)
        return data_frame

    def get_column_generating_rule(self, field_name):
        """method to get field rule"""
        field_rule = self.fr.rules.loc[self.fr.rules["field"] == field_name].to_dict()
        if not field_rule.get("field"):
            field_rule = {}
        for elem in field_rule:
            field_rule[elem] = field_rule[elem][list(field_rule[elem].keys())[0]]
        return field_rule

    def get_values_from_chained_column(self, _field_name, _matches_k):
        """get params reversed and matches_k"""
        matches = self.chains.get(self.table_id, {}).get(_field_name, {}).get("matches")
        revers = self.chains.get(self.table_id, {}).get("revers", False)
        return matches, revers

    def get_dataframe_column(self, _src_column, _matches_k, _revers):
        """get column for field from chained dataframe"""
        df_column = self.chained_df[[_src_column]]
        splited_index = int(max(df_column.index) * _matches_k)
        if _revers:
            df_column = df_column.reindex(index=df_column.index[::-1])
        df_column = df_column.reindex(
            index=df_column.index[0 : splited_index + 1]  # noqa E203
        )  # noqa E203
        df_column = df_column.to_dict()[_src_column].values()
        return df_column

    def get_column_from_chained(self, field_name, matches_k):
        field_chain = self.chains[self.table_id].get(field_name, {})
        if not field_chain:
            return None
        alias = field_chain.get("alias", None)
        src_column = alias or field_name
        df_column = None
        self.chained_df = self.resolve_dependencies()
        if self.chained_df is not None:
            if isinstance(self.chained_df, str) and self.chained_df == tmp_prefix:
                # mean we depend on column from current ds
                df_column = self._read_values_from_txt(f"{tmp_prefix}{field_name}")
            elif src_column in self.chained_df.columns:
                matches_k, revers = self.get_values_from_chained_column(
                    field_name, matches_k
                )
                matches_k = matches_k or self.cfg.matches
                df_column = self.get_dataframe_column(src_column, matches_k, revers)
        return df_column

    def __process_table_settings(
        self, column_cfg, unique_values, unique, matches_k, percent_of_nulls
    ):
        column_settings = self.table_settings.columns.get(column_cfg.name, {})
        if column_settings:
            unique_values = column_settings.unique_values or column_settings.row_numbers
            unique = column_settings.unique
            matches_k = column_settings.matches
            percent_of_nulls = column_settings.percent_of_nulls
        else:
            matches_k = self.table_settings.matches
            percent_of_nulls = self.table_settings.percent_of_nulls
        return unique_values, unique, matches_k, percent_of_nulls

    def __process_df_column(self, df_column, column, column_cfg, unique_values, unique):
        if column_cfg.type == "LIST":
            # mean we need to create as output lists with values from df_column
            max_number_of_elements = column_cfg.max_number or self.cfg.max_list_values
            min_number_of_elements = column_cfg.min_number or self.cfg.min_list_values
            for _ in range(unique_values):
                value = list_generator(
                    list(df_column), min_number_of_elements, max_number_of_elements
                )
                column.append(value)
        else:
            append_times = int(unique_values / len(df_column)) + 1
            column = list(df_column) * append_times
            column = column[:unique_values]
        if unique:
            column = self.filter_on_unique(column)
        return column

    def column_generator(self, column_cfg: Dict):
        """create column with values"""
        log.info("Generate column {}".format(column_cfg.name))
        # unique_values - count of unique values in column in this table
        # unique - flag, must be all values unique in this table or not
        column = []
        unique_values = self.row_numbers
        matches_k = self.cfg.matches
        unique = None
        percent_of_nulls = self.cfg.percent_of_nulls

        if self.table_settings:
            (
                unique_values,
                unique,
                matches_k,
                percent_of_nulls,
            ) = self.__process_table_settings(
                column_cfg, unique_values, unique, matches_k, percent_of_nulls
            )  # todo: refactor this
        # get field rule
        generating_rule = self.get_column_generating_rule(column_cfg.name)

        if self.table_id in self.chains:
            df_column = self.get_column_from_chained(column_cfg.name, matches_k)
        else:
            df_column = None

        if not unique_values:
            unique_values = self.row_numbers
        if df_column:
            column = self.__process_df_column(
                df_column, column, column_cfg, unique_values, unique
            )

        if len(column) < unique_values:
            unique_values = unique_values - len(column)
        else:
            column = column[:unique_values]
            unique_values = 0
        if (
            column_cfg.len
            and math.isnan(generating_rule["len"])
            or column_cfg.len
            and generating_rule["len"] > column_cfg.len
        ):
            generating_rule["len"] = column_cfg.len
        while unique_values:
            value = values_generator(generating_rule, unique)
            column.append(value)
            unique_values -= 1
        total_rows = self.row_numbers - len(column)
        rel_size = total_rows / len(column)
        num_copy = int(rel_size)
        base_column = copy.deepcopy(column)
        for _ in range(num_copy):
            column += base_column
        float_adding = rel_size - num_copy

        column += base_column[: int(len(base_column) * float_adding)]
        column = self.__config_mode_processing(column, column_cfg, percent_of_nulls)
        return column

    @staticmethod
    def __config_mode_processing(column, column_cfg, percent_of_nulls):
        if column_cfg.mode:
            nullable = column_cfg.mode == "nullable"
            if nullable:
                column_len = len(column)
                count_of_nulls = int(column_len * percent_of_nulls)
                for i in range(count_of_nulls):
                    column[randint(0, column_len - 1)] = None
        return column

    def filter_on_unique(self, column):
        return list(set(column))


def column_generation(current_obj: DataGenerator, column: dict) -> None:

    file_name = f"{tmp_prefix}{column.name}"
    with open(file_name, "w+") as column_tmp:
        for line in current_obj.column_generator(column):
            column_tmp.write(str(line))
            column_tmp.write(str("\n"))
    q.put(file_name)
    return file_name
