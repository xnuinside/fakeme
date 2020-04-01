from fakeme import Fakeme
from fakeme.fields import FieldRules

# STEP 1: Define schemas
schema_one_parts_list = [{
  "type": "STRING",
  "name": "part_identification",
  "mode": "NULLABLE"
 },
 {
  "type": "STRING",
  "name": "ship_type",
  "mode": "NULLABLE"
 },
 {
  "type": "STRING",
  "name": "price",
  "mode": "NULLABLE"
 }
]


# STEP 2: Add rules for field generation if you want, if not - will be used default generation rules
FieldRules.user_rules.append(
    {"field": "count", "generator": "str(randint(100, 6000))", "len": ""})

# "generator" must contains code, that can be executed in Generator module with "eval" command
# to see that methods are exist in Generator that you can use - you can simple just check fakeme.generator module

# define more rule
ship_type = {"field": "ship_type", "generator": "'Ship ' + text.word()",  "len": ""}
FieldRules.user_rules.append(ship_type)

# create list of tables, each tuple - one table, values in indexes:
# 1st - dataset/database name
# 2nd - table name
# 3rd - table's schema

list_of_tables = [
    ('robot_factory', 'parts', schema_one_parts_list),
    ('robot_factory', 'warehouse', 'warehouse_schema.json')  # second schema we will read from the file
]

# STEP 3: define dependencies and generation rules
Fakeme(tables=list_of_tables,
       dump_schema=True,
       settings={'row_numbers': 15},  # how much rows we want to generate
       # rls stands for  relationship - defining relationship between tables,
       # that field depend on that
       rls={'warehouse': {'part_id': {'alias': 'part_identification',
                                      'matches': 1,
                                      'table': 'parts'}}
            }).run()

# now just run `python space_ship_warehouse_tables.py`

# as result you will see 2 json files, that contains same data
# in part_identification (in parts.json) and part_id (in warehouse.json) fields
