#!/usr/bin/env python
#-*- coding: utf-8 -*-

import argparse
import os
import sys
import ply.lex as lex
import ply.yacc as yacc
import asmtokens
import asmgrammar
import asmsemantic
import asmcodegen

def read_file(filename):
    "Read the contents of a file into memory."
    if not os.path.isfile(filename):
        print "The file '%s' does not exists." % filename
        exit(1)
    try:
        with open(filename) as f:
            contents = f.read()
        return contents
    except IOError:
        print "Error reading file '%s'." % filename
        exit(1)

def compiler(filename, var_name):
    "Run the compiler on the source file."
    const_table = {}
    data_table = {}
    inst_table = {}

    asmlexer = lex.lex(module=asmtokens)
    asmparser = yacc.yacc(module=asmgrammar, tabmodule="parsetabasm")

    input_string = read_file(filename)
    ast = asmparser.parse(input_string, lexer=asmlexer)

    asmsemantic.semantic_analysis(ast, const_table, data_table, inst_table)
    asmcodegen.codegen(ast, data_table, inst_table, var_name=var_name)

def main():
    "Parse the command line arguments and invoke the compiler."
    parser = argparse.ArgumentParser(
            description='Assembler for an extended 68HC11 clone.',
            epilog='')
    parser.add_argument("file", help='the source file.')
    parser.add_argument("-n", "--name", default="memory",
            help='the name of the memory variable.')
    args = parser.parse_args()

    compiler(args.file, args.name)

if __name__ == '__main__':
    main()
