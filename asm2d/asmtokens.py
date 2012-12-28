# This is a set of regular expressions defining a lexer for our 68HC11 clone.

from __future__ import print_function
import sys
from bitstring import BitArray

tokens = (
        'ABA',              # Add accumulator B to accumulator A
        'ABX',              # Add accumulator B to register X
        'ADDD',             # Add to accumulator D
        'ASRD',             # Arithmetic shift right D
        'BCS',              # Branch if carry set (same as BLO)
        'BEQ',              # Branch equal zero
        'BHI',              # Branch if higher
        'BLO',              # Branch if lower
        'BNE',              # Branch not equal zero
        'BRA',              # Branch always
        'CHAR',             # 'A', '1', etc.
        'CLRS',             # Clear screen
        'COMMA',            # ,
        'CONST_REF',        # #CONSTANT
        'CPK',              # Compare game clock
        'CPX',              # Compare register X
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
        'MUL',              # Multiply unsigned (AccD = AccA x AccB)
        'NEGA',             # 2's complement acc A
        'NUM',              # 10, 35, etc.
        'RMB',              # Reserve memory bytes
        'RSTK',             # Reset the game clock
        'RTS',              # Return from subroutine
        'STAA',             # Store accumulator A
        'STAB',             # Store accumulator B
        'STD',              # Store accumulator D
        'STX',              # Store register X
        'SUBA',             # Subtract from accumulator A
        'SUBD',             # Subtract from double acc D
        'TDXA',             # Transfer double acc D to game register XA
        'TDYA',             # Transfer double acc D to game register YA
        'XGDX'              # Exchange double acc D and register X
        )

states = ()

def t_eolcomment(t):
    r';.*'
    pass

t_COMMA = r','

def t_CHAR(t):
    r"'[A-Z0-9#@]'"
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

reserved = set(tokens) - {'CHAR', 'COMMA', 'CONST_REF', 'ENDL', 'HEX_NUM',\
        'IDENTIFIER', 'IX', 'NUM'}

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
    r'[0-9]+'
    t.value = int(t.value)
    return t

# Whitespace
t_ignore = ' \t\v\r'

def t_ENDL(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(t):
    print("ERROR: Illegal character '{0}' (at line: {1:d})"\
            .format(t.value[0], t.lexer.lineno), file=sys.stderr)
    t.lexer.skip(1)
