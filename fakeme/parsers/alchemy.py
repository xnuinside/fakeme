from fakeme.parsers import parser


class AlchemyParser(parser.Parser):

    reserved = {
        'class': 'class',
        '__tablename__': 'TABLE_NAME'
    }

    types = {
        'INTEGER': 'INTEGER',
        'TINYINT': 'TINYINT',
        'SMALLINT': 'SMALLINT',
        'String': 'STRING',
        'FLOAT': 'FLOAT',
        'DOUBLE': 'DOUBLE',
        'INT': 'INT'
    }
    reserved.update(types)

    tokens = tuple(['COMMA',
                    'ASSIGN',
                    'ID',
                    'NEWLINE',
                    ] + list(reserved.values()))

    t_ignore = '\t\n<>();, '
    t_COMMA = r'\,'
    t_ASSIGN = r'\='

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')  # Check for reserved word
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        t.type = "NEWLINE"
        if t.lexer.paren_count == 0:
            return t

    def t_error(self, t):
        raise SyntaxError("Unknown symbol %r" % (t.value[0],))

    def p_error(self, p):
        # print "Error!", repr(p)
        raise SyntaxError(p, repr(p))

    def p_expression_type(self, p):
        """expr : ID STRING
                | ID INTEGER
                | ID INT
                | ID DOUBLE
                | ID FLOAT

        """
        if p[2] == 'STRING':
            p[0] = {p[1]: 'str'}
        elif p[2] == 'INTEGER' or p[2] == 'INT':
            p[0] = {p[1]: 'int'}
        elif p[2] == 'DOUBLE' or p[2] == 'FLOAT':
            p[0] = {p[1]: 'float'}