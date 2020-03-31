import unittest
from fakeme.config import Config


class TestConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config(settings={"timezone": "US/Eastern"})

    def test_get_config(self):
        self.assertEqual(self.config.get_config().get('timezone'), "US/Eastern")
        self.assertEqual(self.config.get_config({'lala': 'land'}).get('lala'), "land")

    def test_class_variables(self):
        self.assertIsNotNone(getattr(Config, 'default_settings', None))


if __name__ == "__main__":
    unittest.main()
