from __future__ import print_function
import sys
import pprint
import ply.lex as lex
import ply.yacc as yacc
import asm2d.asmtokens as asmtokens
import asm2d.asmgrammar as asmgrammar

SIZE = '__SIZE'

def test_parser(input_string):
    asmlexer = lex.lex(module=asmtokens)
    asmlexer.errors = False

    asmparser = yacc.yacc(module=asmgrammar, tabmodule="parsetabasm")
    asmparser.errors = False
    asmparser.const_table = {}
    asmparser.data_table = {}
    asmparser.inst_table = {}
    asmparser.data_table[SIZE] = 0
    asmparser.inst_table[SIZE] = 0

    ast = asmparser.parse(input_string, lexer=asmlexer)

    if asmlexer.errors or asmparser.errors:
        exit(1)

    return ast, asmparser

def main():
    if len(sys.argv) < 2:
        print("Usage: asmparser_test.py file_path")
        sys.exit(1)

    file_name = sys.argv[1]
    with open(file_name) as f:
        contents = f.read()

    ast, parser = test_parser(contents)

    pp = pprint.PrettyPrinter(indent=4)

    pp.pprint(parser.const_table)
    pp.pprint(parser.data_table)
    pp.pprint(parser.inst_table)
    pp.pprint(ast)

if __name__ == '__main__':
    main()
