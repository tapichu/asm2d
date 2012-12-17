# This is a set of regular expressions defining a lexer for our 68HC11 clone.

from bitstring import BitArray

tokens = (
        'ABX',              # Add accumulator B to register X
        'ADDD',             # Add to accumulator D
        'ASRD',             # Arithmetic shift right D
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
        'JSR',              # Jump to subroutine
        'LDAA',             # Load accumulator A
        'LDAB',             # Load accumulator B
        'LDB',              # Load colour blue
        'LDD',              # Load double acc D
        'LDG',              # Load colour green
        'LDK',              # Load game clock
        'LDR',              # Load colour red
        'LDX',              # Load register X
        'LDXA',             # Load game register XA
        'LDXB',             # Load game register XB
        'LDYA',             # Load game register YA
        'LDYB',             # Load game register YB
        'MAIN',             # .main
        'NEGA',             # 2's complement acc A
        'NUM',              # 10, 35, etc.
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

def t_MAIN(t):
    r'\.(?:main|MAIN)'
    return t

def t_CONST_IDENTIFIER(t):
    r'\.[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    return t

reserved = [
        'ABX', 'ADDD', 'ASRD', 'BEQ', 'BHI', 'BLO', 'BNE', 'BRA', 'CLRS',
        'CONST', 'CPK', 'CPX', 'DRCL', 'DRHLN', 'DRRCT', 'DRVLN', 'JSR', 'LDAA',
        'LDAB', 'LDB', 'LDD', 'LDG', 'LDK', 'LDR', 'LDX', 'LDXA', 'LDXB',
        'LDYA', 'LDYB', 'NEGA', 'RTS', 'STAA', 'STAB', 'STD', 'STX', 'SUBD',
        'TDXA', 'TDYA', 'VAR'
        ]

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
    print "ASM 68HC11 Lexer: Illegal character", t.value[0]
    t.lexer.skip(1)
