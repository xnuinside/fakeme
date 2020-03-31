Supported Schemas for Tables
============================
Schema is needed for Fakeme to know that columns and of that data types must be generated.

As default, library use Schema style from BigQuery - https://cloud.google.com/bigquery/docs/schemas#creating_a_json_schema_file but without 'description' field.

Usually schema looks like a list of dicts - one dict per column and inside each dict:
- 'name': column name,
- 'type': data type of values in column,
- 'mode': contains information nullabe / required. This field is not sensitive to capitalization.


Example:

.. code-block:: json

    [{
      "type": "STRING",
      "name": "part_identification",
      "mode": "Required"
     },
     {
      "type": "FLOAT",
      "name": "ship_type",
      "mode": "NULLABLE"
     },
     {
      "type": "INTEGER",
      "name": "price",
      "mode": "NULLABLE"
     }]

If you don't provide a type, like this:

.. code-block:: json
    {
      "name": "some_field_that_we_have_no_ide_how_to_generate",
      "mode": "NULLABLE"
    }


And Fakeme does not have base rule for generating columns with such name - output will be random string.

But if we have generator for field. For example, with name "price":

.. code-block:: json

    {
      "name": "price",
      "mode": "NULLABLE"
    }

Result will be of float type based on existed Rule for Generating (check rules in fakeme/rules.py).


