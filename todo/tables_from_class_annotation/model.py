from datetime import datetime


class Types:
    # online, offline, offline with online-translation
    id: str
    title: str


class Country:
    id: str
    name: str
    code: str


class City:
    id: str
    name: str
    country_id: Country


class Event:
    id: str
    title: str
    type: Types
    description: str
    city: str
    country: str
    date: datetime
