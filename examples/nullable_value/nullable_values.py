from fakeme import Fakeme

# let's generate some data that can contain nullable values - so, for example, we need to test data pipeline, that
# filter and replace null values with smth, so in test data we must have Nulls in some rows

events = [
    {"name": "id"},
    {"name": "date"},
    {"name": "timestamp"},
    {"name": "server_name"},
    {"name": "ip"},
    {"name": "status", "mode": "nullable"},  # this mean, that in some rows must be nulls in this columns
    {"name": "details", "mode": "nullable"}
]

Fakeme(
    tables=[('events', events)],
    settings={'percent_of_nulls': 0.12}
).run()
# check result, you will see in columns status and details nulls values, by default percent_of_nulls = 0.05 (5%),
# but in out case we set it to 0.12 that mean 12%
