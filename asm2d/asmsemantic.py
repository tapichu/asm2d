# Semantic analysis of an AST (parsed 68hc11 assembly code).

from __future__ import print_function
import sys
from bitstring import BitArray
from asmgrammar import Inst, Var
from asmconstants import SIZE

MAIN_ADDR = 0

errors = False
error_no = 0

def analyse(ast, data_table, inst_table):
    "Semantic analysis for the AST."
    global errors, error_no
    errors = False
    error_no = 0

    if '.main' not in inst_table:
        error("Main entry point not defined")

    first_pass(ast, data_table, inst_table)
    second_pass(ast, data_table, inst_table)

    if errors:
        if error_no == 1:
            print("There is 1 error.")
        else:
            print("There are {0:d} errors.".format(error_no))
        exit(1)

def first_pass(ast, data_table, inst_table):
    """The first pass assigns an address to variables (data segment) and
    labels, and checks for undefined references.
    """
    data_offset = inst_table[SIZE]
    code_offset = 0

    for elem in ast:
        if isinstance(elem, Var):
            data_table[elem.id] = data_offset
            data_offset += elem.size
        if isinstance(elem, Inst):
            if elem.label != '':
                inst_table[elem.label] = code_offset
            code_offset += elem.size

            if len(elem.inst) == 3:
                name, size, label = elem.inst
                if label not in inst_table:
                    error("Undefined label {}", elem, label)
            elif len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if inst_type == 'var':
                    if value not in data_table:
                        error("Undefined variable {}", elem, value)
                    else:
                        elem.inst = (name, size, 'ext', data_table[value])

    if '.main' in inst_table and inst_table['.main'] != MAIN_ADDR:
        error("Main label should be the first instruction")

def second_pass(ast, data_table, inst_table):
    """The second pass handles unsigned values (color registers, fps) and checks
    that immediate values are of the correct size (one or two bytes).
    """
    for elem in ast:
        if isinstance(elem, Inst):
            if len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if name in {'CPK', 'LDB', 'LDG', 'LDR'}:
                    if value < -128 or value > 127:
                        error("Value out of range {0} (instruction {1})", elem, value, name)
                    else:
                        value = BitArray(int=value, length=8).uint
                        elem.inst = (name, size, inst_type, value)
                elif inst_type == 'imm' and name != 'DRSYM':
                    if size == 2:
                        if value < -128 or value > 127:
                            error("Value out of range {0} (instruction {1})", elem, value, name)
                    elif size == 3:
                        if value < -32768 or value > 32767:
                            error("Value out of range {0} (instruction {1})", elem, value, name)
            elif len(elem.inst) == 5:
                name, _, _, offset, _ = elem.inst
                if offset < -128 or offset > 127:
                    error("Value out of range {0} (instruction {1})", elem, offset, name)


# Error reporting

def warn(msg, node, *args):
    "Print a warning message."
    print("WARNING: {0} (at line: {1:d})".format(msg.format(*args), node.lineno), file=sys.stderr)

def error(msg, node=None, *args):
    "Pring an error message, increment the global error count."
    global errors, error_no
    errors = True
    error_no += 1

    if node is None:
        print("ERROR: {}".format(msg.format(*args)), file=sys.stderr)
    else:
        print("ERROR: {0} (at line: {1:d})".format(msg.format(*args), node.lineno), file=sys.stderr)
