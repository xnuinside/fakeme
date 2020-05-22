from fakeme import Fakeme
from model import Event, Types, City, Country

# you can use classes with class annotations as tables schemas
# for the example we have classes, that defined in model.py (check them)

Fakeme(tables=[Event, Types, City, Country]).run()  # we need to generate all related tables,
# if the link one each to other

# run to generate data based on class
