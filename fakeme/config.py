""" module that contain config object with default settings """
from copy import deepcopy


class Config(object):

    default_settings = {
        "row_numbers": 100,  # default number of rows in generated datasets
        "matches": 1,  # matches for values in columns that in relations with other tables
        "timezone": "UTC",  # default timezone for datetime data
        "output": {"file_format": "json",
                   "config": {}},  # output format configuration
        "auto_alias": False,  # use function of auto aliasing between tables or not
        "max_list_values": 4,  # maximum count elements for fields of type list
        "min_list_values": 0,  # minimum count elements for fields of type list
        "percent_of_nulls": 0.05  # if field is nullable - how much rows we need to fill with nulls
    }

    cfg = None

    def __init__(self, settings):
        """
        :param settings:
        """
        self.settings = self.get_config(settings)

    def get_config(self, settings=None):
        """ get current config as is if settings is None or update and return config """
        if self.cfg is None:
            self.cfg = deepcopy(self.default_settings)
        if settings:
            self.cfg.update(settings)
            self.cfg = self._validate_settings(self.cfg)
        return self.cfg

    @staticmethod
    def _validate_settings(config):
        """ validate params in config  """

        if config.get("rowNumbers", 0) < 0 or config.get("matches", 0) < 0:
            raise ValueError("rowNumbers (int) and matches (float) must be positive")

        return config
