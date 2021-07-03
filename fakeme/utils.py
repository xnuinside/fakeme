import os
from logging import getLogger
from typing import Any, List, Optional, Text, Union

from pydantic import BaseModel, Field, validator

log = getLogger("_FakeMe_")


def class_to_table_name(cls: Union[Text, Any]):
    """any mean any class, cls can come as str or as Python class"""
    endings = {"y": lambda x: x[:-1] + "ies", "s": lambda x: x + "es"}
    if isinstance(cls, str):
        base_name = cls.lower()
    else:
        base_name = cls.__name__.lower()
    table_name = endings.get(base_name[-1], lambda x: x + "s")(base_name)
    return table_name


class FakemeException(Exception):
    pass


class Table(BaseModel):
    # class-helper to define the Table
    name: str
    table_schema: Union[str, List] = Field(alias="schema")
    dataset: Optional[str]

    @validator("table_schema")
    def schema_validator(cls, v, values, **kwargs):
        if isinstance(v, str):
            if not os.path.isfile(v):
                raise ValueError(f"Schema file {v} does not exists or it is not a file")
        return v
