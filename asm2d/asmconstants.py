from bitstring import BitArray

SIZE = '__SIZE'

# http://home.earthlink.net/~tdickens/68hc11/68hc11_opcode_map.html

OP_CODES = {
        'ABA': 0x1B,
        'ABX': 0x3A,
        'ADDD': {'imm': 0xC3, 'ext': 0xF3},
        'ASRD': 0x87,           # Unused opcode (in 8611)
        'BCS': 0x25,
        'BEQ': 0x27,
        'BHI': 0x22,
        'BLO': 0x25,
        'BNE': 0x26,
        'BRA': 0x20,
        'CLRS': 0x95,           # Shadows BITA
        'CPK': {'imm': 0x85},   # Shadows BITA
        'CPX': {'imm': 0x8C},
        'DRCL': 0x65,           # Unused opcode (in 6811)
        'DRHLN': 0x6B,          # Unused opcode (in 6811)
        'DRRCT': 0x75,          # Unused opcode (in 6811)
        'DRSYM': {'imm': 0xC5}, # Shadows BITB
        'DRVLN': 0x7B,          # Unused opcode (in 6811)
        'INX': 0x08,
        'JSR': 0xBD,
        'LDAA': {'imm': 0x86, 'ext': 0xB6},
        'LDAB': {'imm': 0xC6, 'ext': 0xF6},
        'LDB': {'imm': 0x41, 'ext': 0x51},      # Unused opcodes (in 6811)
        'LDD': {'imm': 0xCC, 'ext': 0xFC},
        'LDG': {'imm': 0x42, 'ext': 0x52},      # Unused opcodes (in 6811)
        'LDR': {'imm': 0x45, 'ext': 0x55},      # Unused opcodes (in 6811)
        'LDX': {'imm': 0xCE, 'ext': 0xFE},
        'LDXA': {'imm': 0x4B, 'ext': 0x5B},     # Unused opcodes (in 6811)
        'LDXB': {'imm': 0x4E, 'ext': 0x5E},     # Unused opcodes (in 6811)
        'LDYA': {'imm': 0x61, 'ext': 0x71},     # Unused opcodes (in 6811)
        'LDYB': {'imm': 0x62, 'ext': 0x72},     # Unused opcodes (in 6811)
        'MUL': 0x3D,
        'NEGA': 0x40,
        'RSTK': 0xC7,           # Unused opcode (in 6811)
        'RTS': 0x39,
        'STAA': {'ext': 0xB7, 'ind': 0xA7},
        'STAB': {'ext': 0xF7, 'ind': 0xE7},
        'STD': {'ext': 0xFD},
        'STX': {'ext': 0xFF},
        'SUBA': {'ext': 0xB0},
        'SUBD': {'imm': 0x83},
        'TDXA': 0xA5,           # Shadows BITA
        'TDYA': 0xB5,           # Shadows BITA
        'XGDX': 0x8F
        }

SYM_TABLE = {k:BitArray(int=v, length=8).hex.upper()
        for k,v in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', range(8, 44))}
SYM_TABLE['@'] = '05'
SYM_TABLE['#'] = '06'
