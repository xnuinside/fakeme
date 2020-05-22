from fakeme import Fakeme

accounts_schema = [
                {"name": "title"},
                {"name": "balance", 'type': 'INTEGER'},
                {"name": "user_id"},
                {"name": "id", 'type': 'INTEGER'}]

transactions_schema = [{"name": "title"},
                       {"name": "account_id"},
                       {"name": "amount"},
                       {"name": "account_balance", 'type': 'INTEGER'},
                       {"name": "id", 'type': 'INTEGER'}]

tables_list = [('accounts', accounts_schema),
               ('transactions', transactions_schema)]

field_rules = [{"field": "id", "generator": "str(getrandbits(42))", "len": ""}]

relations = {'accounts': {'user_id': {'table': 'users.csv', 'alias': 'id', 'matches': 1}},
             'transactions': {'account_id': {'table': 'accounts', 'alias': 'id', 'matches': 1}}}

Fakeme(
    tables=tables_list,
    with_data=['users.csv'],  # this mean we need load users table as dataset from user.csv
    rls=relations,
    settings={'row_numbers': 100,
              "output": {"file_format": "csv",
                         "config": {}}
              }, field_rules=field_rules).run()
