from fakeme import Fakeme

# define schema as json
posts_schema = {'title':
                {'max_len': 110},
                'description':
                {'max_len': 300},
                'body': {}
                }

Fakeme(tables=('posts', posts_schema)).run()
