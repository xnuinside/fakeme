import unittest
from fakeme.fields import FieldRulesExtractor, FieldRules


class TestFieldRulesExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fre = FieldRulesExtractor(fields="")

    def test_rules_extracts(self):
        self.assertEqual(self.fre.rules_extracts(), [])

    def test_generate_rules(self):
        self.assertEqual(self.fre.generate_rules(), True)

    def test_get_chains(self):
        schemas = {}
        self.assertEqual(self.fre.get_chains(schemas), {})

    def test_extract_fields(self):
        fields = {'table': []}
        self.assertEqual(self.fre.extract_fields(fields), {'a'})

    def test_class_variables(self):

        behavior = {'_id': {"field": None,
                            "generator": "str(uuid1()).replace('-','').upper()",
                            "len": 12},
                    'default': {"field": None,
                                "generator": None,
                                "len": 6},
                    'last_upd_ts': {"field": None,
                                    "generator": "choice([current_time])",
                                    "len": ""},
                    '_ts': {"field": None,
                            "generator": "current_time",
                            "len": ""},
                    '_flg': {"field": None,
                             "generator": "choice({})".format(list(['Y', 'N'])),
                             "len": ""},
                    'addr_line': {"field": None,
                                  "generator": "fake.address()",
                                  "len": ""},
                    '_dt': {"field": None,
                            "generator": "datetime(2019, 2, 21).strftime('%Y-%m-%d')",
                            "len": ""},
                    }
        self.assertEqual(FieldRulesExtractor.file_name, 'rules.json')


if __name__ == "__main__":
    unittest.main()
