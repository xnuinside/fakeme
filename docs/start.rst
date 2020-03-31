Quick Start
===========


.. highlight:: bash

    pip install fakeme


in TODO

Please check Examples section :ref:`Examples`

You can use Fakeme with 2 ways. More flexible is to use from python script with import


.. code-block:: python

    from fakeme import Fakeme

Fakeme - main class that you need to call to run data generation.

Minimal that you need to provide to Generator is a **tables_list** argument.

Fakeme(
    tables=[()]
)


*tables* param
You must provide a list of tuples: [()]. Each tuple define one table.
You must provide table_id and schema, also (optional) you can provide dataset_id.

If you provide only table_id and schema order does not matter: library check type of elements in tuple.
But if you provide tuple with 3 args: dataset_id, table_id and schema, table_id always must have index after dataset_id
this is correct:
    ('dataset_id', 'table_1', [{'name': 'id'}, {'name': 'value'}])

this is wrong ('dataset_id will be used as table name):
    ('table_1', 'dataset_id', [{'name': 'id'}, {'name': 'value'}])





