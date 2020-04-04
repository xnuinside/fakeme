""" main module that contains RunGenerator class that used to init data generation """
import os
import inspect

from collections import defaultdict
from typing import List, Dict, Text, Union
from fakeme.config import Config
from fakeme.tables import MultiTableRunner
from fakeme.fields import FieldRulesExtractor

from datetime import datetime

created = []


class Fakeme:

    def __init__(self,
                 tables: List,
                 with_data: List = None,
                 settings: Dict = None,
                 dump_schema: bool = True,
                 rls: Dict = None,
                 appends: List = None,
                 cli_path: Text = None):
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

        self.tables = tables
        self.cfg = Config(settings).get_config()
        self.rls = rls if rls else None or {}
        self.dump_schema = dump_schema
        self.path_prefix = cli_path or os.path.dirname(inspect.stack()[1][1])
        if not cli_path and os.getcwd() not in self.path_prefix:
            self.path_prefix = os.path.join(os.getcwd(), self.path_prefix)
        self.appends = appends or []
        self.cli_path = cli_path
        self.with_data = self.validate_data_source(with_data)
        self.schemas = None

    def validate_data_source(self, paths_list):
        if not paths_list:
            paths_list = []
        validated_list = []
        for path in paths_list:
            if not os.path.isfile(path):
                if self.path_prefix not in path:
                    path = os.path.join(self.path_prefix, path)
                    if not os.path.isfile(path):
                        raise Exception(f'Could not find the path {path} from "with_data" parameter')
            validated_list.append(path)
        return set(validated_list)

    def run(self):
        """
            call method to run data generation
            # todo: rewrite priority description
            priority 0 - tables that target for relations (
            priority 1 - tables that target for relations and in relations
            priority 2 - tables what not in self.append
            priority 3 - tables in self.append

        """
        print("Fakeme starts at", datetime.now())
        # get all fields and schemas for tables

        self.schemas, fields = MultiTableRunner(self.tables, prefix=self.path_prefix, settings=self.cfg).\
            get_fields_and_schemas(dump_schema=self.dump_schema)
        if self.cfg['auto_alias']:
            self.resolve_auto_alises()
        priority_dict = self.create_priority_table_dict()
        field_extractor = FieldRulesExtractor(fields)
        # generate "value_rules.json" with rules for fields
        field_extractor.generate_rules()

        self.linked_fields = field_extractor.get_chains(self.schemas, self.rls)

        for level in priority_dict:
            for table in priority_dict[level]:
                if table not in created and table not in self.with_data \
                        and table not in priority_dict.get(level+1, []):
                    self.create_table(table)
        print("Fakeme finished successful \n", datetime.now())

    def resolve_auto_alises(self):
        for table in self.schemas:
            for column in self.schemas[table][0]:
                # column - dict with column description
                alias_column_name = column.get('alias', None) or column['name']
                relative_table = self.table_prefix_in_column_name(alias_column_name)

                if relative_table:
                    if table not in self.rls:
                        self.rls[table] = {}

                    self.rls[table].update({
                        column['name']: {
                            'alias': alias_column_name.split('_')[1],
                            'table': relative_table,
                            'matches': column.get('matches') or self.cfg['matches']
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
            print(f"Found alias with {table_name}")
            return table_name

        return

    def create_table(self, table):
        """ run table creation """
        target_path = os.path.join(self.path_prefix, "{}.{}".format(table, self.cfg['output']['file_format']))

        self.schemas[table][1].create_data(
            file_path=target_path,
            with_data=self.with_data,
            chained=self.linked_fields,
            alias_chain=self.rls,
            appends=self.appends,
            prefix=self.path_prefix,
            cli_path=self.cli_path)

        created.append(table)

    def create_priority_table_dict(self):
        priority_dict = defaultdict(set)
        # 3
        [priority_dict[3].add(k) for k in self.appends]

        chains_tables = set([k for k in self.rls])

        if self.rls:
            priority_dict[0] = set([table_name for table_name in self.schemas if table_name not in chains_tables])
        else:
            priority_dict[0] = set(self.schemas.keys())

        if self.with_data:
            for data_file in self.with_data:
                priority_dict[0].add(data_file)
        link_dict = {}
        tables_list = [x for x in self.schemas]
        for table in chains_tables:
            self_table = self.rls[table]
            for field in self_table:
                field_dict = self_table[field]
                if field_dict['table'] in tables_list or field_dict['table'] in self.with_data:
                    if not link_dict.get(field_dict['table']):
                        link_dict[field_dict['table']] = set([])
                    link_dict[field_dict['table']].add(table)
        while link_dict:
            for n in range(0, 6):
                table_moved = []
                for table in link_dict:
                    if table in priority_dict[n]:
                        [priority_dict[n+1].add(tb_name) for tb_name in link_dict[table]]
                        table_moved.append(table)
                if table_moved:
                    for table in table_moved:
                        del link_dict[table]
        return priority_dict
