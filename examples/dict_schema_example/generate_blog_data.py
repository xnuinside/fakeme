from fakeme import Fakeme

# define schema as json
posts_schema = {'title':
                {'len': 110},
                'description':
                {'len': 300},
                'body': {}
                }

Fakeme(tables=('posts', posts_schema)).run()
