### Fakeme 

Data Generator for Chained and Relative Data

![badge1](https://img.shields.io/pypi/v/fakeme) ![badge2](https://img.shields.io/pypi/l/fakeme) ![badge3](https://img.shields.io/pypi/pyversions/fakeme) ![workflow](https://github.com/xnuinside/fakeme/actions/workflows/main.yml/badge.svg)

Documentation in process: https://fakeme.readthedocs.io/en/latest/ 

### How to use

```bash

    pip install fakeme

```

Check examples: https://github.com/xnuinside/fakeme/tree/master/examples

### What is Fakeme?

Fakeme is a tools that try to understand your data based on schemas & fields name and generate data relative to expected.

It create dependencies graph and generate relative data.

**Fakeme** oriented on generation data that depend on values in another tables/datasets.
Data, that knitted together as real.

**Fakeme** can help you if you want to generate several tables, that must contains in columns values, 
that you will use like key for join.

For example, *user_data* table has field *user_id* and *users* table contains list of users with column id. 
You want join it on user_id = id.

**Fakeme** will generate for you 2 tables with same values in those 2 columns. 

It does not matter to have columns with same name you can define dependencies between tables with alias names. 


## TODO in next releases:

1. Add integration with simple-ddl-parser to generated data from different SQL dialects
2. Add integration with py-models-parser to generated data from different Python models
3. Fix cases in todo folder
4. Improve test coverage 


### What you can to do

1. Define that fields in your datasets must contain similar values

2. You can set up how much values must intersect, for example, you want to emulate data for email validation pipeline -  you have one dataset with *incoming* messages  and you need to find all emails that was not added previously in your *contacts* table.

So you will have incoming messages table, that contains, for example only 70% of emails that exist in contacts table. 

3. You can use multiply columns as a key (dependency) in another column, for example, 
*player_final_report* must contains for each player same values as in other tables, for example, you have *player* table
with players details and *in_game_player_activity* with all player activities for some test reasons it's critical
to you generate *player_final_report* with 1-to-1 data from other 2 tables.
 
4. Union tables. You can generate tables that contains all rows from another tables. 

5. You can define your own generator for fields on Python.

6. You can define your own output format


### Examples


You can find usage examples in 'fakeme/examples/' folder.

Example from fakeme/examples/generate_data_related_to_existed_files:

```python

    from fakeme import Fakeme

    # to use some existed data you should provide with_data argument -
    # and put inside list with the paths to the file with data

    # data file must be in same format as .json or csv output of fakeme.
    # so it must be [{"column_name": value, "column_name2": value2 ..},
    #   {"column_name" : value, "column_name2": value2 ..}..]
    # Please check example in countries.json

    cities_schema = [{"name": "name"},
                     {"name": "country_id"},
                     {"name": "id"}]

    # all fields are strings - so I don't define type, because String will be used as default type for the column

    tables_list = [('cities', cities_schema)]

    Fakeme(
        tables=tables_list,
        with_data=['countries.json'],
        rls={'cities': {  # this mean: for table 'cities'
            'country_id': {  # and column 'country_id' in table 'cities'
                'table': 'countries.json',   # please take data from data  in countries.json
                'alias': 'id',  # with alias name 'id'
                'matches': 1  # and I want all values in country_id must be from countries.id column, all.
            }
        }},
        settings={'row_numbers': 1300}  # we want to have several cities for each country,
                                        # so we need to have more rows,
    ).run()

    # run and you will see a list of cities, that generated with same ids as in countries.json
```

Docs: https://fakeme.readthedocs.io/en/latest/


## Changelog
**v0.2.2**
### Fixes: 
1. generate_data_related_to_existed_files example now works well (generation data based on already existing files).
2. Added integration tests to run examples
3. Examples are cleaned up, unworking samples moved to 'todo'

**v0.2.1**
1. Now you can define tables as Table class object if it will be more easily for you.

```python
    from fakeme import Table

    Table(name='table_name_example', schema='path/to/schema.json')

    # or 
    user_schema = [{'name': 'id'},
            {'name': 'title'},
            {'name': 'rights', 'type': 'list', 'alias': 'right_id'},
            {'name': 'description'}]
    Table(name='table_name_example', schema=user_schema)
```
samples it tests: tests/unittests/test_core.py

2. Relationships between tables was corrected 


**v0.1.0**

1. Added code changes to support Python 3.8 and upper (relative to changes in python multiprocessing module)
2. Added tests runner on GitHub
3. Autoaliasing was fixed
4. Added some unit tests
