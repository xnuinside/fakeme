from fakeme import Fakeme

# if you use table schemas from ddl you can init multiply tables or just some of them
# for example:
# TODO:

Fakeme(tables=[
    ('sqlite_schema.ddl', ),  # we will take all tables schemas from sqlite
    ()
]).run()
