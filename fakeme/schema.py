import json
import os
from typing import Dict, List, Optional, Text, Union

from pydantic import BaseModel, validator
from simple_ddl_parser import DDLParser

from fakeme import config
from fakeme.utils import class_to_table_name

supported_types = ["STRING", "INTEGER", "FLOAT", "LIST"]


types_map = {
    "str": "string",
    "int": "integer",
    "float": "float",
    "list": "list",
    "dict": "dict",
    "datetime": "string",
}


class Column(BaseModel):
    name: str
    type: str = "STRING"
    len: Optional[int] = None
    mode: Optional[str] = "NULLABLE"
    max_number: Optional[int] = None
    min_number: Optional[int] = None
    alias: Optional[str] = None

    @validator("name")
    def set_name_lower(cls, value):
        return value.lower()

    @validator("mode")
    def set_mode_lower(cls, value):
        return value.lower()

    @validator("type")
    def set_type_upper(cls, value):
        return value.upper()

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
    def __init__(
        self,
        schema: Text = None,
        dataset: Text = None,
        table_id: Text = "",
        dump_schema: bool = True,
    ):

        self.table_id = table_id
        self.dataset = dataset or self.extract_folder(schema)
        self.dump_schema = dump_schema
        self.rls_founded = {}
        self.schema = self.get_schema(schema)

    @staticmethod
    def _validate_path(path: Text):
        """check schema path exists, try to get correct path"""
        path = os.path.expanduser(path)
        if not os.path.isfile(path):
            os.chdir(config.cfg.path_prefix)
            target_path = os.path.abspath(path)
        else:
            target_path = path
        if not os.path.isfile(target_path):
            raise ValueError("File with schema does not exist {}".format(path))
        return target_path

    def get_schema_from_ddl(self, schema_path):
        """parse ddl and create JSON BigQuery schema"""
        ddl_parser = DDLParser(schema_path, table_id=self.table_id)
        if self.dump_schema:
            dump_path = "schemas/{}".format(self.dataset)
            schema = ddl_parser.run(dump=self.dump_schema, dump_path=dump_path)
        else:
            schema = ddl_parser.run()
        return schema

    def get_schema_from_file(self, schema_path: Text):
        if isinstance(schema_path, str):
            schema_path = self._validate_path(schema_path)
            if schema_path.endswith(".json"):
                with open(schema_path, "r") as schema_file:
                    schema = [Column(**column) for column in json.load(schema_file)]
            elif schema_path.endswith(".ddl"):
                schema = [
                    Column(**column) for column in self.get_schema_from_ddl(schema_path)
                ]
            else:
                raise NotImplementedError("Supports only `.json` format")
        return schema

    def get_schema(self, schema: Union[Dict, List, Text]):
        if isinstance(schema, str):
            schema = self.get_schema_from_file(schema)
        else:
            schema = self.get_schema_from_python_obj(schema)
        return schema

    @staticmethod
    def extract_folder(schema):
        if "/" in schema:
            splited = schema.split("/")
            folder, _ = splited[(len(splited) - 2) :]  # noqa E203
            if folder == "schemas":
                folder = ""
        else:
            folder = "."
        return folder

    def get_schema_from_python_obj(self, schema: Union[Dict, List]):
        """get schema in BQ format"""
        # we have a dict from class annotations
        if isinstance(schema, dict):
            schema_fields = []
            for key in schema:
                if isinstance(schema[key], str):
                    # mean we have type definition
                    _type = schema[key]
                    if _type and _type.__module__ == self.dataset:
                        # mean class defined in same module
                        # need to set dependency
                        if not self.rls_founded.get(self.table_id):
                            self.rls_founded[self.table_id] = {}
                        self.rls_founded[self.table_id][class_to_table_name(key)] = {
                            "alias": "id",
                            "table": class_to_table_name(_type),
                        }
                        _type = None
                    else:
                        _type = self.map_type(_type)
                    field_details = {"name": key, "type": _type}
                else:
                    if not schema[key].get("name"):
                        schema[key]["name"] = key
                    field_details = schema[key]
                field = Column(**field_details)
                schema_fields.append(field)
            schema = schema_fields
        elif isinstance(schema, list):
            schema = [Column(**field) for field in schema]
        if self.dump_schema:
            dump_path = "schemas/{}".format(self.dataset)
            export_schema = [
                column.dict(include={"name", "mode", "type"}) for column in schema
            ]
            self.dump_schema_to_file(export_schema, dump_path=dump_path)
        return schema

    def dump_schema_to_file(self, schema, dump_path):
        """method to dump json schema"""
        if not os.path.isdir(dump_path):
            os.makedirs(dump_path, exist_ok=True)
        with open(
            "{}/{}_schema.json".format(dump_path, self.table_id), "w+"
        ) as schema_file:
            json.dump(schema, schema_file, indent=1)

    @staticmethod
    def map_type(_type):
        """method to map input types to the types that understandable by generator"""
        # in any unknown situation - use string :D
        mapped_type = "string"
        if isinstance(_type, type):
            name = _type.__name__
            mapped_type = types_map[name]
        return mapped_type
