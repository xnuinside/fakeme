"""
    example how to generate data that based on existed data files

    for example, you already generated data in previous, or you want to use set of real products

    and generate relative to them fake orders, so you must have same 'ids' or same names as in existed dataset

    you want to create new dataset based on already existed

    so here we will show how to do this
"""
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
