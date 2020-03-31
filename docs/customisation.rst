User Customisation
==================


How to add custom fields generators
===================================


Find example in:

     fakeme/examples/space_ship_parts/space_ship_warehouse_tables.py


If you want to add your new field rule (how to generate it correct),
you can do it from your python script runner:

    at the bottom of your script (before you call RunGenerator) add:

    from  fakeme.fields import FieldRules

    FieldRules.user_rules.append(
    {"field": "count", "generator": "str(randint(100, 6000))", "len": ""})
