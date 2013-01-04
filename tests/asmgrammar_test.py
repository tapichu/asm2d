from __future__ import print_function
import sys
import pprint
import asm2d.asmutil as asmutil

def test_parser(input_string):
    asmlexer = asmutil.create_lexer()
    asmparser = asmutil.create_parser()

    ast = asmparser.parse(input_string, lexer=asmlexer)

    if asmlexer.errors or asmparser.errors:
        sys.exit(1)

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
