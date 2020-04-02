"""
   example duplicated from fakeme/examples/generate_data_related_to_existed_files

   descriptions for each step and configs you can find in '.py' upper

   now we want to have only unique values in city 'name' column

"""
from fakeme import Fakeme

config = {'row_numbers': 1300,  # this is global setting for all tables in our generated set,
          # but you can it overwrite for each table with personal count
          'tables': {  # let's define setting for tables
              'cities': {  # for table 'cities' use this config
                  'columns': {
                      'name': {  # for column 'name' of table 'cities' use this config
                          'unique': True  # Fakeme, please keep all values in column name unique,
                          # by default it is False
                      }},
                  'row_numbers': 1000  # for table 'cities' please create only 1000 rows
              },
          }
          }

cities_schema = [{"name": "name"},
                 {"name": "country_id"},
                 {"name": "id"}]

# let's define one more table to check that setting for 'cities' applies only on 'cities' table
users_schema = [{"name": "email"},
                {"name": "name"},
                {"name": "login"},
                {"name": "user"}]


tables_list = [('cities', cities_schema), ('users', users_schema)]

Fakeme(
    tables=tables_list,
    with_data=['countries.json'],
    rls={'cities': {
        'country_id': {
            'table': 'countries.json',
            'alias': 'id',
            'matches': 1
        }
    }},
    settings=config
).run()

# now run and check difference, you will see in users.json 1300 rows, in cities.json 1000 rows
# and you will see that in users can exist duplicates, but in cities names not
