""" module that contain config object with default settings """
from typing import Dict, Optional
from pydantic import BaseModel, validator


# current run config instance
cfg = None


class OutputFormat(BaseModel):
    file_format: str = "json"
    config: dict = {}


class ColumnConfig(BaseModel):
    unique_values: bool = False
    row_numbers: Optional[int] = 100
    matches: Optional[int] = 1
    percent_of_nulls: Optional[float] = 0.05


class TableConfig(BaseModel):
    row_numbers: Optional[int] = 100
    columns: Optional[Dict[str, ColumnConfig]] = {}
    percent_of_nulls: Optional[float] = 0.05
    matches: Optional[int] = 1


class Config(BaseModel):
    """ config model """
    row_numbers: int = 100
    matches: float = 1
    timezone: str = "UTC"
    path_prefix: str = "."
    auto_alias: bool = False
    max_list_values: int = 4
    min_list_values: int = 0
    percent_of_nulls: float = 0.05
    output: OutputFormat = OutputFormat(**{'file_format': "json", 'config': {}})
    tables: Optional[Dict[str, TableConfig]] = {}

    @staticmethod
    @validator('row_numbers', 'matches')
    def check_value_above_zero(value):
        if value < 0:
            raise ValueError(f"value must be positive (>0). You set {value}")
        return value
