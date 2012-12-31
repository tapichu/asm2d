# Outputs the memory contents in .mif (Memory Initialization File) format.

from __future__ import print_function
import math
import sys
from bitstring import BitArray
from asmgrammar import Inst, Var

_file = sys.stdout
_addr_bits = 0
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

def codegen(ast, data_table, inst_table, no_words=None, outfile=sys.stdout):
    "Generate the memory content as a VHDL matrix."
    global _file
    _file = outfile
    mem_size = inst_table[SIZE] + data_table[SIZE]
    data_offset = inst_table[SIZE]
    code_offset = 0

    if not no_words: no_words = mem_size
    calculate_addr_bits(no_words)

    output_mif_header(no_words)

    for elem in ast:
        if isinstance(elem, Inst):
            if len(elem.inst) == 2:
                codegen_inherent(elem, code_offset)
                code_offset += elem.size
            elif len(elem.inst) == 3:
                if elem.size == 2:
                    codegen_relative(elem, code_offset, inst_table)
                elif elem.size == 3:
                    codegen_extended(elem, code_offset, inst_table)
                code_offset += elem.size
            elif len(elem.inst) == 4:
                inst_type = elem.inst[2]
                if inst_type == 'imm':
                    codegen_immediate(elem, code_offset)
                elif inst_type == 'ext':
                    codegen_extended(elem, code_offset, inst_table)
                code_offset += elem.size
            elif len(elem.inst) == 5:
                codegen_indexed(elem, code_offset)
                code_offset += elem.size

    for elem in ast:
        if isinstance(elem, Var):
            codegen_data(elem, data_offset)
            data_offset += elem.size

    output_mif_footer(no_words, mem_size, data_offset)

def codegen_data(elem, addr, default_value=0):
    "Output the initial value of a variable in the data segment."
    value = BitArray(int=default_value, length=elem.size*8).hex.upper()
    for i in range(elem.size):
        start, end = i*2, (i+1)*2
        output_data(value[start:end], addr, comment=elem.id)
        addr += 1

def codegen_inherent(elem, addr):
    "Output the memory contents of an inherent instruction (1 byte)."
    output_opcode(elem.inst[0], elem.label, addr)

def codegen_immediate(elem, addr):
    "Output the memory contents of an immediate instruction (2 or 3 bytes)."
    inst_name, _, inst_type, value = elem.inst
    opcode = OP_CODES[inst_name][inst_type]
    output_opcode(inst_name, elem.label, addr, code=opcode)

    addr += 1
    if inst_name in {'CPK', 'LDB', 'LDG', 'LDR'}:
        data = BitArray(uint=value, length=(elem.size-1)*8).hex.upper()
    elif inst_name == 'DRSYM':
        data = SYM_TABLE[value]
    else:
        data = BitArray(int=value, length=(elem.size-1)*8).hex.upper()
    for i in range(elem.size-1):
        start, end = i*2, (i+1)*2
        output_data(data[start:end], addr, comment=value)
        addr += 1

def codegen_relative(elem, addr, inst_table):
    "Output the memory contents of a relative instruction (2 bytes)."
    inst_name, _, label = elem.inst
    output_opcode(inst_name, elem.label, addr)

    addr += 1
    relative_addr = inst_table[label] - (addr + 1)
    data = BitArray(int=relative_addr, length=8).hex.upper()
    output_data(data, addr, comment="{0} (rel {1:d})".format(label, relative_addr))

def codegen_indexed(elem, addr):
    "Output the memory contents of an indexed instruction (2 bytes)."
    inst_name, _, inst_type, offset, register = elem.inst
    opcode = OP_CODES[inst_name][inst_type]
    output_opcode(inst_name, elem.label, addr, code=opcode)

    addr += 1
    data = BitArray(int=offset, length=8).hex.upper()
    output_data(data, addr, comment="{0:d},{1}".format(offset, register.upper()))

def codegen_extended(elem, addr, inst_table):
    "Output the memory contents of an extended instruction (3 bytes)."
    if len(elem.inst) == 3:
        inst_name, _, label = elem.inst
        next_addr = inst_table[label]
        data = BitArray(uint=next_addr, length=16).hex.upper()
        output_opcode(inst_name, elem.label, addr)

        addr += 1
        output_data(data[:2], addr, comment="{0} (abs {1:d})".format(label, next_addr))
        output_data(data[2:], addr+1, comment="{0} (abs {1:d})".format(label, next_addr))
    elif len(elem.inst) == 4:
        inst_name, _, inst_type, value = elem.inst
        data = BitArray(uint=value, length=16).hex.upper()
        opcode = OP_CODES[inst_name][inst_type]
        output_opcode(inst_name, elem.label, addr, code=opcode)

        addr += 1
        output_data(data[:2], addr, comment=value)
        output_data(data[2:], addr+1, comment=value)

# Helper functions

def calculate_addr_bits(depth):
    """Calculate the number of bits (in multiples of 4) needed to address the
    specified number of words.
    """
    global _addr_bits
    _addr_bits = int(math.ceil(math.log(depth, 2) / 4)) * 4

def output_opcode(inst_name, label, addr, code=None):
    "Output the memory contents of an instruction op code (1 byte)."
    code = OP_CODES[inst_name] if code is None else code
    op_code = BitArray(uint=code, length=8).hex.upper()
    addr_hex = BitArray(uint=addr, length=_addr_bits).hex.upper()
    output = '{0} : {1};    -- {2}'.format(addr_hex, op_code, inst_name)
    if label != '':
        output += " ({0})".format(label)
    print(output, file=_file)

def output_data(data, addr, comment=None):
    "Output the memory contents of a byte of data."
    addr_hex = BitArray(uint=addr, length=_addr_bits).hex.upper()
    output = '{0} : {1};'.format(addr_hex, data)
    if comment is not None and comment != '':
        output += '    -- {0}'.format(comment)
    print(output, file=_file)

def output_mif_header(depth, width=8, addr_radix='HEX', data_radix='HEX'):
    "Output the header of a MIF file."
    print('DEPTH = {0:d};\t\t\t-- Size of memory in words'.format(depth), file=_file)
    print('WIDTH = {0:d};\t\t\t\t-- Size of word in bits'.format(width), file=_file)
    print('ADDRESS_RADIX = {0};\t-- Radix for address values'.format(addr_radix), file=_file)
    print('DATA_RADIX = {0};\t\t-- Radix for data values'.format(data_radix), file=_file)
    print('CONTENT', file=_file)
    print('BEGIN\n', file=_file)

def output_mif_footer(depth, mem_size, next_addr):
    "Output the footer of a MIF file."
    if depth > mem_size:
        start_addr = BitArray(uint=next_addr, length=_addr_bits).hex.upper()
        end_addr = BitArray(uint=depth-1, length=_addr_bits).hex.upper()
        print('\n[{0}..{1}] : {2};'.format(start_addr, end_addr, '00'), file=_file)
    print('\nEND;', file=_file)
