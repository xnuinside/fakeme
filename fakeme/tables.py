""" classes to work with tables """

import os
import json
from typing import List, Dict, Text
from fakeme.generator import DataGenerator
from fakeme.output import get_writer


class SchemaExtractor(object):

    def __init__(self,
                 schema_path: Text,
                 folder: Text = None,
                 table_id: Text = "",
                 dump_schema: bool = True):
        self.schema_path = schema_path
        self.folder = folder or self.extract_folder()
        self.table_id = table_id
        self.dump_schema = dump_schema

    def extract_folder(self):
        if '/' in self.schema_path:
            splited = self.schema_path.split('/')
            folder, _ = splited[(len(splited) - 2):]
            if folder == 'schemas':
                folder = ''
        else:
            folder = '.'
        return folder

    def get_schema(self):
        """ get schema in BQ format """
        if self.schema_path.endswith('.json'):
            with open(self.schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
        else:
            raise NotImplementedError('Supports only `.json` format')
        return schema


class TableRunner(object):
    """
    `schema_in_obj` arg example:

        [
            {"type": "STRING", "name": "name", "mode": "NULLABLE"},
            {"type": "STRING", "name": "id", "mode": "NULLABLE"}
        ]

    """
    def __init__(self,
                 table_id: Text,
                 settings: Dict,
                 schema: List,
                 dataset_id: Text = None,
                 dump_schema: bool = False
                 ):
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.settings = settings
        self.schema = schema

    def create_data(self,
                    file_path: Text,
                    with_data: List = None,
                    chained: Dict = None,
                    alias_chain: Dict = None,
                    appends: Dict = None,
                    cli_path: Text = None,
                    prefix: Text = None,
                    remove_old: bool = True
                    ):
        """ generate data and save to the file """
        table_data = DataGenerator(
            schema=self.schema, with_data=with_data, settings=self.settings, chained=chained,
            table_id=self.table_id, alias_chain=alias_chain, appends=appends,
            cli_path=cli_path, prefix=prefix).get_data_frame()

        if table_data is None:
            raise Exception("Data Generator failed")
        else:
            target_file_path = self._prepare_path(file_path, remove_old)
            writer = get_writer(self.settings['output']['file_format'])
            writer(table_data, target_file_path, self.settings['output']['config'])

    @staticmethod
    def _prepare_path(file_path, remove_old):
        """ prepare folder and check target file """
        if os.path.isfile(file_path):
            print("Founded old file {}".format(file_path))
            if remove_old:
                os.remove(file_path)
                print("File {} was removed".format(file_path))
            else:
                raise Exception("Impossible to generate data into file {}. "
                                "File already exist. Please delete file or set "
                                "'remove_old'=True".format(file_path))
        else:
            if not os.path.isdir(os.path.abspath(os.path.dirname(file_path))):
                os.makedirs(os.path.dirname(file_path))
        return file_path


class MultiTableRunner(object):

    def __init__(self, tables: List, settings: Dict, prefix="."):
        """

        :param tables:
        :type tables: list
        :param settings:
        :type settings: dict
        :param prefix:
        :type prefix: str
        """
        self.tables = tables
        self.prefix = prefix
        self.settings = settings

    def _validate_path(self, path: Text):
        """ check schema path exists, try to get correct path """
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            os.chdir(self.prefix)
            target_path = os.path.abspath(path)
        else:
            target_path = path
        if not os.path.isfile(target_path):
            raise ValueError("File with schema does not exist {}".format(path))
        return target_path

    def get_fields_and_schemas(self, dump_schema: bool = False):
        """ return list of schemas and tables fields """
        schemas = {}
        fields = []

        for dataset_id, table_id, schema in self.get_values_from_tables_list():
            if isinstance(schema, str):
                # validate path
                schema_path = self._validate_path(schema)
                # get schema object
                schema = SchemaExtractor(schema_path=schema_path,
                                         folder=dataset_id,
                                         table_id=table_id,
                                         dump_schema=dump_schema).get_schema()

            tg = TableRunner(table_id, dataset_id=dataset_id, settings=self.settings,
                             schema=schema, dump_schema=dump_schema)
            schemas[table_id] = (tg.schema, tg)

        for table_id in schemas:
            fields.append((table_id, [item['name'] for item in schemas[table_id][0]]))
        return schemas, fields

    def get_values_from_tables_list(self):
        """ this method try to understand that we have in table definition tuple """
        for table_definition in self.tables:
            if len(table_definition) == 3:
                dataset_id, table_id, schema = table_definition
            elif len(table_definition) == 2:
                dataset_id = None
                table_id, schema = table_definition
            elif len(table_definition) == 1:
                dataset_id, table_id = None, 'undefined'
                schema = table_definition[0]
            else:
                raise Exception(f'Invalid table definition in table list, it must contains max 3 values. '
                                f'You provided: {table_definition}')
            yield dataset_id, table_id, schema
