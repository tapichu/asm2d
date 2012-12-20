from __future__ import print_function
import sys
import pprint
import ply.lex as lex
import ply.yacc as yacc
import asm2d.asmtokens as asmtokens
import asm2d.asmgrammar as asmgrammar

def test_parser(input_string):
    asmlexer = lex.lex(module=asmtokens)
    asmparser = yacc.yacc(module=asmgrammar, tabmodule="parsetabasm")
    return asmparser.parse(input_string, lexer=asmlexer)

def main():
    if len(sys.argv) < 2:
        print("Usage: asmparser_test.py file_path")
        sys.exit(1)

    file_name = sys.argv[1]
    with open(file_name) as f:
        contents = f.read()

    ast = test_parser(contents)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(ast)

if __name__ == '__main__':
    main()
