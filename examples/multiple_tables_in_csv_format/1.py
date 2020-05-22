from fakeme import Fakeme
from fakeme.fields import FieldRules

gifts = [{"name": "account_id"},
         {"name": "balance", 'type': 'INTEGER'},
                {"name": "user_id"},
                {"name": "rate"},
                {"name": "rate_3"}]
users_schema = [{"name": "address"},
                {"name": "phone"},
                {"name": "name"},
                {"name": "email"},
                {"name": "password"},
                {"name": "user_id"}]
tables_list = [
    ('gifts', gifts), ('users', users_schema)]

FieldRules.user_rules.append(
    {"field": "account_id", "generator": "str(getrandbits(42))", "len": ""})


FieldRules.user_rules.append(
    {"field": "id_int", "generator": "str(getrandbits(42))", "len": ""})


Fakeme(
    tables=tables_list,
    rls={
'gifts': {  # this mean: for table 'cities'
        'user_id': {  # and column 'country_id' in table 'cities'
            'table': 'users',   # please take data from data  in countries.json
            'alias': 'id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }}},
    settings={'row_numbers': 100,
              "output": {"file_format": "csv",
                         "config": {}},
              } # we want to have several cities for each country,
                                  # so we need to have more rows,
).run()
