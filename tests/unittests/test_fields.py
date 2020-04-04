import unittest
from fakeme.fields import FieldRulesExtractor


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
        self.assertEqual(FieldRulesExtractor.file_name, 'rules.json')


if __name__ == "__main__":
    unittest.main()
