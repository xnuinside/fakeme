from fakeme import Fakeme
from fakeme.rules import default_rules

# define schema as json
posts_schema = {'title':
                {'len': 80},
                'description':
                {'len': 160},
                'body': {}
                }

field_rules = [{'field': 'body', 'generator': default_rules['text']['generator']}]

Fakeme(tables=('posts', posts_schema), field_rules=field_rules).run()
