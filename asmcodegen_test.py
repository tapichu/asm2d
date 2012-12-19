from __future__ import print_function
import sys
import ply.lex as lex
import ply.yacc as yacc
import asmtokens
import asmgrammar
import asmsemantic
import asmcodegen

def test_codegen(input_string):
    const_table = {}
    data_table = {}
    inst_table = {}

    asmlexer = lex.lex(module=asmtokens)
    asmparser = yacc.yacc(module=asmgrammar, tabmodule="parsetabasm")
    ast = asmparser.parse(input_string, lexer=asmlexer)
    asmsemantic.semantic_analysis(ast, const_table, data_table, inst_table)
    asmcodegen.codegen(ast, data_table, inst_table)

def main():
    if len(sys.argv) < 2:
        print("Usage: asmcodegen_test.py file_path")
        sys.exit(1)

    file_name = sys.argv[1]
    with open(file_name) as f:
        contents = f.read()

    test_codegen(contents)

if __name__ == '__main__':
    main()
