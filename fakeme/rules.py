# TODO: if included in field_name as part and multiple values by 's', 'es' at the end
#   like {'field': 'languages', 'generator': '[choice(languages), choice(languages)]'}

default_rules = {'id': {'generator': 'uuid4().hex', 'len': 12},
                 'default': {'generator': None, 'len': 6},
                 'price': {'generator': 'round(random(), 2)'},
                 'ts': {'generator': 'current_time'},
                 'flag': {'generator': 'choice([\'Y\', \'N\'])'},
                 'date': {'generator': 'date.date(2019, 2021)'},
                 'city': {'generator': 'address.city()'},
                 'country_code': {'generator': 'choice(countries.codes)'},
                 'country': {'generator': 'choice(countries.names)'},
                 'language': {'generator': 'choice(languages)'},
                 'title': {'generator': 'text.text()', 'len': 24},
                 'name': {'generator': 'person.name().split()[0]'},
                 'description': {'generator': 'text.text()'},
                 'email': {'generator': 'person.email()'}
                 }
