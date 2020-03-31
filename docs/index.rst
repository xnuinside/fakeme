.. Fakeme documentation master file, created by
   sphinx-quickstart on Sun Mar 29 01:14:15 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Fakeme's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   start
   tutorial
   examples
   schemas
   rules
   output
   columns
   customisation
   generators
   cli


Fakeme Data Generator for Chained and Relative Data

Use under the hood at current time:

     - Mimesis (like one of the generators for fields values)
     - Pandas (like main instrument to combain data in tables (frames)
     - Standart Python Library

Basic terminology
-----------------

**Dataset** - taken as parallel to BigQueries Datasets, so it something relative to schema in DB - group of tables.
It's not important right now, but you can group tables this way.

**Table_id** - similar to **table name** main identificator fr your table ('dataframe' in process of data generation).
This name needed to define aliases, links between tables, define aggregations - if they exists and etc.
This 'id' or 'name' will be used as file name for output result.

**Column** -

**Field** -

**Schema** -

**Rule** -

**Generator** -

**Output** -


**Dataset** can contains multiply *Tables*

**Tables** defined by *Schema* - description for the *Columns* (that *Fields* we want to have in table,
with what values and what type of *Values*)



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
