import os

from ply import lex, yacc


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods

        It could not be loaded or called without Subclass, for example - DDLParser

        Subclass must include tokens for parser and rules
    """
    def __init__(self, file_path: str, table_id: str = "") -> None:
        """ init parser for file """
        self.file_path = file_path
        self.data = self.get_data_from_file()
        self.result = []
        self.paren_count = 0
        self.lexer = lex.lex(object=self, debug=False)
        self.yacc = yacc.yacc(module=self, debug=False)
        self.table_id = table_id if table_id else self.get_table_id()

    def get_table_id(self):
        """ get table_id from file name if not provided as arg """
        return os.path.basename(self.file_path).split('.')[0]

    def get_data_from_ddl(self):
        """ get useful data from ddl """
        data, final_data = [], []
        last_elem, first_elem = None, None
        table_creating = None
        with open(self.file_path, 'r') as df:
            for line in df.readlines():
                if line.startswith("--"):
                    # remove comments line from file data
                    continue
                if 'SORTED' not in line and 'CLUSTERED' not in line and (
                        line.startswith("(") or line.startswith("\n(")
                        or line.replace("\n", "").endswith("(")):
                    first_elem = len(data)
                if "ALTER" in line and "(" in line:
                    line = line.split("(")[1].split(")")[0].replace(",", ",\n")
                if 'ASC' not in line and line.replace("\n", "").startswith(")"):
                    last_elem = len(data)
                elif line.startswith("CREATE"):
                    table_creating = line
                data.append(line)
        if table_creating:
            final_data.append(table_creating)
        if final_data:
            [final_data.append(line) for line in data[first_elem + 1:last_elem]]
        result_data = "".join(final_data)
        return result_data

    def get_data_from_hql(self):
        """ get useful data from hql """
        result_data = []
        with open(file=self.file_path) as df:
            for line in df.readlines():
                if not line.startswith("--"):
                    result_data.append(line)
        return result_data

    def get_data_from_file(self):
        """ start extracting data from a file """
        if self.file_path.endswith(".ddl"):
            return self.get_data_from_ddl()
        elif self.file_path.endswith(".hql"):
            return self.get_data_from_hql()
        else:
            raise ValueError("Parser supports only hql and ddl formats")

    def run(self):
        """ run lex and yacc on prepared data from files """
        for line in self.data.split("\n"):
            if line.replace("\n", "").replace("\t", ""):
                _parse_result = yacc.parse(line.upper())
                if _parse_result:
                    self.result.append(_parse_result)
        return self.result
