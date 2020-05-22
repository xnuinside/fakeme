"""  half of imports are used in step of field generation, so this is why imports looks like unused """

import os
import string
import json
import random  # noqa F401
import math
import re  # noqa F401
from uuid import uuid1, uuid4  # noqa F401
from random import randint, random, choice, choices  # noqa F401

from mimesis import Generic, Datetime, Text, Address, Person

from random import getrandbits
# todo: need to add hook with preset data if
#  in rules.json exists generators based on data from 'data' folder
data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class DataObject:
    pass


languages = ['zh', 'ru', 'en', 'es', 'ar', 'fr']

fake = Generic()
text = Text()
person = Person()
date = Datetime()
address = Address()

current_time = None
last_time = None
countries = DataObject()


def countries_init():
    """
        method to read countries and load data for generator
    :return:
    """
    country_data_file = os.path.join(data_folder, 'countries.json')

    with open(country_data_file, 'r') as countries_file:
        countries_data = json.load(countries_file)
        setattr(countries, 'names', [x['name'] for x in countries_data])
        setattr(countries, 'codes', [x['code'] for x in countries_data])


countries_init()


def random_char(_len):
    return ''.join([choice(string.ascii_letters) for x in range(_len)]).upper()


def values_generator(rule=None, unique=False):
    """ values generator, that eval rules what was defined in 'generator' key  """

    value = None
    if rule and rule['generator']:
        value = eval(rule['generator'])
        if isinstance(rule.get('len', ''), float) and not math.isnan(rule['len']):
            rule['len'] = int(rule['len'])
        if isinstance(rule.get('len', ''), int):
            value = value[0:rule['len']]
        if unique:
            if isinstance(value, str):
                value = value + ' ' + text.word().capitalize()
            elif isinstance(value, int):
                value = value + randint(1000, 10000)
            elif isinstance(value, float):
                value = value + round(random(), 4)
    return value


def list_generator(dataset, min_number_of_elements, max_number_of_elements):
    output = []
    len_dataset = len(dataset)
    count_of_elemnts = randint(min_number_of_elements, max_number_of_elements)
    for i in range(count_of_elemnts):
        output.append(dataset[randint(0, len_dataset-1)])
    return output
