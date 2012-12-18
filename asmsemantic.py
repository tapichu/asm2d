# Semantic analysis of an AST (parsed 68hc11 assembly code).

from asmgrammar import Const, Inst, Var

MAIN_ADDR = 0

# memoria(0) := "11111111";

def semantic_analysis(ast, const_table, data_table, inst_table):
    data = {'data_seg_size': 0, 'code_seg_size': 0}
    first_pass(ast, const_table, data_table, inst_table, data)
    second_pass(ast, const_table, data_table, inst_table, data)

def first_pass(ast, const_table, data_table, inst_table, data):
    """The first pass of semantic analysis records every constant and variable
    definition, and calculates the size of the code and data segments.
    """
    for elem in ast:
        if isinstance(elem, Const):
            if elem.id in const_table:
                print "WARNING: overriding already defined constant %s" % elem.id
            const_table[elem.id] = elem.value
        elif isinstance(elem, Var):
            if elem.id in data_table:
                print "ERROR: Duplicate name definition: %s" % elem.id
                exit(1)
            data_table[elem.id] = -1
            data['data_seg_size'] += elem.size
        elif isinstance(elem, Inst):
            if elem.label != '':
                if elem.label in inst_table:
                    print "ERROR: Duplicate label definition: %s" % elem.label
                    exit(1)
                inst_table[elem.label] = -1
            data['code_seg_size'] += elem.size

    if '.main' not in inst_table:
        print "ERROR: Main entry point not defined"
        exit(1)

def second_pass(ast, const_table, data_table, inst_table, data):
    """The second pass assigns an address to variables (data segment) and
    labels. It substitutes constant references with their values and checks
    for undefined references.
    """
    data_offset = 0
    code_offset = 0

    for elem in ast:
        if isinstance(elem, Var):
            data_table[elem.id] = data['code_seg_size'] + data_offset
            data_offset += elem.size
        if isinstance(elem, Inst):
            if elem.label != '':
                inst_table[elem.label] = code_offset
            code_offset += elem.size

            if len(elem.inst) == 3:
                name, size, label = elem.inst
                if label not in inst_table:
                    print "ERROR: Undefined label %s" % label
                    exit(1)
            elif len(elem.inst) == 4:
                name, size, inst_type, value = elem.inst
                if inst_type == 'const':
                    if value not in const_table:
                        print "ERROR: Undefined constant %s" % value
                        exit(1)
                    elem.inst = (name, size, 'imm', const_table[value])
                elif inst_type == 'var':
                    if value not in data_table:
                        print "ERROR: Undefined variable %s" % value
                        exit(1)
                    elem.inst = (name, size, 'dir', data_table[value])

    if inst_table['.main'] != 0:
        print "ERROR: Main label should be the first instruction"
        exit(1)
