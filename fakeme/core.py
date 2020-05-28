""" main module that contains RunGenerator class that used to init data generation """
import os
import inspect

from copy import deepcopy
from collections import defaultdict
from typing import List, Dict, Text, Union, Tuple, Optional
from fakeme.tables import MultiTableRunner
from fakeme.fields import FieldRulesExtractor, FieldRules
from fakeme.config import Config
from fakeme.utils import log
from fakeme import config
from fakeme.walker import Walker


from datetime import datetime

created = []


class FakemeException(Exception):
    pass


class Fakeme:
    def __init__(self,
                 tables: Union[List, Tuple[str, Union[str, dict, list]]],
                 with_data: List = None,
                 settings: Dict = None,
                 dump_schema: bool = True,
                 rls: Dict = None,
                 appends: List = None,
                 cli_path: Text = None,
                 field_rules: Optional[List] = None,
                 paths_with_scripts: Optional[List] = None):
        """
        Main Class to start data generation

        :param tables: list with tuples, what contain
            (dataset/database (optional), table_id/table_name, path_to_table_schema
            or schema in one of supported formats), example:

                [
                    ("yourdatabase", "table_name1", "schemas/table_name1.json"),
                    ("yourdatabase", "table_name2", schema_in_python_object),
                    ("table_name3", "schemas/your_schema_in_json.json") ...
                ]

                where
                        schema_in_python_object = [
                                {
                                  "type": "STRING",
                                  "name": "field1",
                                  "mode": "NULLABLE"
                                 },
                                 {
                                  "type": "STRING",
                                  "name": "field2"
                                 }]
        :type tables: list
        :param settings:
            Example:
                    settings = {
                        'table_id' : {
                            'field': {
                                'unique_values': count_of_unique_values_in_column,
                                'unique': True
                            }
                        }
                    }
        :type settings: dict
        :param dump_schema:
        :type dump_schema:
        :param rls:
        :type rls:
        """
        if not field_rules:
            field_rules = []
        FieldRules.user_rules = field_rules
        self.tables = self.normalise_tables(tables)
        if not settings:
            settings = {}
        config.cfg = Config(**settings)
        self.paths_with_scripts = paths_with_scripts if paths_with_scripts else []
        self.cfg = config.cfg
        self.cfg.path_prefix = cli_path or os.path.dirname(inspect.stack()[1][1])
        self.rls = rls if rls else None or {}
        self.dump_schema = dump_schema
        # todo: remove this things with paths
        if not cli_path and os.getcwd() not in self.cfg.path_prefix:
            self.cfg.path_prefix = os.path.join(os.getcwd(), self.cfg.path_prefix)
        self.appends = appends or []
        self.cli_path = cli_path
        self.with_data = self.validate_data_source(with_data)

    @staticmethod
    def normalise_tables(tables):
        if (isinstance(tables, Tuple) or isinstance(tables, List)) and isinstance(tables[0], str):
            # mean we have only one table definition
            tables = tuple(tables,)
            return [tables]
        elif isinstance(tables, List):
            for table in tables:
                if not isinstance(table[0], str):
                    raise FakemeException(
                        f"Tables definitions must be presented like a tuple ('table_name', schema). "
                        f"You provided: {table}")
            return tables

    def validate_data_source(self, paths_list):
        if not paths_list:
            paths_list = []
        validated_list = []
        for path in paths_list:
            if not os.path.isfile(path):
                if self.cfg.path_prefix not in path:
                    path = os.path.join(self.cfg.path_prefix, path)
                    if not os.path.isfile(path):
                        raise Exception(f'Could not find the path {path} from "with_data" parameter')
            validated_list.append(path)
        return set(validated_list)

    def run(self):
        log.info("Fakeme starts at", datetime.now())
        # get all fields and schemas for tables
        self.schemas, fields = MultiTableRunner(
            self.tables, rls=self.rls).\
            get_fields_and_schemas(dump_schema=self.dump_schema)

        if self.cfg.auto_alias:
            self.resolve_auto_alises()
        walk_list = []
        for path in self.paths_with_scripts:
            walker = Walker(path_to_dir=path, extension="hql", recursive=True)
            [walk_list.append(path) for path in walker.walk()]

        field_extractor = FieldRulesExtractor(fields, walk_list)
        # generate "value_rules.json" with rules for fields
        field_extractor.generate_rules()
        # to do: remove and just use rls dict
        self.rls = field_extractor.get_chains(self.schemas, self.rls)

        priority_dict = self.create_tables_priority_graph()
        print(priority_dict)
        print('priority_dict')
        for level, tables in priority_dict.items():
            print(level)
            for table in tables:
                if table not in created and table not in self.with_data:
                    self.create_table(table)
        log.info("Fakeme finished successful \n", datetime.now())

    def resolve_auto_alises(self):
        for table in self.schemas:
            for column in self.schemas[table][0]:
                # column - dict with column description
                alias_column_name = column.alias or column.name
                relative_table = self.table_prefix_in_column_name(alias_column_name)
                if relative_table:
                    matches = self.cfg.matches
                    if self.cfg.tables.get(table):
                        column_settings = self.cfg.tables.get(table).columns.get(column.name, {})
                        if column_settings:
                            matches = column_settings.matches
                        else:
                            matches = self.cfg.tables.get(table).matches
                    if table not in self.rls:
                        self.rls[table] = {}
                    self.rls[table].update({
                        column.name: {
                            'alias': alias_column_name.split('_')[1],
                            'table': relative_table,
                            'matches': matches
                        }
                    })

    def table_prefix_in_column_name(self, column_name: Text) -> Union[Text, None]:
        """ check do we have table name prefix in column name, to get possible auto aliasing """
        table_names = list(self.schemas.keys())

        column_name = column_name.split('_')[0]
        if column_name.endswith('y'):
            table_name = column_name.replace('y', 'ies')
        elif column_name.endswith('s'):
            table_name = column_name + 'es'
        else:
            table_name = column_name + 's'

        if table_name in table_names:
            log.info(f"Found alias with {table_name}")
            return table_name

        return

    def create_table(self, table):
        """ run table creation """

        target_path = os.path.join(self.cfg.path_prefix, "{}.{}".format(table, self.cfg.output.file_format))

        self.schemas[table][1].create_data(
            file_path=target_path,
            with_data=self.with_data,
            chained={},
            alias_chain=self.rls,
            appends=self.appends,
            prefix=self.cfg.path_prefix,
            cli_path=self.cli_path)

        created.append(table)

    def create_tables_priority_graph(self):
        priority_dict = defaultdict(set)
        priority_dict_temp = defaultdict(int)
        clean_up_rls = defaultdict(set)
        rls_copy = deepcopy(self.rls)
        """
        {table: prior}
        """
        upstream = defaultdict(set)

        def get_table_level(_table, level=0):
            # todo: cover that with tests
            if not level:
                if _table in priority_dict_temp:
                    level = priority_dict_temp[_table]
                else:
                    level = 0
            dependency = self.rls[_table]

            for field, alias_data in dependency.items():
                # iter on dependencies of each table
                alias_table = alias_data['table']
                alias_field = alias_data['alias']
                if field in clean_up_rls and alias_table in clean_up_rls[field]:
                    # mean we already added similar field
                    continue
                elif alias_field == field:
                    # mean this is a auto chain
                    clean_up_rls[alias_field].add(alias_table)
                    # get alias table dependencies ()
                if priority_dict_temp.get(alias_table):
                    level = priority_dict_temp[alias_table] + 1
                else:
                    level += 1
                _level = get_table_level(alias_table, level-1)
                level = _level +1
                priority_dict_temp[alias_table] = _level
                upstream[alias_table].add(table)
            return level
        for table in rls_copy:
            # iter on each table
            if table not in priority_dict_temp:
                priority_dict_temp[table] = get_table_level(table)

        def increment_upstream(upstreamed):
            for table_ in upstreamed:
                if priority_dict_temp.get(table) >= priority_dict_temp.get(table_):
                    priority_dict_temp[table_] = priority_dict_temp[table] + 1
                    if table_ in upstream:
                        increment_upstream(upstream[table_])

        for table, upstreamed in upstream.items():
            increment_upstream(upstreamed)

        for table, level in priority_dict_temp.items():
            priority_dict[level].add(table)
        [priority_dict[len(priority_dict)].add(k) for k in self.appends]
        for table in priority_dict[0]:
            for field in self.rls[table]:
                alias_table_name = self.rls[table][field]['table']
                alias_field = self.rls[table][field]['alias']
                if alias_field == field and self.rls[alias_table_name].get(alias_field):
                    del self.rls[alias_table_name][field]
        return dict(sorted(priority_dict.items()))
