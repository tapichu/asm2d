# Grammar definition file for a subset of the 68HC11, with custom instructions
# for drawing.

import ply.yacc as yacc
from asmtokens import tokens

start = 'asm'

def p_asm(p):
    'asm : element asm'
    p[0] = [p[1]] + p[2]
def p_asm_empty(p):
    'asm : '
    p[0] = []

# Elements

def p_element_constant(p):
    'element : CONST_IDENTIFIER CONST HEX_NUM'
    p[0] = ('constant', p[1], p[3])

def p_element_variable(p):
    'element : IDENTIFIER VAR NUM'
    p[0] = ('variable', p[1], p[3])

def p_element_instruction_main(p):
    'element : MAIN instruction'
    p[0] = ('instruction', '.main', p[2])

def p_element_instruction_label(p):
    'element : IDENTIFIER instruction'
    p[0] = ('instruction', p[1], p[2])

def p_element_instruction(p):
    'element : instruction'
    p[0] = ('instruction', '', p[1])

## Instructions

# ABX
def p_instruction_abx(p):
    'instruction : ABX'
    p[0] = (p[1],)

# BEQ, BNE, BRA
def p_instruction_branch(p):
    '''instruction : BEQ IDENTIFIER
                   | BNE IDENTIFIER
                   | BRA IDENTIFIER'''
    p[0] = (p[1], p[2])

# CLRS
def p_instruction_clrs(p):
    'instruction : CLRS'
    p[0] = (p[1],)

# CPK
def p_instruction_cpk_const(p):
    'instruction : CPK CONST_IDENTIFIER'
    p[0] = (p[1], 'const', p[2])

def p_instruction_cpk(p):
    'instruction : CPK HEX_NUM'
    p[0] = (p[1], 'imm', p[2])

# DRHLN, DRRCT, DRVLN
def p_instruction_draw(p):
    '''instruction : DRCL
                   | DRHLN
                   | DRRCT
                   | DRVLN'''
    p[0] = (p[1],)

# JSR
def p_instruction_jsr(p):
    'instruction : JSR IDENTIFIER'
    p[0] = (p[1], p[2])

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
    p[0] = (p[1], 'const', p[2])

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
    p[0] = (p[1], 'var', p[2])

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
    p[0] = (p[1], 'imm', p[2])

# RTS
def p_instruction_rts(p):
    'instruction : RTS'
    p[0] = (p[1],)

# STAA, STAB, STX
def p_instruction_store_var(p):
    '''instruction : STAA IDENTIFIER
                   | STAB IDENTIFIER
                   | STX IDENTIFIER'''
    p[0] = (p[1], 'var', p[2])

# SUBD
def p_instruction_subd_const(p):
    'instruction : SUBD CONST_IDENTIFIER'
    p[0] = (p[1], 'const', p[2])

def p_instruction_subd(p):
    'instruction : SUBD HEX_NUM'
    p[0] = (p[1], 'imm', p[2])

# TDXA, TDYA
def p_instruction_transfer(p):
    '''instruction : TDXA
                   | TDYA'''
    p[0] = (p[1],)

def p_error(p):
    print "ASM Syntax Error: near token %s (line %d)" % (p.type, p.lineno)
    yacc.errok()
