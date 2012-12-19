# Grammar definition file for a subset of the 68HC11, with custom instructions
# for drawing.

import ply.yacc as yacc
from asmtokens import tokens

class Const:
    def __init__(self, id, value, lineno):
        self.id = id
        self.value = value
        self.lineno = lineno
    def __repr__(self):
        return "Const<Id: '{0}', Value: {1:d}, Line: {2:d}>".format(self.id, self.value, self.lineno)

class Var:
    def __init__(self, id, size, lineno):
        self.id = id
        self.size = size
        self.lineno = lineno
    def __repr__(self):
        return "Var<Id: '{0}', Size: {1:d}, Line: {2:d}>".format(self.id, self.size, self.lineno)

class Inst:
    def __init__(self, label, inst, size, lineno):
        self.label = label
        self.inst = inst
        self.size = size
        self.lineno = lineno
    def __repr__(self):
        return "Inst<Label: '{0}', Size: {1:d}, Line: {2:d}, Detail: {3!r}>"\
                .format(self.label, self.size, self.lineno, str(self.inst))

start = 'asm'

def p_asm(p):
    'asm : element ENDL asm'
    if p[1] is None:
        p[0] = p[3]
    else:
        p[0] = [p[1]] + p[3]
def p_asm_empty(p):
    'asm : '
    p[0] = []

# Elements

def p_element_constant(p):
    'element : CONST_IDENTIFIER CONST HEX_NUM'
    p[0] = Const(p[1], p[3], p.lineno(1))
def p_element_constant_error(p):
    'element : CONST_IDENTIFIER error HEX_NUM'
    print "ERROR: Syntax error in constant declaration {0} (at line: {1:d})"\
            .format(p[1], p.lineno(1))

def p_element_variable(p):
    'element : IDENTIFIER VAR NUM'
    p[0] = Var(p[1], p[3], p.lineno(1))
def p_element_variable_error(p):
    'element : IDENTIFIER error NUM'
    print "ERROR: Syntax error in variable declaration {0} (at line: {1:d})" \
            .format(p[1], p.lineno(1))

def p_element_instruction_label(p):
    'element : IDENTIFIER instruction'
    p[0] = Inst(p[1], p[2], p[2][1], p.lineno(1))
def p_element_instruction_label_error(p):
    'element : IDENTIFIER error'
    print "ERROR: Syntax error in instruction at label {0} (at line: {1:d})" \
            .format(p[1], p.lineno(1))

def p_element_instruction(p):
    'element : instruction'
    p[0] = Inst('', p[1], p[1][1], p.lineno(1))
def p_element_instruction_error(p):
    'element : error'
    print "ERROR: Syntax error in instruction (at line: {0:d})".format(p.lineno(1))

def p_element_empty(p):
    'element : '
    pass

## Instructions

# ABX
def p_instruction_abx(p):
    'instruction : ABX'
    p[0] = (p[1], 1)
    p.set_lineno(0, p.lineno(1))

# ADDD
def p_instruction_addd_const(p):
    'instruction : ADDD CONST_IDENTIFIER'
    p[0] = (p[1], 3, 'const', p[2])
    p.set_lineno(0, p.lineno(1))

def p_instruction_addd_var(p):
    'instruction : ADDD IDENTIFIER'
    p[0] = (p[1], 3, 'var', p[2])
    p.set_lineno(0, p.lineno(1))

def p_instruction_addd(p):
    'instruction : ADDD HEX_NUM'
    p[0] = (p[1], 3, 'imm', p[2])
    p.set_lineno(0, p.lineno(1))

# ASRD
def p_instruction_asrd(p):
    'instruction : ASRD'
    p[0] = (p[1], 1)
    p.set_lineno(0, p.lineno(1))

# BEQ, BNE, BRA
def p_instruction_branch(p):
    '''instruction : BEQ IDENTIFIER
                   | BHI IDENTIFIER
                   | BLO IDENTIFIER
                   | BNE IDENTIFIER
                   | BRA IDENTIFIER'''
    p[0] = (p[1], 2, p[2])
    p.set_lineno(0, p.lineno(1))

# CLRS
def p_instruction_clrs(p):
    'instruction : CLRS'
    p[0] = (p[1], 1)
    p.set_lineno(0, p.lineno(1))

# CPK, CPX
def p_instruction_compare_const(p):
    '''instruction : CPK CONST_IDENTIFIER
                   | CPX CONST_IDENTIFIER'''
    p[0] = (p[1], 3, 'const', p[2])
    p.set_lineno(0, p.lineno(1))

def p_instruction_compare(p):
    '''instruction : CPK HEX_NUM
                   | CPX HEX_NUM'''
    p[0] = (p[1], 3, 'imm', p[2])
    p.set_lineno(0, p.lineno(1))

# DRHLN, DRRCT, DRVLN
def p_instruction_draw(p):
    '''instruction : DRCL
                   | DRHLN
                   | DRRCT
                   | DRVLN'''
    p[0] = (p[1], 1)
    p.set_lineno(0, p.lineno(1))

# JSR
def p_instruction_jsr(p):
    'instruction : JSR IDENTIFIER'
    p[0] = (p[1], 3, p[2])
    p.set_lineno(0, p.lineno(1))

# LDB, LDD, LDG, LDK, LDR, LDX, LDXA, LDXB, LDYA, LDYB
def p_instruction_load_const(p):
    '''instruction : LDAA CONST_IDENTIFIER
                   | LDAB CONST_IDENTIFIER
                   | LDB CONST_IDENTIFIER
                   | LDD CONST_IDENTIFIER
                   | LDG CONST_IDENTIFIER
                   | LDK CONST_IDENTIFIER
                   | LDR CONST_IDENTIFIER
                   | LDX CONST_IDENTIFIER
                   | LDXA CONST_IDENTIFIER
                   | LDXB CONST_IDENTIFIER
                   | LDYA CONST_IDENTIFIER
                   | LDYB CONST_IDENTIFIER'''
    size = 2 if p[1] in {'LDAA', 'LDAB', 'LDB', 'LDG', 'LDR'} else 3
    p[0] = (p[1], size, 'const', p[2])
    p.set_lineno(0, p.lineno(1))

def p_instruction_load_var(p):
    '''instruction : LDAA IDENTIFIER
                   | LDAB IDENTIFIER
                   | LDB IDENTIFIER
                   | LDD IDENTIFIER
                   | LDG IDENTIFIER
                   | LDK IDENTIFIER
                   | LDR IDENTIFIER
                   | LDX IDENTIFIER
                   | LDXA IDENTIFIER
                   | LDXB IDENTIFIER
                   | LDYA IDENTIFIER
                   | LDYB IDENTIFIER'''
    p[0] = (p[1], 3, 'var', p[2])
    p.set_lineno(0, p.lineno(1))

def p_instruction_load(p):
    '''instruction : LDAA HEX_NUM
                   | LDAB HEX_NUM
                   | LDB HEX_NUM
                   | LDD HEX_NUM
                   | LDG HEX_NUM
                   | LDK HEX_NUM
                   | LDR HEX_NUM
                   | LDX HEX_NUM
                   | LDXA HEX_NUM
                   | LDXB HEX_NUM
                   | LDYA HEX_NUM
                   | LDYB HEX_NUM'''
    size = 2 if p[1] in {'LDAA', 'LDAB', 'LDB', 'LDG', 'LDR'} else 3
    p[0] = (p[1], size, 'imm', p[2])
    p.set_lineno(0, p.lineno(1))

# NEGA
def p_instruction_nega(p):
    'instruction : NEGA'
    p[0] = (p[1], 1)
    p.set_lineno(0, p.lineno(1))

# RTS
def p_instruction_rts(p):
    'instruction : RTS'
    p[0] = (p[1], 1)
    p.set_lineno(0, p.lineno(1))

# STAA, STAB, STX
def p_instruction_store_var(p):
    '''instruction : STAA IDENTIFIER
                   | STAB IDENTIFIER
                   | STD IDENTIFIER
                   | STX IDENTIFIER'''
    p[0] = (p[1], 3, 'var', p[2])
    p.set_lineno(0, p.lineno(1))

# SUBD
def p_instruction_subd_const(p):
    'instruction : SUBD CONST_IDENTIFIER'
    p[0] = (p[1], 3, 'const', p[2])
    p.set_lineno(0, p.lineno(1))

def p_instruction_subd(p):
    'instruction : SUBD HEX_NUM'
    p[0] = (p[1], 3, 'imm', p[2])
    p.set_lineno(0, p.lineno(1))

# TDXA, TDYA
def p_instruction_transfer(p):
    '''instruction : TDXA
                   | TDYA'''
    p[0] = (p[1], 1)
    p.set_lineno(0, p.lineno(1))

def p_error(p):
    value = p.value if p.value != '\n' else 'NEWLINE'
    print "ERROR: Syntax error near token {0} (at line: {1:d})".format(value, p.lineno)
