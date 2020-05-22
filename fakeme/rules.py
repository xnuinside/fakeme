# TODO: if included in field_name as part and multiple values by 's', 'es' at the end
#   like {'field': 'languages', 'generator': '[choice(languages), choice(languages)]'}

default_rules = {
                 'user_id': {'generator': 'choice(["stone", "crosher", "valensia", "sun56", "bigmommy"]).lower()'},
                 'id': {'generator': 'uuid4().hex', 'len': 12},
                 'family_name': {'generator': 'person.surname()'},
                 'balance': {'generator': 'randint(350, 5500)'},
                 'amount': {'generator': 'randint(5, 1200) * choice([-1, 1])'},
                 'address': {'generator': 'address.address()'},
                 'default': {'generator': 'uuid4().hex', 'len': 6},
                 'rate': {'generator': 'randint(1, 5)/10'},
                 'login': {'generator': 'text.word()'},
                 'nickname': {'generator': 'text.word()'},
                 'phone': {'generator': 'person.telephone()'},
                 'price': {'generator': 'round(random(), 2)'},
                 'ts': {'generator': 'current_time'},
                 'flag': {'generator': 'choice([\'Y\', \'N\'])'},
                 'date': {'generator': 'date.date(2019, 2021)'},
                 'city': {'generator': 'address.city()'},
                 'country_code': {'generator': 'choice(countries.codes)'},
                 'country': {'generator': 'choice(countries.names)'},
                 'language': {'generator': 'choice(languages)'},
                    'title_actions': {'generator': 'choice(["Monthly payment", '
                                                   '"Transfer between accounts", '
                                                   '"Account dividends"])'},
                 'title': {'generator': 'choice(["Shopping", "Vacation", '
                                        '"Study Expenses", '
                                        '"Mom\'s Expenses", "Grocery", '
                                        '"Christmas", "Presents"])', 'len': 20},
                 'surname': {'generator': 'person.surname()'},
                 'name': {'generator': 'person.name().split()[0]'},
                 'description': {'generator': 'text.text()'},
                 'email': {'generator': 'person.email()'}
                 }
