# Semantic analysis of an AST (parsed 68hc11 assembly code).

from __future__ import print_function
from asmconstants import SIZE, ONE_BYTE_INST
from asmerrors import error, warn
from asmgrammar import Inst, Var

MAIN_ADDR = 0

def analyse(ast, const_table, data_table, inst_table, errors):
    "Semantic analysis for the AST."

    if '.main' not in inst_table:
        error("Main entry point not defined", errors=errors)

    first_pass(ast, const_table, data_table, inst_table, errors)
    second_pass(ast, data_table, inst_table, errors)

    errors.report_errors()

def first_pass(ast, const_table, data_table, inst_table, errors):
    """The first pass assigns an address to variables (data segment) and
    labels, and checks for undefined references. It also warns about constants,
    variables and labels that are not used, and about mismatches between
    variable size and instruction size.
    """
    data_offset = inst_table[SIZE]
    code_offset = 0
    main_lineno = 0

    for elem in ast:
        if isinstance(elem, Var):
            data_table[elem.id].addr = data_offset
            data_offset += elem.size
        if isinstance(elem, Inst):
            if elem.label != '':
                if elem.label == '.main': main_lineno = elem.lineno
                inst_table[elem.label].addr = code_offset
            code_offset += elem.size

            if len(elem.inst) == 3:
                _, _, label = elem.inst
                if label not in inst_table:
                    error("Undefined label {}", label, lineno=elem.lineno, errors=errors)
                else:
                    inst_table[label].used = True
            elif len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if inst_type == 'var':
                    if value not in data_table:
                        error("Undefined variable {}", value, lineno=elem.lineno, errors=errors)
                    else:
                        data_table[value].used = True
                        elem.inst = (name, size, 'ext', data_table[value].addr)

                        var_size = data_table[value].size
                        inst_size = 1 if name in ONE_BYTE_INST else 2
                        if inst_size != var_size:
                            warn("Size mismatch. Instruction {0} expects {1:d} byte{2}, variable {3} has {4:d} byte{5}",
                                    name, inst_size, 's' if inst_size > 1 else '', value, var_size,
                                    's' if var_size > 1 else '', lineno=elem.lineno)
            elif len(elem.inst) == 5:
                _, _, inst_type, _, label = elem.inst
                if inst_type == 'imm-rel':
                    if label not in inst_table:
                        error("Undefined label {}", label, lineno=elem.lineno, errors=errors)
                    else:
                        inst_table[label].used = True

    # Warnings for unused constants, variables and labels
    for const in [k for k in const_table if const_table[k].used == False]:
        warn("Unused constant {}", const, lineno=const_table[const].lineno)

    for var in [k for k in data_table if k != SIZE and data_table[k].used == False]:
        warn("Unused variable {}", var, lineno=data_table[var].lineno)

    for label in [k for k in inst_table if k != SIZE and inst_table[k].used == False]:
        warn("Unused label {}", label, lineno=inst_table[label].lineno)

    if '.main' in inst_table and inst_table['.main'].addr != MAIN_ADDR:
        error("Main label should be the first instruction",lineno=main_lineno, errors=errors)

def second_pass(ast, data_table, inst_table, errors):
    """The second pass handles unsigned values (color registers, fps) and checks
    that immediate values are of the correct size (one or two bytes).
    """
    for elem in ast:
        if isinstance(elem, Inst):
            if len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if name in {'CPK', 'LDB', 'LDG', 'LDR', 'RNDA'}:
                    if value < 0 or value > 255:
                        error("Value out of range {0} (instruction {1})",
                                value, name, lineno=elem.lineno, errors=errors)
                    else:
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
                name, _, inst_type, offset, _ = elem.inst
                if inst_type == 'ind':
                    if offset < -128 or offset > 127:
                        error("Value out of range {0} (instruction {1})",
                                offset, name, lineno=elem.lineno, errors=errors)
