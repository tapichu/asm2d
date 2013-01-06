from __future__ import print_function
import sys
import asm2d.asmcodegen as asmcodegen
import asm2d.asmsemantic as asmsemantic
import asm2d.asmutil as asmutil
from asm2d.asmerrors import ErrorReport

def test_codegen(input_string):
    errors = ErrorReport()
    asmlexer = asmutil.create_lexer(errors)
    asmparser = asmutil.create_parser(errors, debug=True)

    ast = asmparser.parse(input_string, lexer=asmlexer)
    asmsemantic.analyse(ast, asmparser.const_table, asmparser.data_table, asmparser.inst_table, errors)

    asmcodegen.codegen(ast, asmparser.data_table, asmparser.inst_table)

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
