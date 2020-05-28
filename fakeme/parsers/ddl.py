import os
import json
from fakeme.parsers.parser import Parser

# add type cast
# map types from one system to second system


class DDLParser(Parser):
    """
        lex and yacc parser for parse ddl into BQ schemas
    """
    reserved = {
        'IF': 'IF',
        'then': 'THEN',
        'else': 'ELSE',
        'while': 'WHILE',
        'USE': 'USE',
        'CREATE': 'CREATE',
        'TABLE': 'TABLE',
        'NOT': 'NOT',
        'EXISTS': 'EXISTS',
    }

    types = {
        'INTEGER': 'INTEGER',
        'TINYINT': 'TINYINT',
        'SMALLINT': 'SMALLINT',
        'STRING': 'STRING',
        'FLOAT': 'FLOAT',
        'DOUBLE': 'DOUBLE',
        'INT': 'INT',
        'DECIMAL': 'DECIMAL'
    }

    reserved.update(types)

    tokens = tuple([
                       'COMMA',
                       'ID',
                       'NEWLINE',
                   ] + list(reserved.values()))

    t_ignore = '\t\n<>();, .${}\r'
    t_COMMA = r'\,'

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9:]*'
        t.type = self.reserved.get(t.value, 'ID')  # Check for reserved word
        return t

    def t_int(self, t):
        r'[0-9]+\D'
        t.type = "INT"
        return t

    def t_newline(self, t):
        r'\n+'
        self.lexer.lineno += len(t.value)
        t.type = "NEWLINE"
        if self.lexer.paren_count == 0:
            return t

    def t_error(self, t):
        raise SyntaxError("Unknown symbol %r" % (t.value[0],))

    def p_error(self, p):
        raise SyntaxError(p)

    def p_expression_table_name(self, p):
        """expr : CREATE TABLE IF NOT EXISTS ID
                | CREATE TABLE IF NOT EXISTS ID ID
                | CREATE TABLE ID

        """
        pass

    def p_expression_type(self, p):
        """expr : ID STRING
                | ID INTEGER
                | ID INT
                | ID DOUBLE
                | ID FLOAT
                | ID SMALLINT
                | ID DECIMAL INT
                | ID DECIMAL INT INT
                | ID
        """
        type_str = 'STRING'

        p[0] = {"name": p[1].lower(), "type": type_str, "mode": "NULLABLE"}

    def dump_schema(self, dump_path):
        """ method to dump json schema """
        if not os.path.isdir(dump_path):
            os.makedirs(dump_path, exist_ok=True)
        with open("{}/{}_schema.json".format(dump_path, self.table_id),
                  'w+') as schema_file:
            json.dump(self.result, schema_file, indent=1)

    def run(self, dump=None, dump_path="dump_schemas"):
        """ run lex and yacc on prepared data from files """
        self.result = super().run()
        if dump:
            self.dump_schema(dump_path)
        return self.result
