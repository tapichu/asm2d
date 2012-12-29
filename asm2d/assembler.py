#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import pkg_resources
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
        print("The file '{}' does not exists.".format(filename), file=sys.stderr)
        sys.exit(1)
    try:
        with open(filename) as f:
            contents = f.read()
        return contents
    except IOError:
        print("Error reading file '{}'.".format(filename), file=sys.stderr)
        sys.exit(1)

def run_compiler(input_file, output_file, no_words):
    "Run the compiler on the source file."
    const_table = {}
    data_table = {}
    inst_table = {}

    asmlexer = lex.lex(module=asmtokens)
    asmparser = yacc.yacc(module=asmgrammar, write_tables=0, debug=0)

    input_string = read_file(input_file)
    ast = asmparser.parse(input_string, lexer=asmlexer)
    asmsemantic.semantic_analysis(ast, const_table, data_table, inst_table)

    with open(output_file, 'w+') as f:
        asmcodegen.codegen(ast, data_table, inst_table, no_words=no_words, outfile=f)

def main():
    "Parse the command line arguments and invoke the compiler."
    parser = argparse.ArgumentParser(
            description='Assembler for an extended 68HC11 clone.',
            epilog='As private parts to the gods are we, they play with us for their sport.')
    parser.add_argument('file', help='the source file')
    parser.add_argument('-o', '--output-file',
            help='the output file')
    parser.add_argument('-w', '--words', type=int, default=None,
            help='the number of words in the memory')
    version = 'asm2d {}'.format(pkg_resources.require('asm2d')[0].version)
    parser.add_argument('-v', '--version', action='version', version=version)
    args = parser.parse_args()

    output_file = args.output_file
    if output_file is None:
        filename, ext = os.path.splitext(args.file)
        output_file = filename + '.mif'

    run_compiler(args.file, output_file, args.words)

if __name__ == '__main__':
    main()
