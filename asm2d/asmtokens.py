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
        'CLRS',             # Clear screen
        'CONST',            # Constant declaration
        'CONST_IDENTIFIER', # .FPS
        'CPK',              # Compare game clock
        'CPX',              # Compare register X
        'DRCL',             # Draw circle
        'DRHLN',            # Draw horizontal line
        'DRRCT',            # Draw rectangle
        'DRVLN',            # Draw vertical line
        'ENDL',             # Newline
        'HEX_NUM',          # $F0
        'IDENTIFIER',       # FPS_LOOP
        'INX',              # Increment register X
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
        'RSTK',             # Reset the game clock
        'RTS',              # Return from subroutine
        'STAA',             # Store accumulator A
        'STAB',             # Store accumulator B
        'STD',              # Store accumulator D
        'STX',              # Store register X
        'SUBD',             # Subtract from double acc D
        'TDXA',             # Transfer to game register XA
        'TDYA',             # Transfer to game register YA
        'VAR'               # Variable declaration
        )

states = ()

def t_eolcomment(t):
    r'(\#|;).*'
    pass

def t_CONST_IDENTIFIER(t):
    r'\.[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    if t.value == '.MAIN':
        t.type = "IDENTIFIER"
        t.value = '.main'
    return t

reserved = set(tokens) - {'CONST_IDENTIFIER', 'ENDL', 'HEX_NUM', 'IDENTIFIER', 'NUM'}

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
