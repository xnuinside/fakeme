import json
from typing import Text


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
