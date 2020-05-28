from fakeme import Fakeme
from fakeme.rules import default_rules

# define schema as JSON, you can also use BigQuery Schema format, or DDL that you use to create tables with SQL
posts_schema = {'title':
                {'len': 80},
                'description':
                {'len': 160},
                'body': {},
                'date': {},
                'category': {},
                'id': {}
                }
# we can define our custom rules how to generate data, if you need it
field_rules = [{'field': 'body', 'generator': default_rules['text']['generator']},
               {'field': 'category', 'generator': 'choice(["Python", "New Project", "Open Source", "Read List"])'}]

Fakeme(tables=('posts', posts_schema), field_rules=field_rules, settings={'row_numbers': 5}).run()
