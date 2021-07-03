from fakeme.core import Fakeme


def test_fakeme_one_required_arg():
    schema_users = [
        {"name": "id"},
        {"name": "name"},
        {"name": "last_name"},
        {"name": "group_id"},
    ]
    tables = [("users", schema_users)]
    # check no errors
    assert Fakeme(tables)
