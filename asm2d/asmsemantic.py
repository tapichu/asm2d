# Semantic analysis of an AST (parsed 68hc11 assembly code).

from __future__ import print_function
from bitstring import BitArray
from asmconstants import SIZE
from asmerrors import error
from asmgrammar import Inst, Var

MAIN_ADDR = 0

def analyse(ast, data_table, inst_table, errors):
    "Semantic analysis for the AST."

    if '.main' not in inst_table:
        error("Main entry point not defined", errors=errors)

    first_pass(ast, data_table, inst_table, errors)
    second_pass(ast, data_table, inst_table, errors)

    errors.report_errors()

def first_pass(ast, data_table, inst_table, errors):
    """The first pass assigns an address to variables (data segment) and
    labels, and checks for undefined references.
    """
    data_offset = inst_table[SIZE]
    code_offset = 0
    main_lineno = 0

    for elem in ast:
        if isinstance(elem, Var):
            data_table[elem.id] = data_offset
            data_offset += elem.size
        if isinstance(elem, Inst):
            if elem.label != '':
                if elem.label == '.main': main_lineno = elem.lineno
                inst_table[elem.label] = code_offset
            code_offset += elem.size

            if len(elem.inst) == 3:
                name, size, label = elem.inst
                if label not in inst_table:
                    error("Undefined label {}", label, lineno=elem.lineno, errors=errors)
            elif len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if inst_type == 'var':
                    if value not in data_table:
                        error("Undefined variable {}", value, lineno=elem.lineno, errors=errors)
                    else:
                        elem.inst = (name, size, 'ext', data_table[value])

    if '.main' in inst_table and inst_table['.main'] != MAIN_ADDR:
        error("Main label should be the first instruction",lineno=main_lineno, errors=errors)

def second_pass(ast, data_table, inst_table, errors):
    """The second pass handles unsigned values (color registers, fps) and checks
    that immediate values are of the correct size (one or two bytes).
    """
    for elem in ast:
        if isinstance(elem, Inst):
            if len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if name in {'CPK', 'LDB', 'LDG', 'LDR'}:
                    if value < -128 or value > 127:
                        error("Value out of range {0} (instruction {1})",
                                value, name, lineno=elem.lineno, errors=errors)
                    else:
                        value = BitArray(int=value, length=8).uint
                        elem.inst = (name, size, inst_type, value)
                elif inst_type == 'imm' and name != 'DRSYM':
                    if size == 2:
                        if value < -128 or value > 127:
                            error("Value out of range {0} (instruction {1})",
                                    value, name, lineno=elem.lineno, errors=errors)
                    elif size == 3:
                        if value < -32768 or value > 32767:
                            error("Value out of range {0} (instruction {1})",
                                    value, name, lineno=elem.lineno, errors=errors)
            elif len(elem.inst) == 5:
                name, _, _, offset, _ = elem.inst
                if offset < -128 or offset > 127:
                    error("Value out of range {0} (instruction {1})",
                            offset, name, lineno=elem.lineno, errors=errors)
