# TODO: if included in field_name as part and multiple values by 's', 'es' at the end
#   like {'field': 'languages', 'generator': '[choice(languages), choice(languages)]'}
from typing import List, Optional

from pydantic import BaseModel


class Rule(BaseModel):
    field: str
    generator: str
    len: Optional[int] = None


class RuleSet(BaseModel):
    name: str
    rules: List[Rule]


# todo: move rules to pydantic models & define sets


person_rules = [
    {
        "field": "user_id",
        "generator": 'choice(["stone", "crosher", "valensia", "sun56", "bigmommy"]).lower()',
    }
]


person_rules = RuleSet(name="person", rules=[Rule(**rule) for rule in person_rules])

default_rules = {
    "user_id": {"generator": "text.word().lower() + str(randint(10, 99))"},
    "id": {"generator": "uuid4().hex", "len": 12},
    "family_name": {"generator": "person.surname()"},
    "balance": {"generator": "randint(350, 5500)"},
    "amount": {"generator": "randint(5, 1200) * choice([-1, 1])"},
    "address": {"generator": "address.address()"},
    "default": {"generator": "uuid4().hex", "len": 6},
    "rate": {"generator": "randint(1, 5)/10"},
    "login": {"generator": "text.word()"},
    "text": {"generator": "text.text()"},
    "nickname": {"generator": "text.word()"},
    "phone": {"generator": "person.telephone()"},
    "price": {"generator": "round(random(), 2)"},
    "current_time": {"generator": "current_time()"},
    "ts": {"generator": "current_time()"},
    "flag": {"generator": "choice(['Y', 'N'])"},
    "datetime": {
        "generator": "datetime.datetime.now()"
    },  # todo: change to data random generator in range
    "date": {"generator": "date.date(2019, 2021)"},
    "city": {"generator": "address.city()"},
    "country_code": {"generator": "choice(countries.codes)"},
    "country": {"generator": "choice(countries.names)"},
    "language": {"generator": "choice(languages)"},
    "title": {"generator": "text.text()", "len": 20},
    "surname": {"generator": "person.surname()"},
    "name": {"generator": "person.name().split()[0]"},
    "description": {"generator": "text.text()"},
    "email": {"generator": "person.email()"},
}
