# Semantic analysis of an AST (parsed 68hc11 assembly code).

from collections import namedtuple

Var = namedtuple('Var', 'addr size')

def semantic_analysis(ast, const_table, data_table, inst_table):
    data_seg_size, code_seg_size = first_pass(ast, const_table, data_table, inst_table)
    print data_seg_size, code_seg_size
    second_pass(ast, const_table, data_table, inst_table)

def first_pass(ast, const_table, data_table, inst_table):
    """The first pass of semantic analysis records every constant and variable
    definition, and calculates the size of variables and instructions.
    """
    data_seg_size = 0
    code_seg_size = 0

    for elem in ast:
        elem_type = elem[0]
        if elem_type == 'constant':
            _, name, value = elem
            if name in const_table:
                print "WARNING: overriding already defined constant %s" % name
            const_table[name] = value
        elif elem_type == 'variable':
            _, name, size = elem
            if name in data_table:
                print "ERROR: Duplicate name definition: %s" % name
                exit(1)
            data_table[name] = Var(-1, size)
            data_seg_size += size
        elif elem_type == 'instruction':
            _, label, instruction = elem
            size = inst_size(instruction)
            code_seg_size += size

            if label != '':
                if label in inst_table:
                    print "ERROR: Duplicate label definition: %s" % name
                    exit(1)
                inst_table[label] = -1

    if '.main' not in inst_table:
        print "ERROR: Main entry point not defined"
        exit(1)

    return data_seg_size, code_seg_size

def second_pass(ast, const_table, data_table, inst_table):
    """The second pass assigns an address to every instruction, substitutes
    constant references with their values and checks for undefined references.
    """
    pass

# Instruction types

inherent = {'ABX', 'ASRD', 'CLRS', 'DRCL', 'DRHLN', 'DRRCT', 'DRVLN', 'NEGA',
        'RTS', 'TDXA', 'TDYA'}
immediate = {}
direct = {}
extended = {'JSR', 'STAA', 'STAB', 'STD', 'STX'}
indexed = {}
relative = {'BEQ', 'BHI', 'BLO', 'BNE', 'BRA'}
ambiguous = {'ADDD', 'CPK', 'CPX', 'LDAA', 'LDAB', 'LDB', 'LDB', 'LDD', 'LDG',
        'LDK', 'LDR', 'LDX', 'LDXA', 'LDXB', 'LDYA', 'LDYB'}

INST_SIZE = {
        'inherent': 1,
        'immediate': 2,
        'direct': 2,
        'extended': 3,
        'indexed': 2,
        'relative': 2
        }

def inst_size(instruction):
    """Returns the size of the instruction, in number of bytes."""
    inst_type = instruction[0]

    if inst_type in inherent: return INST_SIZE['inherent']
    elif inst_type in immediate: return INST_SIZE['immediate']
    elif inst_type in direct: return INST_SIZE['direct']
    elif inst_type in extended: return INST_SIZE['extended']
    elif inst_type in indexed: return INST_SIZE['indexed']
    elif inst_type in relative: return INST_SIZE['relative']
    elif inst_type in ambiguous:
        access_type = instruction[1]
        if access_type == 'const': return INST_SIZE['immediate']
        elif access_type == 'imm': return INST_SIZE['immediate']
        elif access_type == 'var': return INST_SIZE['relative']
    else:
        if inst_type == 'SUBD': return 3
        else:
            print "ERROR: Unknown instruction %s" % inst_type
            exit(1)
