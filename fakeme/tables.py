""" classes to work with tables """

import os
from typing import Dict, List, Text

from fakeme import config
from fakeme.generator import DataGenerator
from fakeme.output import get_writer
from fakeme.schema import SchemaExtractor
from fakeme.utils import log


class TableRunner:
    """
    `schema_in_obj` arg example:

        [
            {"type": "STRING", "name": "name", "mode": "NULLABLE"},
            {"type": "STRING", "name": "id", "mode": "NULLABLE"}
        ]

    """

    def __init__(self, table_id: Text, schema: List, dataset_id: Text = None):
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.schema = schema

    def create_data(
        self,
        file_path: Text,
        with_data: List = None,
        chained: Dict = None,
        alias_chain: Dict = None,
        appends: Dict = None,
        cli_path: Text = None,
        prefix: Text = None,
        remove_old: bool = True,
    ):
        """generate data and save to the file"""

        cfg = config.cfg

        table_data = DataGenerator(
            schema=self.schema,
            with_data=with_data,
            chained=chained,
            table_id=self.table_id,
            alias_chain=alias_chain,
            appends=appends,
            cli_path=cli_path,
            prefix=prefix,
        ).get_data_frame()

        if table_data is None:
            raise Exception("Data Generator failed")
        else:
            target_file_path = self._prepare_path(file_path, remove_old)
            writer = get_writer(cfg.output.file_format)
            writer(table_data, target_file_path, cfg.output.config)

    @staticmethod
    def _prepare_path(file_path, remove_old):
        """prepare folder and check target file"""
        if os.path.isfile(file_path):
            log.info("Founded old file {}".format(file_path))
            if remove_old:
                os.remove(file_path)
                log.info("File {} was removed".format(file_path))
            else:
                raise Exception(
                    "Impossible to generate data into file {}. "
                    "File already exist. Please delete file or set "
                    "'remove_old'=True".format(file_path)
                )
        else:
            if not os.path.isdir(os.path.abspath(os.path.dirname(file_path))):
                os.makedirs(os.path.dirname(file_path))
        return file_path


class MultiTableRunner(object):
    def __init__(self, tables: List, rls: Dict):
        """

        :param tables:
        :type tables: list
        :param settings:
        :type settings: dict
        :param prefix:
        :type prefix: str
        """
        self.tables = tables
        self.rls = rls

    def get_fields_and_schemas(self, dump_schema: bool = False):
        """return list of schemas and tables fields"""
        schemas = {}
        fields = []
        for dataset_id, table_id, schema in self.get_values_from_tables_list():
            se = SchemaExtractor(
                schema=schema,
                dataset=dataset_id,
                table_id=table_id,
                dump_schema=dump_schema,
            )
            schema = se.schema

            if se.rls_founded:
                self.rls.update(se.rls_founded)

            tg = TableRunner(table_id, dataset_id=dataset_id, schema=schema)
            schemas[table_id] = (tg.schema, tg)

        for table_id in schemas:
            fields.append((table_id, [column.name for column in schemas[table_id][0]]))
        return schemas, fields

    def get_values_from_tables_list(self):
        """this method try to understand that we have in table definition tuple"""

        for table_definition in self.tables:

            if isinstance(table_definition, tuple) or isinstance(
                table_definition, list
            ):
                # we have tuple with table definition
                if len(table_definition) == 3:
                    dataset_id, table_id, schema = table_definition
                elif len(table_definition) == 2:
                    dataset_id = None
                    table_id, schema = table_definition
                elif len(table_definition) == 1:
                    dataset_id, table_id = None, "undefined"
                    schema = table_definition[0]
                else:
                    raise Exception(
                        f"Invalid table definition in table list, it must contains max 3 values. "
                        f"You provided: {table_definition}"
                    )
            else:
                # we have class definition
                if not getattr(table_definition, "__dict__", None):
                    raise Exception(
                        "Table Definition must be the tuple with table properties or class"
                    )
                else:
                    dataset_id = table_definition.__module__
                    table_id = table_definition.__name__.lower()
                    schema = table_definition.__annotations__
            yield dataset_id, table_id, schema
