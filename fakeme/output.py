"""
    class to write DataFrame in output format,
    that you need, can be customised by using

    import fakeme.output
    fakeme.output.user_defined_writers['your_format_name'] = python_callable

"""
import json
from copy import deepcopy
from typing import Text, Dict, Callable
from pandas import ExcelWriter, DataFrame


default_format_setting = {
    'to_json': {
        'orient': 'records',
        'lines': False
    },
    'to_csv': {
        'header': True,
        'index': False,
        'line_terminator': '\n'
    }
}


def to_excel(df: DataFrame) -> Callable:
    to_method = getattr(df, 'to_excel')

    def excel_method(*args, **kwargs):
        path = kwargs['path']
        del kwargs['path']
        return to_method(ExcelWriter(path), *args, **kwargs)
    return excel_method


def output_writer(method_name: Text) -> Callable:
    def format_writer_with_defaults(df: DataFrame, path: Text, params: Dict = None):
        if not params:
            params = {}
        combined_params = deepcopy(default_format_setting[method_name])
        combined_params.update(params)
        return getattr(df, method_name)(path, **combined_params)
    return format_writer_with_defaults


def json_with_indent() -> Callable:
    def json_with_indent_inner(df: DataFrame, path: Text, params: Dict = None) -> None:
        if not params:
            params = {}
        combined_params = deepcopy(default_format_setting['to_json'])
        combined_params.update(params)
        with open(path, 'w+') as file_to_write:
            json.dump(json.loads(df.to_json(**combined_params)), file_to_write, indent=1)
    return json_with_indent_inner


supported_formats = {'json': json_with_indent(),
                     'csv': output_writer('to_csv'),
                     'feather': lambda df: getattr(df, 'to_feather'),
                     'md': lambda df: getattr(df, 'to_markdown'),
                     'parquet': lambda df: getattr(df, 'to_parquet'),
                     'html': lambda df: getattr(df, 'to_html'),
                     'excel': to_excel,
                     'hdf': lambda df: getattr(df, 'to_hdf'),
                     'pickle': lambda df: getattr(df, 'to_pickle')}

user_defined_writers = {}


def get_writer(format_key: Text) -> Callable:
    supported_formats.update(user_defined_writers)
    writer = supported_formats.get(format_key)
    if not writer:
        raise Exception(f'Output format {format_key} not exist. '
                        f'Please, provide correct name or add your custom output writer'
                        f'with OutputWriter.user_defined_writers[\'your_format_name\'] = python_callable')
    return writer
