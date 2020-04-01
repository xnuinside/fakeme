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

   You can find usage examples in 'fakeme/examples/' folder.

    Minimal example:

.. code-block:: python


Docs: https://fakeme.readthedocs.io/en/latest/