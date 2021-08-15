import pytest
from pydantic import ValidationError

from fakeme.utils import Table


def test_table_no_error():
    assert Table(name="table_name", schema="tests/unit/schemas/test_table_schema.json")


def test_table_path_validation_error():
    with pytest.raises(ValidationError):
        assert Table(name="table_name", schema="no_file_schema.json")


def test_table_object_schema():
    assert Table(name="table_name", schema=[{"name": "field1"}])
