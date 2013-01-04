from __future__ import print_function
import sys
import ply.lex as lex
import ply.yacc as yacc
import asmtokens
import asmgrammar
from asmconstants import SIZE

def create_lexer(errors):
    "Create an instance of the lexer."
    asmlexer = lex.lex(module=asmtokens)
    asmlexer.errors = errors
    return asmlexer

def create_parser(errors, debug=False):
    "Create an instance of the parser."
    if debug:
        asmparser = yacc.yacc(module=asmgrammar, tabmodule="parsetabasm")
    else:
        asmparser = yacc.yacc(module=asmgrammar, write_tables=0, debug=0)
    asmparser.errors = errors
    asmparser.const_table = {}
    asmparser.data_table = {}
    asmparser.inst_table = {}
    asmparser.data_table[SIZE] = 0
    asmparser.inst_table[SIZE] = 0
    return asmparser

class ErrorReport:
    "A class to count errors and report totals."

    def __init__(self):
        self._num_errors = 0

    def has_errors(self):
        return self._num_errors > 0

    def num_errors(self):
        return self._num_errors

    def add_error(self):
        self._num_errors += 1

    def report_errors(self):
        if self.has_errors():
            if self.num_errors() == 1:
                print("There is 1 error.", file=sys.stderr)
            else:
                print("There are {0:d} errors.".format(self.num_errors()), file=sys.stderr)
            sys.exit(1)
