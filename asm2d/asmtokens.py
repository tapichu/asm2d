# This is a set of regular expressions defining a lexer for the 68112D
# microprocessor.

from __future__ import print_function
from bitstring import BitArray
from asmerrors import error

tokens = (
        'ABA',              # Add accumulator B to accumulator A
        'ABX',              # Add accumulator B to register X
        'ADDD',             # Add to accumulator D
        'ASRD',             # Arithmetic shift right D
        'BCS',              # Branch if carry set (same as BLO)
        'BEQ',              # Branch equal zero
        'BHI',              # Branch if higher
        'BKE',              # Branch if key event
        'BLO',              # Branch if lower
        'BNE',              # Branch not equal zero
        'BRA',              # Branch always
        'CHAR',             # 'A', '1', etc.
        'CLRS',             # Clear screen
        'COMMA',            # ,
        'CONST_REF',        # #CONSTANT
        'CPK',              # Compare game clock
        'CPX',              # Compare register X
        'DIVIDE',           # /
        'DRCL',             # Draw circle
        'DRHLN',            # Draw horizontal line
        'DRRCT',            # Draw rectangle
        'DRSYM',            # Draw symbol
        'DRVLN',            # Draw vertical line
        'ENDL',             # Newline
        'EQU',              # Equate symbol to a value
        'HEX_NUM',          # $F0
        'IDENTIFIER',       # FPS_LOOP
        'INX',              # Increment register X
        'IX',               # Index Register X
        'JSR',              # Jump to subroutine
        'KEY_ID',           # KEY_0 throught KEY_15
        'LDAA',             # Load accumulator A
        'LDAB',             # Load accumulator B
        'LDB',              # Load colour blue
        'LDD',              # Load double acc D
        'LDG',              # Load colour green
        'LDR',              # Load colour red
        'LDX',              # Load register X
        'LDXA',             # Load game register XA
        'LDXB',             # Load game register XB
        'LDYA',             # Load game register YA
        'LDYB',             # Load game register YB
        'LPAREN',           # (
        'MINUS',            # -
        'MUL',              # Multiply unsigned (AccD = AccA x AccB)
        'NEGA',             # 2's complement acc A
        'NUM',              # 10, 35, etc.
        'PLUS',             # +
        'PSHA',             # Push accumulator A onto stack
        'PSHB',             # Push accumulator B onto stack
        'PSHCB',            # Push colour blue onto stack
        'PSHCG',            # Push colour green onto stack
        'PSHCR',            # Push colour red onto stack
        'PSHX',             # Push index register X onto stack
        'PSHXA',            # Push game register XA onto stack
        'PSHXB',            # Push game register XB onto stack
        'PSHYA',            # Push game register YA onto stack
        'PSHYB',            # Push game register YB onto stack
        'PULA',             # Pull accumulator A from stack
        'PULB',             # Pull accumulator B from stack
        'PULCB',            # Pull colour blue from stack
        'PULCG',            # Pull colour green from stack
        'PULCR',            # Pull colour red from stack
        'PULX',             # Pull index register X from stack
        'PULXA',            # Pull game register XA from stack
        'PULXB',            # Pull game register XB from stack
        'PULYA',            # Pull game register YA from stack
        'PULYB',            # Pull game register YB from stack
        'RMB',              # Reserve memory bytes
        'RPAREN',           # )
        'RSTK',             # Reset the game clock
        'RTS',              # Return from subroutine
        'STAA',             # Store accumulator A
        'STAB',             # Store accumulator B
        'STD',              # Store accumulator D
        'STX',              # Store register X
        'SUBA',             # Subtract from accumulator A
        'SUBD',             # Subtract from double acc D
        'TIMES',            # *
        'TDX',              # Transfer double acc D to index register X
        'TDXA',             # Transfer double acc D to game register XA
        'TDXB',             # Transfer double acc D to game register XB
        'TDYA',             # Transfer double acc D to game register YA
        'TDYB',             # Transfer double acc D to game register YB
        'XGDX'              # Exchange double acc D and register X
        )

states = ()

def t_eolcomment(t):
    r';.*'
    pass

t_COMMA = r','
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_MINUS = r'\-'
t_PLUS = r'\+'
t_RPAREN = r'\)'
t_TIMES = r'\*'

def t_CHAR(t):
    r"'[A-Z0-9.,;:&?!|#@<^]'"
    t.value = t.value[1]
    return t

def t_IX(t):
    r'x|X'
    return t

def t_CONST_REF(t):
    r'\#[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value[1:].upper()
    return t

def t_MAIN(t):
    r'\.main|\.MAIN'
    t.type = "IDENTIFIER"
    t.value = '.main'
    return t

reserved = set(tokens) - {'CHAR', 'COMMA', 'CONST_REF', 'DIVIDE', 'ENDL',\
        'HEX_NUM', 'IDENTIFIER', 'IX', 'KEY_ID', 'LPAREN', 'MINUS', 'NUM',\
        'PLUS', 'RPAREN', 'TIMES'}

def t_KEY_ID(t):
    r'(key|KEY)_(1[0-5]|[0-9])'
    t.value = int(t.value.split('_')[1])
    return t

def t_IDENTIFIER(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    if t.value in reserved:
        t.type = t.value
    return t

def t_HEX_NUM(t):
    r'\$([0-9a-fA-F])+'
    t.value = BitArray(hex="0x" + t.value[1:]).int
    return t

def t_NUM(t):
    r'(0)|(-?[1-9][0-9]*)'
    t.value = int(t.value)
    return t

# Whitespace
t_ignore = ' \t\v\r'

def t_ENDL(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(t):
    error("Illegal character '{0}'", t.value[0], errors=t.lexer.errors, lineno=t.lexer.lineno)
    t.lexer.skip(1)
