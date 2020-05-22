from fakeme import Fakeme
from fakeme.fields import FieldRules

users_schema = [{"name": "address"},
                {"name": "phone"},
                {"name": "family_name"},
                {"name": "name"},
                {"name": "email"},
                {"name": "password"},
                {"name": "user_id"}]
gifts = [{"name": "account_id"},
         {"name": "balance", 'type': 'INTEGER'},
                {"name": "user_id"},
                {"name": "rate"},
                {"name": "rate_3"}]
product_schema = [
                {"name": "title"},
                {"name": "balance", 'type': 'INTEGER'},
                {"name": "user_id"},
                {"name": "account_id", 'type': 'INTEGER'}]

product_account_schema = product_schema + [{"name": "interest_rate", 'type': 'FLOAT'}]

action_schema = [{"name": "title_actions"},
                 {"name": "account_id"},
                {"name": "amount"},
                {"name": "account_balance", 'type': 'INTEGER'},
                {"name": "id_int", 'type': 'INTEGER'}]

tables_list = [
               ('saving_accounts', product_account_schema),
               ('checking_accounts', product_account_schema),
               ('credit_cards', product_schema),
               ('credit_cards_actions', action_schema),
               ('saving_accounts_actions', action_schema),
               ('checking_accounts_actions', action_schema),
    ('gifts', gifts)]

FieldRules.user_rules.append(
    {"field": "account_id", "generator": "str(getrandbits(42))", "len": ""})

FieldRules.user_rules.append(
    {"field": "id_int", "generator": "str(getrandbits(42))", "len": ""})


Fakeme(
    tables=tables_list,
    with_data=['users.csv'],
    rls={
'gifts': {  # this mean: for table 'cities'
        'user_id': {  # and column 'country_id' in table 'cities'
            'table': 'users.csv',   # please take data from data  in countries.json
            'alias': 'id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }},
        'saving_accounts': {  # this mean: for table 'cities'
        'user_id': {  # and column 'country_id' in table 'cities'
            'table': 'users.csv',   # please take data from data  in countries.json
            'alias': 'id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }},
        'checking_accounts': {  # this mean: for table 'cities'
        'user_id': {  # and column 'country_id' in table 'cities'
            'table': 'users.csv',   # please take data from data  in countries.json
            'alias': 'id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }},
'credit_cards': {  # this mean: for table 'cities'
        'user_id': {  # and column 'country_id' in table 'cities'
            'table': 'users',   # please take data from data  in countries.json
            'alias': 'id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }
    },
'saving_accounts_actions': {  # this mean: for table 'cities'
        'account_id': {  # and column 'country_id' in table 'cities'
            'table': 'saving_accounts',   # please take data from data  in countries.json
            'alias': 'account_id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }
    },
'credit_cards_actions': {  # this mean: for table 'cities'
        'account_id': {  # and column 'country_id' in table 'cities'
            'table': 'credit_cards',   # please take data from data  in countries.json
            'alias': 'account_id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }
    },
'checking_accounts_actions': {  # this mean: for table 'cities'
        'account_id': {  # and column 'country_id' in table 'cities'
            'table': 'checking_accounts',   # please take data from data  in countries.json
            'alias': 'account_id',  # with alias name 'id'
            'matches': 1 # and I want all values in country_id must be from countries.id column, all.

        }
    }},
    settings={'row_numbers': 10,
              "output": {"file_format": "csv",
                         "config": {}},
              'tables': {  # let's define setting for tables
                  'checking_accounts_actions': {
                      'row_numbers': 100  # for table 'cities' please create only 1000 rows
                  },
                  'saving_accounts_actions': {
                      'row_numbers': 100  # for table 'cities' please create only 1000 rows
                  },
                  'credit_cards_actions': {
                      'row_numbers': 100  # for table 'cities' please create only 1000 rows
                  },

              }} # we want to have several cities for each country,
                                  # so we need to have more rows,
).run()
