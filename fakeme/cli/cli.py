""" module with command line to run test data generation
    from command line with json config"""
import os.path
import json
import argparse
import inspect
from fakeme.core import Fakeme


def create_cli_parser():
    """ generate command line cli """
    description = "Fakeme - Flexible, customizable data generator for related data"

    parser = argparse.ArgumentParser(description=description,
                                     prog="Fakeme Tables Data Generator")

    parser.add_argument('config',
                        help="path to config file with defined rules "
                             "to data generation, to get example, "
                             "please look at /fakeme/example/example_with_command_line")

    return parser


def run_cli():
    """ main method for fakeme cli """
    parser = create_cli_parser()
    args = parser.parse_args()
    config_path = os.path.expanduser(args.config)
    if not os.getcwd() in config_path:
        config_path = os.path.join(os.getcwd(), config_path)
    if not os.path.isfile(config_path):
        print("Config path {} does not exist. Please, provide "
              "valid path".format(args.config))
        exit(1)
    with open(config_path, 'r') as config:
        conf = json.load(config)
        validate_config(conf)
        Fakeme(cli_path=os.path.dirname(config_path), **conf).run()


def validate_config(conf):
    possible_config_params = inspect.signature(Fakeme.__init__).parameters
    for key, _ in conf.items():
        if key not in possible_config_params:
            print(f"Config contain incorrect values. "
                  f"You can provide only: {possible_config_params} params ")
            exit(1)
