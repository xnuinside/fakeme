Fakeme 
=======

Data Generator for Chained and Relative Data

|badge1| |badge2| |badge3|

.. |badge1| image:: https://img.shields.io/pypi/pyversions/fakeme 
.. |badge2| image:: https://img.shields.io/pypi/v/fakeme
.. |badge3| image:: https://travis-ci.com/xnuinside/fakeme.svg?branch=master

Documentation in process: https://fakeme.readthedocs.io/en/latest/ 

Use under the hood at current time:

     - Mimesis (like one of the generators for fields values)
     - Pandas (like main instrument to combain data in tables (frames) 
     - Standart Python Library


Support Python 3.7

What it does not do?
=========================

This is not random value generated library - for this exist pretty cool lib Mimesis and another. 


What it does?
=========================

**Fakeme** oriented on generation data that depend on values in another tables/datasets.
Data, that knitted together as real. 

**Fakeme** can help you if you want to generate several tables, that must contains in columns values, 
that you will use like key for join.

For example, *user_data* table has field *user_id* and *users* table contains list of users with column id. 
You want join it on user_id = id.

**Fakeme** will generate for you 2 tables with same values in those 2 columns. 

It does not matter to have columns with same name you can define dependencies between tables with alias names. 
 
 
What you can to do
=========================

1. Define that fields in your datasets must contain similar values

2. You can set up how much values must intersect, for example, you want to emulate data for email validation pipeline - 
you have one dataset with *incoming* messages  and you need to find all emails that was not added previously in your *contacts* table.

So you will have incoming messages table, that contains, for example only 70% of emails that exist in contacts table. 

3. You can use multiply columns as a key (dependency) in another column, for example, 
*player_final_report* must contains for each player same values as in other tables, for example, you have *player* table
with players details and *in_game_player_activity* with all player activities for some test reasons it's critical
to you generate *player_final_report* with 1-to-1 data from other 2 tables.
 
4. Union tables. You can generate tables that contains all rows from another tables. 

5. You can define your own generator for fields on Python.

6. You can define your own output format


Examples
=========================

   You can find usage examples in 'examples/' folder.
        
Supported schema formats
=========================
    
    ...
 
Build and install from src
==========================
    
    ...
    

Usage
=========================
    
    ...
    
    
Customisation
=========================
    
    ...


Output formats
=========================

By default result output is JSON. 



From Command Line
=========================

Usage from command line:

     fakeme path_to/config.json

To use Generator from command line, you need to install it at first. 
To check what it installed correct, input command:

     fakeme
    
You must get such output: 

    usage: Fakeme Tables Data Generator [-h] config
    Fakeme Tables Data Generator: error: the following arguments are required: config

To use generator from command line, you need to define config.json 
(it must be json file, name of file does not matter). 

To get example, how to define config, check: 

        fakeme/examples/cli_usage/fakeme_config.json


JSON Config for Cli usage
=========================

You can put into config dict all args, what is RunGenerator class wait for:

    `tables_list, paths_with_scripts, settings, dump_schema, chains`

To get more information about types - look at RunGenerator class docstring.

Example: 

   ...

Field Rules
=========================

Field rule it's a dict, what contain:
 
 **field**  name for field 
 **generator**  it is a key, what contain python code or value; must be defined like a string look at section Generators to know more.
 **len** len of result value  
 
Exist list of pre-defined rules that will be usd by default if user did not any provide specific rules
and field name include one of standart rules key.

List of built_in_rules here:

    fakeme/rules.py
    
Generators
=========================

Generators it's a functions or values, or other python structures, 
that are used to generate value like this:

    value = eval(rule['generator'])

So it must be valid python code that will be 'evaled'. 


All generators for fields are defined in field rules in key 'generator', for example:

    {"field": "name", "generator": "person.name()", "len": "4"} 
    
It mean, what value for field will be result of person.name() splitted to have len == 4.


Relations
=========================

To define relations you need to use param 'rls' of  RunGenerator class or provide it in 
json config.

rls waits for dictionary, that contains as a keys of 1st level tables

For example:

    rls = {'warehouse': {'part_id': {'alias': 'part_identification',
                                                'matches': 1,
                                                'table': 'parts'}}
                                                }

Means, that field 'part_id' of table 'warehouse' depends on field 'part_identification' in table 'parts'. 
It means it must contain save values as in 'parts' table in column 'part_identification'.

Settings:
    
    "matches" - % of values in column that must intersect with aliased column in another table. 1 == 100, 0.8 = 80 and etc
   

Example: 
    
     fakeme/examples/space_ship_parts/space_ship_warehouse_tables.py


Settings
=========================

Default settings: 

    d default_settings = {
        "row_numbers": 100,
        "matches": 0.6,
        "timezone": "UTC",
        "output": {"file_format": "json","config": {}}}
    
Setting description: 

    "row_numbers" - count of how many rows need to generate for each table data
    
    "matches" - % of values in column that must intersect with aliased column in another table. 1 == 100, 0.8 = 80 and etc
    
    "timezone" - default timezone for datetime data
    
    "output" - settings of output data format 
    
    


Generators "from the Box"
=========================

...

    
Add custom fields generators
=============================

Find example in:

     fakeme/examples/space_ship_parts/space_ship_warehouse_tables.py

    
If you want to add your new field rule (how to generate it correct), 
you can do it from your python script runner:

    at the bottom of your script (before you call RunGenerator) add:
    
    from  fakeme.fields import FieldRules
    
    FieldRules.user_rules.append(
    {"field": "count", "generator": "str(randint(100, 6000))", "len": ""})


