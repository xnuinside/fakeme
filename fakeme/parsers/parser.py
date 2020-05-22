from ply import *


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, file_path):
        self.data = self.get_data_from_file(file_path)
        self.result = {}
        lex.lex(module=self)
        yacc.yacc(module=self,
                  debug=True)

    @staticmethod
    def get_data_from_file(file_path):
        data = []
        with open(file=file_path) as df:
            for line in df.readlines():
                data.append(line)
            return df.read()

    def run(self):
        try:
            for line in self.data.split("\n"):
                self.result.update(yacc.parse(line))
        except SyntaxError:
            if not self.result:
                raise
        return self.result

