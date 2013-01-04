# Grammar definition file for a subset of the 68HC11, with custom instructions
# for drawing.

from __future__ import print_function
from functools import wraps
from asmconstants import SIZE
from asmerrors import error, warn
from asmtokens import tokens

# AST nodes

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


# Grammar

start = 'asm'

precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        )

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

def p_element_declaration_constant(p):
    'element : IDENTIFIER EQU expr'
    name, lineno = p[1], p.lineno(1)
    if name in p.parser.const_table:
        warn("Overriding already defined constant {0}", name, lineno=lineno)
    try:
        p.parser.const_table[name] = eval_expr(p[3], p, lineno)
    except SyntaxError: pass
    pass

def p_element_declaration_variable(p):
    'element : IDENTIFIER RMB NUM'
    name, size, lineno = p[1], p[3], p.lineno(1)
    if name in p.parser.data_table:
        error("Duplicate name definition {0}", name, lineno=lineno, errors=p.parser.errors)
    if size <= 0:
        error("Error in variable declaration {0}: the number of bytes must be greater than zero",
                name, lineno=lineno, errors=p.parser.errors)
    p.parser.data_table[name] = -1
    p.parser.data_table[SIZE] += size

    p[0] = Var(p[1], p[3], lineno)

def p_element_declaration_error(p):
    'element : IDENTIFIER error expr'
    error("Syntax error in declaration {0}", p[1], lineno=p.lineno(1), errors=p.parser.errors)


def p_element_instruction_label(p):
    'element : IDENTIFIER instruction'
    name, size, lineno = p[1], p[2][1], p.lineno(1)
    if name in p.parser.inst_table:
        error("Duplicate label definition: {0}", name, lineno=lineno, errors=p.parser.errors)
    p.parser.inst_table[name] = -1
    p.parser.inst_table[SIZE] += size
    p[0] = Inst(p[1], p[2], p[2][1], p.lineno(1))

def p_element_instruction_label_error(p):
    'element : IDENTIFIER error'
    error("Syntax error in instruction at label {0}", p[1], lineno=p.lineno(1), errors=p.parser.errors)


def p_element_instruction(p):
    'element : instruction'
    p.parser.inst_table[SIZE] += p[1][1]
    p[0] = Inst('', p[1], p[1][1], p.lineno(1))

def p_element_instruction_error(p):
    'element : error'
    error("Syntax error in instruction", lineno=p.lineno(1), errors=p.parser.errors)

def p_element_empty(p):
    'element : '
    pass

## Expressions

def p_expr_num(p):
    '''expr : HEX_NUM
            | NUM'''
    p[0] = ('num', p[1])

def p_expr_const_ref(p):
    'expr : CONST_REF'
    p[0] = ('const', p[1])

def p_expr_paren(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]

def p_expr_arith(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr'''
    p[0] = (p[2], p[1], p[3])

## Instructions

# ABA, ABX
@lineno(1)
def p_instruction_add(p):
    '''instruction : ABA
                   | ABX'''
    p[0] = (p[1], 1)

# ADDD
@lineno(1)
def p_instruction_addd_expr(p):
    'instruction : ADDD expr'
    p[0] = (p[1], 3, 'imm', eval_expr(p[2], p, p.lineno(1)))

@lineno(1)
def p_instruction_addd_var(p):
    'instruction : ADDD IDENTIFIER'
    p[0] = (p[1], 3, 'var', p[2])

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
def p_instruction_compare_expr(p):
    '''instruction : CPK expr
                   | CPX expr'''
    size = 2 if p[1] in {'CPK'} else 3
    p[0] = (p[1], size, 'imm', eval_expr(p[2], p, p.lineno(1)))

# DRCL, DRHLN, DRRCT, DRVLN
@lineno(1)
def p_instruction_draw(p):
    '''instruction : DRCL
                   | DRHLN
                   | DRRCT
                   | DRVLN'''
    p[0] = (p[1], 1)

# DRSYM
@lineno(1)
def p_instruction_draw_symbol(p):
    'instruction : DRSYM CHAR'
    p[0] = (p[1], 2, 'imm', p[2])

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
def p_instruction_load_expr(p):
    '''instruction : LDAA expr
                   | LDAB expr
                   | LDB expr
                   | LDD expr
                   | LDG expr
                   | LDR expr
                   | LDX expr
                   | LDXA expr
                   | LDXB expr
                   | LDYA expr
                   | LDYB expr'''
    size = 2 if p[1] in {'LDAA', 'LDAB', 'LDB', 'LDG', 'LDR'} else 3
    p[0] = (p[1], size, 'imm', eval_expr(p[2], p, p.lineno(1)))

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

# MUL
@lineno(1)
def p_instruction_mul(p):
    'instruction : MUL'
    p[0] = (p[1], 1)

# NEGA
@lineno(1)
def p_instruction_nega(p):
    'instruction : NEGA'
    p[0] = (p[1], 1)

# PSHX, PULX
@lineno(1)
def p_instruction_stack(p):
    '''instruction : PSHX
                   | PULX'''
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

# STAA, STAB, STD, STX
@lineno(1)
def p_instruction_store_ind(p):
    '''instruction : STAA NUM COMMA IX
                   | STAB NUM COMMA IX'''
    p[0] = (p[1], 2, 'ind', p[2], 'x')

@lineno(1)
def p_instruction_store_var(p):
    '''instruction : STAA IDENTIFIER
                   | STAB IDENTIFIER
                   | STD IDENTIFIER
                   | STX IDENTIFIER'''
    p[0] = (p[1], 3, 'var', p[2])

# SUBA
@lineno(1)
def p_instruction_suba_var(p):
    'instruction : SUBA IDENTIFIER'
    p[0] = (p[1], 3, 'var', p[2])

# SUBD
@lineno(1)
def p_instruction_subd_expr(p):
    'instruction : SUBD expr'
    p[0] = (p[1], 3, 'imm', eval_expr(p[2], p, p.lineno(1)))

# TDXA, TDXB, TDYA, TDYB
@lineno(1)
def p_instruction_transfer(p):
    '''instruction : TDXA
                   | TDXB
                   | TDYA
                   | TDYB'''
    p[0] = (p[1], 1)

# XGDX
@lineno(1)
def p_instruction_xgdx(p):
    'instruction : XGDX'
    p[0] = (p[1], 1)

def p_error(t):
    value = t.value if t.value != '\n' else 'NEWLINE'
    error("Syntax error near token {0}", value, lineno=t.lineno)


# Functions to walk the AST

def eval_expr(ast, p, lineno):
    "Returns the value obtained by evaluating an expression."
    expr_type = ast[0]
    if expr_type == 'num':
        return ast[1]
    elif expr_type == 'const':
        name = ast[1]
        if name not in p.parser.const_table:
            error("Undefined constant {0}", name, lineno=lineno, errors=p.parser.errors)
            raise SyntaxError
        return p.parser.const_table[name]
    elif expr_type == '+':
        return eval_expr(ast[1], p, lineno) + eval_expr(ast[2], p, lineno)
    elif expr_type == '-':
        return eval_expr(ast[1], p, lineno) - eval_expr(ast[2], p, lineno)
    elif expr_type == '*':
        return eval_expr(ast[1], p, lineno) * eval_expr(ast[2], p, lineno)
    elif expr_type == '/':
        return eval_expr(ast[1], p, lineno) / eval_expr(ast[2], p, lineno)
