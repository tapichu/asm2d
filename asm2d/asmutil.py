import ply.lex as lex
import ply.yacc as yacc
import asmtokens
import asmgrammar
from asmconstants import SIZE

def create_lexer():
    asmlexer = lex.lex(module=asmtokens)
    asmlexer.errors = False
    return asmlexer

def create_parser(debug=True):
    if debug:
        asmparser = yacc.yacc(module=asmgrammar, tabmodule="parsetabasm")
    else:
        asmparser = yacc.yacc(module=asmgrammar, write_tables=0, debug=0)
    asmparser.errors = False
    asmparser.const_table = {}
    asmparser.data_table = {}
    asmparser.inst_table = {}
    asmparser.data_table[SIZE] = 0
    asmparser.inst_table[SIZE] = 0
    return asmparser
