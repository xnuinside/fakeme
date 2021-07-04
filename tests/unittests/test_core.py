import os
from collections import defaultdict

import pytest

from fakeme import Table
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
        path_prefix=os.path.dirname(os.path.abspath(__file__)),
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
    fakeme.run()
    assert fakeme._remove_plural_from_table_name("users") == "user"


def test_auto_alias_relationships(fakeme):
    fakeme.run()
    assert fakeme.rls["users"] == {
        "group_id": {"alias": "id", "table": "groups", "matches": 1}
    }


def test_fakeme_define_table_as_obj():
    schema_users = [
        {"name": "id"},
        {"name": "name"},
        {"name": "last_name"},
        {"name": "group_id"},
    ]
    result = Fakeme(tables=[Table(schema=schema_users, name="users")])
    assert result.cfg == Config(
        path_prefix=os.path.dirname(os.path.abspath(__file__)),
        auto_alias=True,
    )


@pytest.fixture
def multiple_tables_fakeme():
    schema_users = [
        {"name": "id"},
        {"name": "name"},
        {"name": "last_name"},
        {"name": "group_id"},
    ]
    schema_groups = [
        {"name": "id"},
        {"name": "title"},
        {
            "name": "rights",
            "type": "list",
            "alias": "right_id",
        },  # mean field rights contains list of right_ids
        {"name": "description"},
    ]

    schema_rights = [
        {"name": "id"},
        {"name": "title"},
        {"name": "description"},
        {
            "name": "permissions",
            "type": "list",
            "alias": "permission_id",
        },
    ]
    schema_permissions = [{"name": "id"}, {"name": "title"}, {"name": "description"}]
    fakeme = Fakeme(
        tables=[
            Table(schema=schema_users, name="users"),
            Table(schema=schema_groups, name="groups"),
            Table(schema=schema_rights, name="rights"),
            Table(schema=schema_permissions, name="permissions"),
        ]
    )
    return fakeme


def test_relationships(multiple_tables_fakeme):
    fakeme = multiple_tables_fakeme
    fakeme.run()
    assert fakeme.rls == {
        "users": {"group_id": {"alias": "id", "table": "groups", "matches": 1}},
        "groups": {"rights": {"alias": "id", "matches": 1, "table": "rights"}},
        "rights": {
            "permissions": {"alias": "id", "matches": 1, "table": "permissions"}
        },
    }
    expected = defaultdict(set)
    expected.update({0: {"permissions"}, 1: {"rights"}, 2: {"groups"}, 3: {"users"}})
    assert fakeme.priority_dict == expected


@pytest.fixture
def multiple_tables_depend_fakeme():
    schema_users = [
        {"name": "id"},
        {"name": "name"},
        {"name": "last_name"},
        {"name": "group_id"},
        {"name": "address_id"},
    ]
    schema_addresses = [
        {"name": "id"},
        {"name": "street"},
        {"name": "country"},
        {"name": "house"},
    ]
    schema_groups = [
        {"name": "id"},
        {"name": "title"},
        {
            "name": "rights",
            "type": "list",
            "alias": "right_id",
        },  # mean field rights contains list of right_ids
        {"name": "description"},
    ]

    schema_rights = [
        {"name": "id"},
        {"name": "title"},
        {"name": "description"},
        {
            "name": "permissions",
            "type": "list",
            "alias": "permission_id",
        },
    ]
    schema_permissions = [{"name": "id"}, {"name": "title"}, {"name": "description"}]
    fakeme = Fakeme(
        tables=[
            Table(schema=schema_users, name="users"),
            Table(schema=schema_groups, name="groups"),
            Table(schema=schema_rights, name="rights"),
            Table(schema=schema_permissions, name="permissions"),
            Table(schema=schema_addresses, name="addresses"),
        ]
    )
    return fakeme


def test_relationships_depend_on_several_tables(multiple_tables_depend_fakeme):
    fakeme = multiple_tables_depend_fakeme
    fakeme.run()
    assert fakeme.rls == {
        "users": {
            "group_id": {"alias": "id", "table": "groups", "matches": 1},
            "address_id": {"alias": "id", "matches": 1, "table": "addresses"},
        },
        "groups": {"rights": {"alias": "id", "matches": 1, "table": "rights"}},
        "rights": {
            "permissions": {"alias": "id", "matches": 1, "table": "permissions"}
        },
    }

    expected = defaultdict(set)
    expected.update(
        {0: {"permissions", "addresses"}, 1: {"rights"}, 2: {"groups"}, 3: {"users"}}
    )
    assert fakeme.priority_dict == expected
