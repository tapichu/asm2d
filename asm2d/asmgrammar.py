# Grammar definition file for a subset of the 68HC11, with custom instructions
# for drawing.

from __future__ import print_function
import sys
from functools import wraps
from asmtokens import tokens

class Const:
    "AST node for a constant."
    def __init__(self, id, value, lineno):
        self.id = id
        self.value = value
        self.lineno = lineno
    def __repr__(self):
        return "Const<Id: '{0}', Value: {1:d}, Line: {2:d}>"\
                .format(self.id, self.value, self.lineno)

class Var:
    "AST node for a variable."
    def __init__(self, id, size, lineno):
        self.id = id
        self.size = size
        self.lineno = lineno
    def __repr__(self):
        return "Var<Id: '{0}', Size: {1:d}, Line: {2:d}>"\
                .format(self.id, self.size, self.lineno)

class Inst:
    "AST node for an instruction."
    def __init__(self, label, inst, size, lineno):
        self.label = label
        self.inst = inst
        self.size = size
        self.lineno = lineno
    def __repr__(self):
        return "Inst<Label: '{0}', Size: {1:d}, Line: {2:d}, Detail: {3!r}>"\
                .format(self.label, self.size, self.lineno, str(self.inst))

# Helper decorator

def lineno(n):
    def lineno_decorator(fn):
        @wraps(fn)
        def set_lineno(p):
            """Set the line number of the production using the line number
            of the nth terminal in the production's body.
            """
            p.set_lineno(0, p.lineno(n))
            return fn(p)
        return set_lineno
    return lineno_decorator

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
    error("Syntax error in constant declaration {0} (at line: {1:d})", p[1], p.lineno(1))

def p_element_variable(p):
    'element : IDENTIFIER VAR NUM'
    p[0] = Var(p[1], p[3], p.lineno(1))
def p_element_variable_error(p):
    'element : IDENTIFIER error NUM'
    error("Syntax error in variable declaration {0} (at line: {1:d})", p[1], p.lineno(1))

def p_element_instruction_label(p):
    'element : IDENTIFIER instruction'
    p[0] = Inst(p[1], p[2], p[2][1], p.lineno(1))
def p_element_instruction_label_error(p):
    'element : IDENTIFIER error'
    error("Syntax error in instruction at label {0} (at line: {1:d})", p[1], p.lineno(1))

def p_element_instruction(p):
    'element : instruction'
    p[0] = Inst('', p[1], p[1][1], p.lineno(1))
def p_element_instruction_error(p):
    'element : error'
    error("ERROR: Syntax error in instruction (at line: {0:d})", p.lineno(1))

def p_element_empty(p):
    'element : '
    pass

## Instructions

# ABA, ABX
@lineno(1)
def p_instruction_add(p):
    '''instruction : ABA
                   | ABX'''
    p[0] = (p[1], 1)

# ADDD
@lineno(1)
def p_instruction_addd_const(p):
    'instruction : ADDD CONST_IDENTIFIER'
    p[0] = (p[1], 3, 'const', p[2])

@lineno(1)
def p_instruction_addd_var(p):
    'instruction : ADDD IDENTIFIER'
    p[0] = (p[1], 3, 'var', p[2])

@lineno(1)
def p_instruction_addd(p):
    'instruction : ADDD HEX_NUM'
    p[0] = (p[1], 3, 'imm', p[2])

# ASRD
@lineno(1)
def p_instruction_asrd(p):
    'instruction : ASRD'
    p[0] = (p[1], 1)

# BCS, BEQ, BHI, BLO, BNE, BRA
@lineno(1)
def p_instruction_branch(p):
    '''instruction : BCS IDENTIFIER
                   | BEQ IDENTIFIER
                   | BHI IDENTIFIER
                   | BLO IDENTIFIER
                   | BNE IDENTIFIER
                   | BRA IDENTIFIER'''
    p[0] = (p[1], 2, p[2])

# CLRS
@lineno(1)
def p_instruction_clrs(p):
    'instruction : CLRS'
    p[0] = (p[1], 1)

# CPK, CPX
@lineno(1)
def p_instruction_compare_const(p):
    '''instruction : CPK CONST_IDENTIFIER
                   | CPX CONST_IDENTIFIER'''
    p[0] = (p[1], 3, 'const', p[2])

@lineno(1)
def p_instruction_compare(p):
    '''instruction : CPK HEX_NUM
                   | CPX HEX_NUM'''
    p[0] = (p[1], 3, 'imm', p[2])

# DRHLN, DRRCT, DRVLN
@lineno(1)
def p_instruction_draw(p):
    '''instruction : DRCL
                   | DRHLN
                   | DRRCT
                   | DRVLN'''
    p[0] = (p[1], 1)

# INX
@lineno(1)
def p_instruction_inx(p):
    'instruction : INX'
    p[0] = (p[1], 1)

# JSR
@lineno(1)
def p_instruction_jsr(p):
    'instruction : JSR IDENTIFIER'
    p[0] = (p[1], 3, p[2])

# LDB, LDD, LDG, LDR, LDX, LDXA, LDXB, LDYA, LDYB
@lineno(1)
def p_instruction_load_const(p):
    '''instruction : LDAA CONST_IDENTIFIER
                   | LDAB CONST_IDENTIFIER
                   | LDB CONST_IDENTIFIER
                   | LDD CONST_IDENTIFIER
                   | LDG CONST_IDENTIFIER
                   | LDR CONST_IDENTIFIER
                   | LDX CONST_IDENTIFIER
                   | LDXA CONST_IDENTIFIER
                   | LDXB CONST_IDENTIFIER
                   | LDYA CONST_IDENTIFIER
                   | LDYB CONST_IDENTIFIER'''
    size = 2 if p[1] in {'LDAA', 'LDAB', 'LDB', 'LDG', 'LDR'} else 3
    p[0] = (p[1], size, 'const', p[2])

@lineno(1)
def p_instruction_load_var(p):
    '''instruction : LDAA IDENTIFIER
                   | LDAB IDENTIFIER
                   | LDB IDENTIFIER
                   | LDD IDENTIFIER
                   | LDG IDENTIFIER
                   | LDR IDENTIFIER
                   | LDX IDENTIFIER
                   | LDXA IDENTIFIER
                   | LDXB IDENTIFIER
                   | LDYA IDENTIFIER
                   | LDYB IDENTIFIER'''
    p[0] = (p[1], 3, 'var', p[2])

@lineno(1)
def p_instruction_load(p):
    '''instruction : LDAA HEX_NUM
                   | LDAB HEX_NUM
                   | LDB HEX_NUM
                   | LDD HEX_NUM
                   | LDG HEX_NUM
                   | LDR HEX_NUM
                   | LDX HEX_NUM
                   | LDXA HEX_NUM
                   | LDXB HEX_NUM
                   | LDYA HEX_NUM
                   | LDYB HEX_NUM'''
    size = 2 if p[1] in {'LDAA', 'LDAB', 'LDB', 'LDG', 'LDR'} else 3
    p[0] = (p[1], size, 'imm', p[2])

# NEGA
@lineno(1)
def p_instruction_nega(p):
    'instruction : NEGA'
    p[0] = (p[1], 1)

# RSTK
@lineno(1)
def p_instruction_rstk(p):
    'instruction : RSTK'
    p[0] = (p[1], 1)

# RTS
@lineno(1)
def p_instruction_rts(p):
    'instruction : RTS'
    p[0] = (p[1], 1)

# STAA, STAB, STX
@lineno(1)
def p_instruction_store_var(p):
    '''instruction : STAA IDENTIFIER
                   | STAB IDENTIFIER
                   | STD IDENTIFIER
                   | STX IDENTIFIER'''
    p[0] = (p[1], 3, 'var', p[2])

# SUBD
@lineno(1)
def p_instruction_subd_const(p):
    'instruction : SUBD CONST_IDENTIFIER'
    p[0] = (p[1], 3, 'const', p[2])

@lineno(1)
def p_instruction_subd(p):
    'instruction : SUBD HEX_NUM'
    p[0] = (p[1], 3, 'imm', p[2])

# TDXA, TDYA
@lineno(1)
def p_instruction_transfer(p):
    '''instruction : TDXA
                   | TDYA'''
    p[0] = (p[1], 1)

def p_error(p):
    value = p.value if p.value != '\n' else 'NEWLINE'
    error("Syntax error near token {0} (at line: {1:d})", value, p.lineno)

def error(msg, *args):
    print("ERROR: {}".format(msg.format(*args)), file=sys.stderr)
