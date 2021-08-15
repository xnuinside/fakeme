import glob
import os
import sys
from typing import List

import pytest
from markers import LOCAL_ONLY

base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
examples_folder = os.path.join(base_path, "examples")


# add examples folder to PYTHONPATH
sys.path.insert(0, examples_folder)


def clean_up_folder_before_test(
    folder: str, exclude: List[str] = None, pattern: str = "*.json"
) -> str:
    if exclude is None:
        exclude = []
    folder = os.path.join(examples_folder, folder)
    path = os.path.join(folder, pattern)
    files = glob.glob(path, recursive=False)
    for file_ in files:
        if os.path.basename(file_) not in exclude:
            os.remove(file_)
    return folder


def check_files_in_folder(files: List[str]) -> None:
    for file_path in files:
        assert os.path.isfile(file_path)


def files_list(folder: str, names: List[str]) -> List[str]:

    files = []
    for name in names:
        files.append(os.path.join(folder, name))

    return files


@LOCAL_ONLY
def test_auto_alising():
    names = ["users.json", "groups.json", "rights.json"]
    files = files_list(clean_up_folder_before_test("auto_aliasing"), names)

    from auto_aliasing import auto_alias

    assert auto_alias
    check_files_in_folder(files)


@LOCAL_ONLY
def test_dict_schema_example():
    names = ["posts.json", "schemas/posts_schema.json"]
    files = files_list(clean_up_folder_before_test("dict_schema_example"), names)

    from dict_schema_example import generate_blog_data

    assert generate_blog_data
    check_files_in_folder(files)


@LOCAL_ONLY
def test_generate_data_related_to_existed_files():
    names = [
        "cities.json",
        "schemas/cities_schema.json",
        "schemas/cities_schema.json",
        "countries.json",
    ]
    files = files_list(
        clean_up_folder_before_test(
            "generate_data_related_to_existed_files", exclude=["countries.json"]
        ),
        names,
    )

    from generate_data_related_to_existed_files import cities_generator

    assert cities_generator
    check_files_in_folder(files)


@LOCAL_ONLY
def test_minimal_example():
    names = ["cats.json", "dogs.json"]
    files = files_list(clean_up_folder_before_test("minimal_example"), names)

    from minimal_example import minimal_example

    assert minimal_example
    check_files_in_folder(files)


@pytest.mark.skip("mystery issue with files")
def test_multiple_tables_in_csv_format():
    names = ["transactions.csv", "accounts.csv", "users.csv"]
    files = files_list(
        clean_up_folder_before_test(
            "multiple_tables_in_csv_format", pattern="*.csv", exclude=["users.csv"]
        ),
        names,
    )

    from multiple_tables_in_csv_format import generate_user_banking_data

    assert generate_user_banking_data.main()
    check_files_in_folder(files)


@LOCAL_ONLY
def test_nullable_value():
    names = ["events.json"]
    files = files_list(clean_up_folder_before_test("nullable_value"), names)

    from nullable_value import nullable_values

    assert nullable_values
    check_files_in_folder(files)


@pytest.mark.skip("mystery issue with files")
def test_space_ship_parts():
    names = ["parts.json", "warehouse.json"]
    files = files_list(
        clean_up_folder_before_test(
            "space_ship_parts", exclude=["warehouse_schema.json"]
        ),
        names,
    )

    from space_ship_parts import space_ship_warehouse_tables

    assert space_ship_warehouse_tables
    check_files_in_folder(files)


@pytest.mark.skip("fails")
def test_tables_from_class_annotation():
    names = ["parts.json", "warehouse.json"]
    folder = clean_up_folder_before_test("tables_from_class_annotation")
    files = files_list(folder, names)
    sys.path.insert(0, folder)
    import class_annotation

    assert class_annotation
    check_files_in_folder(files)


@pytest.mark.skip("fails")
def test_unique_values_per_column_and_rows_per_table():
    names = ["parts.json", "warehouse.json"]
    folder = clean_up_folder_before_test(
        "unique_values_per_column_and_rows_per_table", exclude=["countries.json"]
    )
    files = files_list(folder, names)
    from unique_values_per_column_and_rows_per_table import cities_generator

    assert cities_generator
    check_files_in_folder(files)
