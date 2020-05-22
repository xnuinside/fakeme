from fakeme.parsers.alchemy import AlchemyParser
from tokenize import generate_tokens
from token import OP

def main(path):
    version = "0.0.1"

    # create parser
    #schema = AlchemyParser(path).run()
    #print("Schema", schema)

    tables = {}
    stack = []
    model_ = {}
    with open(path, 'r+') as f_input:
        for token in generate_tokens(f_input.readline):
            print(token)
            if token.string == 'class':
                if len(stack) > 0:
                    stack = []
                stack.append(token.string)
            elif stack[-1] == 'class':
                stack = []
                stack.append(token.string)
            elif token.name == '__tablename__':
                table_name = True
            elif table_name and token != OP:
                table_name = token.string




    print(tables)


if __name__ == '__main__':
    main(path='/Users/jvolkova/fakeme/fakeme/db_sample.py')
