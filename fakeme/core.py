""" main module that contains RunGenerator class that used to init data generation """
import inspect
import os
from datetime import datetime
from typing import Dict, List, Optional, Text, Tuple, Union

from fakeme import config
from fakeme.config import Config
from fakeme.fields import FieldRules, FieldRulesExtractor
from fakeme.logic.relationships import Relationship
from fakeme.tables import MultiTableRunner
from fakeme.utils import FakemeException, Table, log
from fakeme.walker import Walker

created = []


class Settings:
    def __init__(
        self,
        with_data: List = None,
        settings: Dict = None,
        dump_schema: bool = True,
        rls: Dict = None,
        appends: List = None,
        cli_path: Text = None,
        field_rules: Optional[List] = None,
        paths_with_scripts: Optional[List] = None,
        auto_alias: bool = True,
    ):
        """
        Base Settings class, that contains configuration for Fakeme runner

        """
        if not field_rules:
            field_rules = []

        FieldRules.user_rules = field_rules

        if not settings:
            settings = {}

        settings.update({"auto_alias": auto_alias})

        config.cfg = Config(**settings)

        self.paths_with_scripts = paths_with_scripts if paths_with_scripts else []

        self.cfg = config.cfg
        # os.path.dirname(inspect.stack()[2][1]) - path of the file where Fakeme was called
        self.cfg.path_prefix = cli_path or os.path.dirname(inspect.stack()[2][1])
        self.rls = rls if rls else None or {}
        self.dump_schema = dump_schema
        # todo: remove this things with paths
        if not cli_path and os.getcwd() not in self.cfg.path_prefix:
            self.cfg.path_prefix = os.path.join(os.getcwd(), self.cfg.path_prefix)
        self.appends = appends or []
        self.cli_path = cli_path
        self.with_data = self.validate_data_source(with_data)


class Fakeme(Settings, Relationship):
    def __init__(
        self,
        tables: Union[List, Tuple[str, Union[str, dict, list, Table]]],
        *args,
        **kwargs,
    ):
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
        super().__init__(*args, **kwargs)
        self.tables = self.normalize_tables(tables)

    @staticmethod
    def normalize_tables(tables: Union[Table, Tuple, List]) -> List[Table]:
        if (isinstance(tables, Tuple) or isinstance(tables, List)) and isinstance(
            tables[0], str
        ):
            # mean we have only one table definition
            tables = tuple(
                tables,
            )
            tables = [tables]
        elif isinstance(tables, List):
            for table in tables:
                if not isinstance(table, Table) and not isinstance(table[0], str):
                    raise FakemeException(
                        f"Tables definitions must be presented like a tuple ('table_name', schema). "
                        f"You provided: {table}"
                    )
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
                        raise Exception(
                            f'Could not find the path {path} from "with_data" parameter'
                        )
            validated_list.append(path)
        return set(validated_list)

    def run(self):

        log.info(f"Fakeme starts at {datetime.now()}")
        # get all fields and schemas for tables
        self.schemas, fields = MultiTableRunner(
            self.tables, rls=self.rls
        ).get_fields_and_schemas(dump_schema=self.dump_schema)

        walk_list = []

        for path in self.paths_with_scripts:
            walker = Walker(path_to_dir=path, extension="hql", recursive=True)
            [walk_list.append(path) for path in walker.walk()]

        field_extractor = FieldRulesExtractor(fields, walk_list)
        # generate "value_rules.json" with rules for fields
        field_extractor.generate_rules()

        self.priority_dict = self.create_tables_priority_graph()

        for key, value in self.priority_dict.items():
            for table in value:
                if (
                    table not in created
                    and table not in self.with_data
                    and table not in self.priority_dict.get(key + 1, [])
                ):
                    self.create_table(table)

        log.info(f"Fakeme finished data generation successful \n {datetime.now()}")

    def _remove_plural_from_table_name(self, table_name) -> List:
        if table_name.endswith("es"):
            table_name = table_name[:-3]
        elif table_name.endswith("s"):
            table_name = table_name[:-1]
        return table_name

    def table_prefix_in_column_name(self, column_name: Text) -> Union[Text, None]:
        """check do we have table name prefix in column name,
        to get possible auto aliasing"""
        table_names = list(self.schemas.keys())
        for table_name in table_names:
            if self._remove_plural_from_table_name(table_name) in column_name:
                log.info(f"Found alias with {table_name}")
                return table_name

    def create_table(self, table):
        """run table creation"""
        if self.cfg.output.file_name_style:
            file_name = eval(f"'{table}'.{self.cfg.output.file_name_style}()")
        else:
            file_name = table
        target_path = os.path.join(
            self.cfg.path_prefix, "{}.{}".format(file_name, self.cfg.output.file_format)
        )

        self.schemas[table][1].create_data(
            file_path=target_path,
            with_data=self.with_data,
            chained={},
            alias_chain=self.rls,
            appends=self.appends,
            prefix=self.cfg.path_prefix,
            cli_path=self.cli_path,
        )

        created.append(table)
