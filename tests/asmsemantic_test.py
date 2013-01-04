from __future__ import print_function
import sys
import pprint
import asm2d.asmsemantic as asmsemantic
import asm2d.asmutil as asmutil

def test_semantic_analysis(input_string):
    asmlexer = asmutil.create_lexer()
    asmparser = asmutil.create_parser()

    ast = asmparser.parse(input_string, lexer=asmlexer)
    asmsemantic.analyse(ast, asmparser.data_table, asmparser.inst_table)

    if asmlexer.errors or asmparser.errors:
        sys.exit(1)

    return (ast, asmparser.data_table, asmparser.inst_table)

def main():
    if len(sys.argv) < 2:
        print("Usage: asmsemantic_test.py file_path")
        sys.exit(1)

    file_name = sys.argv[1]
    with open(file_name) as f:
        contents = f.read()

    ast, data_table, inst_table = test_semantic_analysis(contents)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data_table)
    pp.pprint(inst_table)
    pp.pprint(ast)

if __name__ == '__main__':
    main()
