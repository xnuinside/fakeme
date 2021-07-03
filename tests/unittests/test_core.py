import pytest

from fakeme.core import Config, Fakeme


def test_fakeme_one_required_arg():
    schema_users = [
        {"name": "id"},
        {"name": "name"},
        {"name": "last_name"},
        {"name": "group_id"},
    ]
    tables = [("users", schema_users)]
    # check no errors
    result = Fakeme(tables)
    assert result.cfg == Config(
        path_prefix="/Users/iuliia_volkova2/work/fakeme/tests/unittests",
        auto_alias=True,
    )


@pytest.fixture
def fakeme():
    schema_users = [
        {"name": "id"},
        {"name": "name"},
        {"name": "last_name"},
        {"name": "group_id"},
    ]
    group_schema = [{"name": "name"}, {"name": "id"}]
    tables = [("users", schema_users), ("groups", group_schema)]
    # check no errors
    return Fakeme(tables)


def test_fakeme_remove_plural_from_table_name(fakeme):

    assert fakeme.cfg == Config(
        path_prefix="/Users/iuliia_volkova2/work/fakeme/tests/unittests",
        auto_alias=True,
    )

    fakeme.run()

    assert fakeme._remove_plural_from_table_name("users") == "user"


def test_auto_alias_relationships(fakeme):
    fakeme.run()
    assert fakeme.rls["users"] == {
        "group_id": {"alias": "id", "table": "groups", "matches": 1}
    }
