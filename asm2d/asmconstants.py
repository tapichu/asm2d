from bitstring import BitArray

SIZE = '___SIZE___'

# http://home.earthlink.net/~tdickens/68hc11/68hc11_opcode_map.html

OP_CODES = {
        'ABA': 0x1B,
        'ABX': 0x3A,
        'ADDD': {'imm': 0xC3, 'ext': 0xF3},
        'ASRD': 0x87,           # Unused opcode (in 8611)
        'BCS': 0x25,
        'BEQ': 0x27,
        'BHI': 0x22,
        'BKE': 0xB5,            # Shadows BITA
        'BLO': 0x25,
        'BMI': 0x2B,
        'BNE': 0x26,
        'BPL': 0x2A,
        'BRA': 0x20,
        'CLRS': 0x95,           # Shadows BITA
        'CPK': {'imm': 0x85},   # Shadows BITA
        'CPX': {'imm': 0x8C, 'ext': 0xBC},
        'DRCL': 0x65,           # Unused opcode (in 6811)
        'DRHLN': 0x6B,          # Unused opcode (in 6811)
        'DRRCT': 0x75,          # Unused opcode (in 6811)
        'DRSYM': {'imm': 0xA5}, # Shadows BITA
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
        'PSHA': 0x36,
        'PSHB': 0x37,
        'PSHCB': 0x88,          # Shadows EORA
        'PSHCG': 0x98,          # Shadows EORA
        'PSHCR': 0xA8,          # Shadows EORA
        'PSHX': 0x3C,
        'PSHXA': 0xB8,          # Shadows EORA
        'PSHXB': 0xC8,          # Shadows EORB
        'PSHYA': 0xD8,          # Shadows EORB
        'PSHYB': 0xE8,          # Shadows EORB
        'PULA': 0x32,
        'PULB': 0x33,
        'PULCB': 0x8A,          # Shadows ORAA
        'PULCG': 0x9A,          # Shadows ORAA
        'PULCR': 0xAA,          # Shadows ORAA
        'PULX': 0x38,
        'PULXA': 0xBA,          # Shadows ORAA
        'PULXB': 0xCA,          # Shadows ORAB
        'PULYA': 0xDA,          # Shadows ORAB
        'PULYB': 0xEA,          # Shadows ORAB
        'RNDA': {'imm': 0xFA},  # Shadows ORAB
        'RSTK': 0xC7,           # Unused opcode (in 6811)
        'RTS': 0x39,
        'STAA': {'ext': 0xB7, 'ind': 0xA7},
        'STAB': {'ext': 0xF7, 'ind': 0xE7},
        'STD': {'ext': 0xFD},
        'STX': {'ext': 0xFF},
        'SUBA': {'imm': 0x80, 'ext': 0xB0},
        'SUBD': {'imm': 0x83, 'ext': 0xB3},
        'TDX': 0xF8,            # Shadows EORB
        'TDXA': 0xC5,           # Shadows BITB
        'TDXB': 0xD5,           # Shadows BITB
        'TDYA': 0xE5,           # Shadows BITB
        'TDYB': 0xF5,           # Shadows BITB
        'XGDX': 0x8F
        }

# Extended instructions that operate on one byte
ONE_BYTE_INST = {'LDAA', 'LDAB', 'LDB', 'LDG', 'LDR', 'STAA', 'STAB', 'SUBA'}

# Opcodes for graphic unit
SYM_TABLE = {k:BitArray(int=v, length=8).hex.upper()
        for k,v in zip('@# ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,;:&|?!<^', range(5, 56))}

# Opcodes for key press events
KEY_TABLE = {k:BitArray(int=v, length=8).hex.upper()
        for k,v in zip(range(0, 16), range(7, 23))}
