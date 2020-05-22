import json
import os
from typing import Text, Optional, Dict, List, Union
from fakeme.utils import class_to_table_name
from fakeme import config
from pydantic import BaseModel, validator


supported_types = ['STRING', 'INTEGER', 'FLOAT', 'LIST']


types_map = {

    'str': 'string',
    'int': 'integer',
    'float': 'float',
    'list': 'list',
    'dict': 'dict',
    'datetime': 'string'
}


class Column(BaseModel):
    name: str
    type: str = str
    len: Optional[int] = None
    mode: Optional[int] = None

    @staticmethod
    @validator('mode')
    def check_value_above_zero(value):
        return value.lower()

    # todo: add type validation
    """
    
    def schema_validation(self, schema):
        for item in schema:
            _type = item.type
            self.type_validation(_type)
        return schema

    @staticmethod
    def type_validation(type_name):
        if type_name.upper() not in supported_types:
            raise ValueError

    """

class SchemaExtractor(object):

    def __init__(self,
                 schema: Text = None,
                 dataset: Text = None,
                 table_id: Text = "",
                 dump_schema: bool = True):
        self.schema = self.get_schema(schema)
        self.dataset = dataset or self.extract_folder()
        self.table_id = table_id
        self.dump_schema = dump_schema
        self.rls_founded = {}

    @staticmethod
    def _validate_path(path: Text):
        """ check schema path exists, try to get correct path """
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            os.chdir(config.cfg['path_prefix'])
            target_path = os.path.abspath(path)
        else:
            target_path = path
        if not os.path.isfile(target_path):
            raise ValueError("File with schema does not exist {}".format(path))
        return target_path

    def get_schema_from_file(self, schema_path: Text):
        # validate path
        if isinstance(schema_path, str):
            schema_path = self._validate_path(schema_path)
            if self.schema.endswith('.json'):
                with open(schema_path, 'r') as schema_file:
                    schema = json.load(schema_file)
            else:
                raise NotImplementedError('Supports only `.json` format')
        return schema

    def get_schema(self, schema: Union[Dict, List, Text]):
        if isinstance(schema, str):
            schema = self.get_schema_from_file(schema)
        else:
            schema = self.get_schema_from_python_obj(schema)
        return schema

    def extract_folder(self):
        if '/' in self.schema:
            splited = self.schema.split('/')
            folder, _ = splited[(len(splited) - 2):]
            if folder == 'schemas':
                folder = ''
        else:
            folder = '.'
        return folder

    def get_schema_from_python_obj(self, schema: Union[Dict, List]):
        """ get schema in BQ format """
        # we have a dict from class annotations
        print(schema)
        print('schema')
        print(type(schema))
        if isinstance(schema, dict):
            print('?')
            schema_fields = []
            for key in schema:
                print(key)
                print(key)
                if isinstance(schema[key], str):
                    # mean we have type definition
                    _type = schema[key]
                    if _type and _type.__module__ == self.dataset:
                        # mean class defined in same module
                        # need to set dependency
                        print(_type)
                        if not self.rls_founded.get(self.table_id):
                            self.rls_founded[self.table_id] = {}
                        self.rls_founded[self.table_id][class_to_table_name(key)] = {
                                'alias': 'id',
                                'table':  class_to_table_name(_type)
                            }

                        _type = None
                    else:
                        _type = self.map_type(_type)
                    field = Column(**{'name': key, 'type': _type})
                else:
                    print('Hi!')
                    print(schema[key])
                    if not schema[key].get('name'):
                        schema[key]['name'] = key
                    field = Column(**schema[key])
                schema_fields.append(field)
                print(schema_fields)
            schema = schema_fields
        elif isinstance(schema, list):
            print('Hiiii')
            return schema
        print('Hiiiir')
        print(schema)
        return schema

    def map_type(self, _type):
        """ method to map input types to the types that understandable by generator"""
        # in any unknown situation - use string :D
        mapped_type = 'string'
        if isinstance(_type, type):
            name = _type.__name__
            mapped_type = types_map[name]
        return mapped_type
