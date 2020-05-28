import os.path
import json
from collections import defaultdict
from copy import copy
from pandas import DataFrame
from fakeme.rules import default_rules
from fakeme.utils import log


class FieldRulesExtractor(object):

    file_name = "rules.json"

    def __init__(self, fields, paths_list=None):
        if paths_list:
            paths_list = []
        self.fields = self.extract_fields(fields)
        self.paths_list = paths_list

    @staticmethod
    def extract_fields(fields):
        _fields = set([])
        fields_with_fixed_rules = [line['field'] for
                                   line in FieldRules.user_rules]
        for table in fields:
            [_fields.add(field) if field not in fields_with_fixed_rules
             else None for field in table[1]]
        return _fields

    def rules_extracts(self):
        field_rules = []
        fields_with_rules = []

        for rule in FieldRules.user_rules:
            # todo: all rules extract need to refactor
            if '*' in rule['field']:
                key = rule['field'].split('*')[1].lower()
                for field in self.fields:
                    if key in field.lower():
                        field_rule = copy(rule)
                        field_rule['field'] = field
                        fields_with_rules.append(field)
                        field_rules.append(field_rule)

            else:
                for field in self.fields:
                    if rule['field'].lower() == field.lower():
                        field_rule = rule
                        fields_with_rules.append(field)
                        field_rules.append(field_rule)

        for field in self.fields:
            if field not in fields_with_rules:
                for key in default_rules:
                    if key in field.lower():
                        field_rule = copy(default_rules[key])
                        break
                else:
                    field_rule = copy(default_rules['default'])
                field_rule['field'] = field
                field_rules.append(field_rule)
        return field_rules

    def generate_rules(self, remove_existed=True):
        if not remove_existed and os.path.isfile(self.file_name):
            log.info("{} with rules founded in {}".format(self.file_name, os.getcwd()))
        else:
            values_rules_dict = self.rules_extracts()
            with open(self.file_name, 'w+') as outfile:
                json.dump(values_rules_dict, outfile, indent=2)
            log.info("{} with rules for fields was created".format(self.file_name))
        return True

    @staticmethod
    def get_chains(schemas, chains=None):
        print(chains)
        if not chains:
            chains = {}
        chained = defaultdict(dict)
        table_field_added = {}
        for num, table in enumerate(schemas.items()):
            # get schema list except current
            table_name, table_schema = table
            table_fields = [field.name for field in table_schema[0]]
            for second_table_name, second_table_schema in list(schemas.items())[:num]:
                fields_was_found = [field.name for field in second_table_schema[0] if field.name in table_fields]
                if len(fields_was_found) > 0:
                    for field in fields_was_found:
                        if field not in table_field_added or (
                                field in table_field_added and table_field_added.get(field) != second_table_name):
                            # to avoid recursive link table1 - table2 with same fields
                            chained[table_name][field] = {
                                'table': second_table_name,
                                'alias': field
                            }
                            table_field_added[field] = table_name
        for table in chained:
            if chains.get(table):
                print('table')
                print(table)
                chained[table].update(chains[table])
        for table in chains:
            if table not in chained:
                chained[table] = chains[table]
        return chained


class FieldRules(object):

    user_rules = []

    def __init__(self):
        try:
            with open(FieldRulesExtractor.file_name, 'r') as json_file:
                list_with_field_rules = json.load(json_file)
        except IOError:
            list_with_field_rules = []

        dict_none_duplicates = {}

        for line in list_with_field_rules:
            dict_none_duplicates[line['field']] = line

        for line in FieldRules.user_rules:
            dict_none_duplicates[line['field']] = line

        final_rules_list = [dict_none_duplicates[line]
                            for line in dict_none_duplicates]
        self.rules = DataFrame.from_records(final_rules_list)
