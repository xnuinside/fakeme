""" minimal example that will generate 2 datasets based on schema
    this data will not have any relations because 'rls' parameter is not defined

    how to define relations between tables - check
        fakeme/examples/space_ship_parts/space_ship_warehouse_tables.py
"""
from fakeme import Fakeme

# if you provide tables as a tuple with 2 values, system decide,
# that first value is table name and second is a schema

# Order always must be dataset_id, table_id, schema. If you provide only table_id and schema.
# But if you provide tuple with 3 args: dataset_id, table_id and schema,
# table_id always must have index after dataset_id
# this is correct:
#   ('dataset_id', 'table_1', [{'name': 'id'}, {'name': 'value'}])
#
# this is wrong ('dataset_id will be used as table name):
#   ('table_1', 'dataset_id', [{'name': 'id'}, {'name': 'value'}])


Fakeme(tables=[
    ('dogs', [{'name': 'name'}, {'name': 'breed'}, {'name': 'id'}]),
    ('amazing_animals', 'cats', [{'name': 'Id'}, {'name': 'breed'}, {'name': 'Name'}])
]).run()

# schema: library use schema style of BigQuery, because it provide information about
# nullable/not nullable column and type.
# so usually schema looks like a list of dicts - one dict per column and inside each dict
# keys 'name', 'type' and 'mode' that contains information nullabe /required
