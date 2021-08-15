import unittest

from fakeme.config import Config


class TestConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config(**{"timezone": "US/Eastern"})

    def test_get_config(self):
        self.assertEqual(self.config.timezone, "US/Eastern")


if __name__ == "__main__":
    unittest.main()
