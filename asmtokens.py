# This is a set of regular expressions defining a lexer for our 68HC11 clone.

tokens = (
        'BEQ',              # Branch equal zero
        'BNE',              # Branch not equal zero
        'BRA',              # Branch always
        'CLRS',             # Clear screen
        'CONST',            # Constant declaration
        'CONST_IDENTIFIER', # .FPS
        'CPK',              # Compare game clock
        'DRHLN',            # Draw horizontal line
        'DRRCT',            # Draw rectangle
        'DRVLN',            # Draw vertical line
        'HEX_NUM',          # $F0
        'IDENTIFIER',       # FPS_LOOP
        'JSR',              # Jump to subroutine
        'LDB',              # Load colour blue
        'LDD',              # Load double acc D
        'LDG',              # Load colour green
        'LDK',              # Load game clock
        'LDR',              # Load colour red
        'LDX',              # Load register X
        'LDXA',             # Load game register XA
        'LDXB',             # Load game register XB
        'LDYA',             # Load game register YA
        'MAIN',             # .main
        'RTS',              # Return from subroutine
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

t_MAIN = r'\.(main|MAIN)'

def t_CONST_IDENTIFIER(t):
    r'\.[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    return t

reserved = ['BEQ', 'BNE', 'BRA', 'CLRS', 'CONST', 'CPK', 'DRHLN', 'DRRCT', \
        'DRVLN', 'JSR', 'LDB', 'LDD', 'LDG', 'LDK', 'LDR', 'LDX', 'LDXA', \
        'LDXB', 'LDYA', 'RTS', 'STX', 'SUBD', 'TDXA', 'TDYA', 'VAR']

def t_IDENTIFIER(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.value = t.value.upper()
    if t.value in reserved:
        t.type = t.value
    return t

def t_HEX_NUM(t):
    r'\$([0-9a-fA-F])+'
    t.value = int(t.value[1:], 16)
    return t

# Whitespace
t_ignore = ' \t\v\r'

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

def t_error(t):
    print "ASM 68HC11 Lexer: Illegal character", t.value[0]
    t.lexer.skip(1)
