# Semantic analysis of an AST (parsed 68hc11 assembly code).

from asmgrammar import Const, Inst, Var
from bitstring import BitArray

MAIN_ADDR = 0
SIZE = '__SIZE'

errors = False
error_no = 0

def semantic_analysis(ast, const_table, data_table, inst_table):
    "Semantic analysis for the AST."
    global errors, error_no
    errors = False
    error_no = 0

    data_table[SIZE] = 0
    inst_table[SIZE] = 0

    first_pass(ast, const_table, data_table, inst_table)
    second_pass(ast, const_table, data_table, inst_table)
    third_pass(ast, const_table, data_table, inst_table)

    if errors:
        print "There are %d errors" % error_no
        exit(1)

def first_pass(ast, const_table, data_table, inst_table):
    """The first pass of semantic analysis records every constant and variable
    definition, and calculates the size of the code and data segments.
    """
    for elem in ast:
        if isinstance(elem, Const):
            if elem.id in const_table:
                warn("Overriding already defined constant %s", elem.id)
            const_table[elem.id] = elem.value
        elif isinstance(elem, Var):
            if elem.id in data_table:
                error("Duplicate name definition: %s", elem.id)
            data_table[elem.id] = -1
            data_table[SIZE] += elem.size
        elif isinstance(elem, Inst):
            if elem.label != '':
                if elem.label in inst_table:
                    error("Duplicate label definition: %s", elem.label)
                inst_table[elem.label] = -1
            inst_table[SIZE] += elem.size

    if '.main' not in inst_table:
        error("Main entry point not defined")

def second_pass(ast, const_table, data_table, inst_table):
    """The second pass assigns an address to variables (data segment) and
    labels. It substitutes constant references with their values and checks
    for undefined references.
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
                    error("Undefined label %s", label)
            elif len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if inst_type == 'const':
                    if value not in const_table:
                        error("Undefined constant %s", value)
                    else:
                        elem.inst = (name, size, 'imm', const_table[value])
                elif inst_type == 'var':
                    if value not in data_table:
                        error("Undefined variable %s", value)
                    else:
                        elem.inst = (name, size, 'ext', data_table[value])

    if inst_table['.main'] != MAIN_ADDR:
        error("Main label should be the first instruction")

def third_pass(ast, const_table, data_table, inst_table):
    """The third pass handles unsigned values (color registers) and checks that
    immediate values are of the correct size (one or two bytes).
    """
    for elem in ast:
        if isinstance(elem, Inst):
            if len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if name in {'LDB', 'LDG', 'LDR'}:
                    value = BitArray(int=value, length=8).uint
                    elem.inst = (name, size, inst_type, value)
                if inst_type == 'imm':
                    if name in {'LDB', 'LDG', 'LDR'}:
                        if value < 0 or value > 255:
                            error("Value out of range %s (instruction %s)", value, name)
                    elif size == 2:
                        if value < -128 or value > 127:
                            error("Value out of range %s (instruction %s)", value, name)
                    elif size == 3:
                        if value < -32768 or value > 32767:
                            error("Value out of range %s (instruction %s)", value, name)


# TODO: line numbers
def warn(msg, *args):
    "Print a warning message."
    print "WARNING: " + msg % args

def error(msg, *args):
    "Pring an error message, increment the global error count."
    global errors, error_no
    errors = True
    error_no += 1
    print "ERROR: " + msg % args
