""" main module that contains RunGenerator class that used to init data generation """

from collections import defaultdict

from fakeme.config import Config
from fakeme.tables import MultiTableRunner
from fakeme.fields import FieldRulesExtractor

from datetime import datetime

target_paths = []
created = []
break_point = None


class Fakeme:

    def __init__(self,
                 tables,
                 params=None,
                 dump_schema=True,
                 rls=None,
                 path_prefix=".",
                 appends=None,
                 cli_path=None):
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
        :param params:
        :type params: dict
        :param dump_schema:
        :type dump_schema:
        :param rls:
        :type rls:
        """
        print("Fake me starts at", datetime.now())

        self.tables = tables
        self.cfg = Config(params).get_config()
        self.rls = self.resolve_aliases_tuples(rls) if rls else None or {}
        self.dump_schema = dump_schema
        self.path_prefix = path_prefix
        self.appends = appends or []
        self.cli_path = cli_path

    def resolve_aliases_tuples(self, rls: dict):
        """
            resolve fields aliases (situation when one table depend on second)
            or need to contain same value as in second table

            rls example:

                {'warehouse': {'part_id': {'alias': 'part_name',
                                                'matches': 1,
                                                'table': 'parts'}}}
        """

        for table in rls:
            new_dict = {}
            to_delete = []
            for key in rls[table]:
                if isinstance(key, tuple):
                    if isinstance(rls[table][key]["alias"], tuple):
                        for num, item in enumerate(key):
                            if len(rls[table][key]["alias"]) > num:
                                alias = rls[table][key]["alias"][num]
                            else:
                                alias = item
                            new_dict.update({item: {
                                "alias": alias,
                                "table": rls[table][key]["table"],
                                "matches": rls[table][key].get("matches")
                                            or self.cfg['matches']}})
                    to_delete.append(key)
            rls[table].update(new_dict)
            for item in to_delete:
                del rls[table][item]
        return rls

    def run(self):
        """
            call method to run data generation

            priority 0 - tables what target for chains
            priority 1 - tables what target for chains and in chains
            priority 2 - tables what not in self.append
            priority 3 - tables in self.append

        """

        print("Run Generation with settings: {}".format(self.cfg))
        # get all fields and schemas for tables
        self.schemas, fields = MultiTableRunner(
            self.tables, prefix=self.path_prefix, settings=self.cfg).\
            get_fields_and_schemas(dump_schema=self.dump_schema)

        priority_dict = self.create_priority_table_dict()
        field_extractor = FieldRulesExtractor(fields)

        # generate "value_rules.json" with rules for fields
        field_extractor.generate_rules()

        self.linked_fields = field_extractor.get_chains(self.schemas, self.rls)

        for level in priority_dict:
            for table in priority_dict[level]:
                if table not in created and table not in priority_dict.get(level+1, []):
                    self.create_table(table)
        if self.cfg['output'].get('line_start'):
            for target_file_path in target_paths:
                self._add_symbol_at_line_start(target_file_path)

        print("Data Generation ended successful \n", datetime.now())

    def _add_symbol_at_line_start(self, target_file_path):
        file_buf = []
        with open(target_file_path, "r") as csv_file:
            for num, line in enumerate(csv_file.readlines()):
                if num == 0:
                    if self.cfg["header"].get("no_quotes"):
                        line = line.replace('\"', "")
                    if self.cfg["header"].get("case"):
                        line = eval("line.{}()".format(self.cfg['header'].get(
                            "case")))
                file_buf.append(self.cfg['line_start'] + line)
        with open(target_file_path, "w+") as csv_file:
            csv_file.writelines(file_buf)

    def create_table(self, table):
        """ run table creation """
        target_path = "{}.{}".format(table, self.cfg['output']['file_format'])
        self.schemas[table][1].create_data(
            file_path=target_path, chained=self.linked_fields,
            alias_chain=self.rls, appends=self.appends,
            cli_path=self.cli_path)
        target_paths.append(target_path)
        created.append(table)

    def create_priority_table_dict(self):
        priority_dict = defaultdict(set)
        # 3
        [priority_dict[3].add(k) for k in self.appends]

        chains_tables = set([k for k in self.rls if k != "all"])

        priority_dict[0] = set([x[1] for x in self.tables if x[1] not in chains_tables])

        link_dict = {}
        tables_list = [x[1] for x in self.tables]
        for table in chains_tables:
            self_table = self.rls[table]
            for field in self_table:
                field_dict = self_table[field]
                if field_dict['table'] in tables_list:
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