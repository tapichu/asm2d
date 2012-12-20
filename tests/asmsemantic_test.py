from __future__ import print_function
import sys
import pprint
import ply.lex as lex
import ply.yacc as yacc
import asm2d.asmtokens as asmtokens
import asm2d.asmgrammar as asmgrammar
import asm2d.asmsemantic as asmsemantic

def test_semantic_analysis(input_string):
    const_table = {}
    data_table = {}
    inst_table = {}

    asmlexer = lex.lex(module=asmtokens)
    asmparser = yacc.yacc(module=asmgrammar, tabmodule="parsetabasm")
    ast = asmparser.parse(input_string, lexer=asmlexer)
    asmsemantic.semantic_analysis(ast, const_table, data_table, inst_table)
    return (ast, const_table, data_table, inst_table)

def main():
    if len(sys.argv) < 2:
        print("Usage: asmsemantic_test.py file_path")
        sys.exit(1)

    file_name = sys.argv[1]
    with open(file_name) as f:
        contents = f.read()

    ast, const_table, data_table, inst_table = test_semantic_analysis(contents)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(const_table)
    pp.pprint(data_table)
    pp.pprint(inst_table)
    pp.pprint(ast)

if __name__ == '__main__':
    main()
