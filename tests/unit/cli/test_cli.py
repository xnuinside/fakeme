import os
import sys
import unittest
from argparse import ArgumentParser

from fakeme.cli.cli import create_cli_parser, run_cli


class TestCliFunctions(unittest.TestCase):
    def test_create_cli_parser(self):
        self.assertTrue(isinstance(create_cli_parser(), ArgumentParser))

    def test_run_cli(self):
        cli_config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "test_data/datagenerate_config.json",
        )
        sys.argv = ["fakeme", cli_config_path]
        self.assertIsNone(run_cli())


if __name__ == "__main__":
    unittest.main()
