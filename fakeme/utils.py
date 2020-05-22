from typing import Text, Union, Any
from logging import getLogger

log = getLogger('_FakeMe_')


def class_to_table_name(cls: Union[Text, Any]):
    """ any mean any class, cls can come as str or as Python class"""
    endings = {'y': lambda x: x[:-1] + "ies", 's': lambda x: x + 'es'}
    if isinstance(cls, str):
        base_name = cls.lower()
    else:
        base_name = cls.__name__.lower()
    table_name = endings.get(base_name[-1], lambda x: x + 's')(base_name)
    return table_name
