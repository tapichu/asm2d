import ply.lex as lex
import ply.yacc as yacc
import asmtokens
import asmgrammar
from asmconstants import SIZE

# Factories

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
