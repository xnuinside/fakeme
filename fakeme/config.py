""" module that contain config object with default settings """
from copy import deepcopy


class Config(object):

    default_settings = {
        "row_numbers": 100,
        "matches": 0.6,
        "timezone": "UTC",
        "output": {"file_format": "json",
                   "config": {}},
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
