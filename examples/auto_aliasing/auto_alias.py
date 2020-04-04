from fakeme import Fakeme

# in Fakeme exists feature 'auto_alias' that will alias columns between tables based on logic
# $column_name_in_singular_form_$field_name
# for example, you have cities and countries
# (like in example: examples/generate_data_related_to_existed_files)


# define 3 tables

users = [{'name': 'id'},
         {'name': 'name'},
         {'name': 'last_name'},
         {'name': 'group_id'}]  # let's imagine, that we have different users groups,
# Fakeme will check tables names and if one of them will be mapped to 1rst part
# of column name and second part after '_' to column name in this table - with
# data will be chained together and used like all ids from groups must be in users

groups = [{'name': 'id'},
          {'name': 'title'},
          {'name': 'rights', 'type': 'list', 'alias': 'right_id'},  # mean field rights contains list of right_ids
          {'name': 'description'}]

rights = [{'name': 'id'},
          {'name': 'title'},
          {'name': 'description'}]

Fakeme(tables=[('users', users),
               ('groups', groups),
               ('rights', rights)],
       settings={'auto_alias': True,
                 'tables': {
                     'rights': {
                         'row_numbers': 50,
                     },
                     'groups': {
                         'row_numbers': 10,
                     }
                 }}  # set auto alias to True
       ).run()

# after run you will see 3 tables that contains values of each users contains ids from groups table in field group_id
# and in groups  each group contains list of ids from rights table in rights field
