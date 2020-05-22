import os.path
import json
from copy import copy
from pandas import DataFrame
from fakeme.rules import default_rules
from fakeme.utils import log


class FieldRulesExtractor(object):

    file_name = "rules.json"

    def __init__(self, fields):

        self.fields = self.extract_fields(fields)

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
        for field in self.fields:
            for key in default_rules:
                if key in field.lower():
                    field_rule = copy(default_rules[key])
                    break
            else:
                field_rule = copy(default_rules['default'])
            field_rule['field'] = field
            field_rules.append(field_rule)
        [field_rules.append(x) for x in FieldRules.user_rules]
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

    def get_chains(self, schemas, chains=None):
        """ TODO: add validation for constr "list ON list.grec_cust_id_lsr=hh.grec_cust_id"
            need to add support to chains
        """
        chained = {}
        for table in schemas:
            last_tables = [table_fields for table_fields in schemas
                           if table_fields[0] != schemas[table][0]]
            for second_table in last_tables:
                found_fields = [field['name'] for field in second_table[0] if
                                field in schemas[table][0]]
                if len(found_fields) > 0:
                    for field in found_fields:
                        if chained.get(field):
                            [chained[field].add(
                                name) for name in [table[0], second_table[0]]]
                        else:
                            chained[field] = {table[0], second_table[0]}
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
