from collections import defaultdict
from typing import Dict, List, Set, Tuple


class Relationship:
    def process_first_priority(self):
        # relationships that was passed directly from Fakeme class + auto aliases
        self.tables_in_relations = set([k for k in self.rls])
        # first prior - tables that does not depend on other
        for table_name in self.schemas:
            if table_name not in self.tables_in_relations:
                self.priority_dict[0].add(table_name)
            print(self.priority_dict[0], "0")

    def create_tables_priority_graph(self):

        if self.cfg.auto_alias:
            self.resolve_auto_alises()

        self.priority_dict = defaultdict(set)
        # all tables that must be appended - to the end of priority
        [self.priority_dict[100].add(k) for k in self.appends]

        # tables that already in priority dict
        already_in_dicts = []
        already_in_dicts.extend(self.priority_dict[100])

        if self.rls:
            self.process_first_priority()
        else:
            self.priority_dict[0] = set(self.schemas.keys())

        if self.with_data:
            # if we generate based on some already existed data
            for data_file in self.with_data:
                self.priority_dict[0].add(data_file)

        already_in_dicts.extend(self.priority_dict[0])

        linked_pairs = self._process_chains_tables(
            self.tables_in_relations, already_in_dicts
        )
        n = 4
        while linked_pairs and n:
            self.priority_dict, linked_pairs = self._recombine_priority_by_links(
                self.priority_dict, linked_pairs
            )
            n -= 1
        self.normalize_priority()
        print(self.priority_dict)
        return self.priority_dict

    def normalize_priority(self):
        if self.priority_dict[100]:
            max_level = max(list(self.priority_dict.keys())[1:])
            self.priority_dict[max_level + 1] = self.priority_dict[100]
        del self.priority_dict[100]

    def _process_chains_tables(self, chains_tables: Set, already_in_dicts: List) -> Set:
        link_pairs = set()
        tables_list = [x for x in self.schemas if x not in already_in_dicts]
        for table in chains_tables:
            self_table = self.rls[table]
            for field in self_table:
                print(field)
                field_dict = self_table[field]
                if (
                    field_dict["table"] in tables_list
                    or field_dict["table"] in self.with_data
                ):
                    link_pairs.add((field_dict["table"], table))
        return link_pairs

    def _recombine_priority_by_links(
        self, priority_dict: Dict, linked_pairs: Set[Tuple]
    ) -> Tuple[Dict]:
        for n in range(len(priority_dict.keys()) + 1):
            pair_moved = set()
            for pair in linked_pairs:
                parent, child = pair
                if self.rls.get(parent, {}):
                    for _, value in self.rls[parent].items():
                        if value["table"] in priority_dict[n]:
                            priority_dict[n + 1].add(parent)
                            priority_dict[n + 2].add(child)
                            pair_moved.add(pair)
                else:
                    priority_dict[n].add(parent)
                    priority_dict[n + 1].add(child)
                    pair_moved.add(pair)

            for pair in pair_moved:
                linked_pairs.remove(pair)
        return priority_dict, linked_pairs

    def check_column_alias(self, column, table) -> None:
        # column - dict with column description
        alias_column_name = column.alias or column.name
        relative_table = self.table_prefix_in_column_name(alias_column_name)
        if relative_table:
            matches = self.cfg.matches

            if self.cfg.tables.get(table):
                column_settings = self.cfg.tables.get(table).columns.get(
                    column.name, {}
                )
                if column_settings:
                    matches = column_settings.matches
                else:
                    matches = self.cfg.tables.get(table).matches

            if table not in self.rls:
                self.rls[table] = {}

            self.rls[table].update(
                {
                    column.name: {
                        "alias": alias_column_name.split("_")[1],
                        "table": relative_table,
                        "matches": matches,
                    }
                }
            )

    def resolve_auto_alises(self):
        for table in self.schemas:
            for column in self.schemas[table][0]:
                self.check_column_alias(column, table)
