# VHDL code gen: generates the memory contents.

from __future__ import print_function
import sys
from bitstring import BitArray
from asmgrammar import Inst, Var

_var_name = 'memory'
_file = sys.stdout

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
        'STAA': {'ext': 0xB7},
        'STAB': {'ext': 0xF7},
        'STD': {'ext': 0xFD},
        'STX': {'ext': 0xFF},
        'SUBA': {'ext': 0xB0},
        'SUBD': {'imm': 0x83},
        'TDXA': 0xA5,           # Shadows BITA
        'TDYA': 0xB5,           # Shadows BITA
        'XGDX': 0x8F
        }

def codegen(ast, data_table, inst_table, var_name='memory', outfile=sys.stdout):
    "Generate the memory content as a VHDL matrix."
    global _var_name, _file
    _var_name = var_name
    _file = outfile
    data_offset = inst_table['__SIZE']
    code_offset = 0

    for elem in ast:
        if isinstance(elem, Var):
            codegen_data(elem, data_offset)
            data_offset += elem.size
        elif isinstance(elem, Inst):
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
    if inst_name in {'LDB', 'LDG', 'LDR'}:
        data = BitArray(uint=value, length=(elem.size-1)*8).hex.upper()
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

def output_opcode(inst_name, label, addr, code=None):
    "Output the memory contents of an instruction op code (1 byte)."
    code = OP_CODES[inst_name] if code is None else code
    op_code = BitArray(uint=code, length=8).hex.upper()
    output = '{0}({1:d}) := X"{2}";    -- {3}'.format(_var_name, addr, op_code, inst_name)
    if label != '':
        output += " ({0})".format(label)
    print(output, file=_file)

def output_data(data, addr, comment=None):
    "Output the memory contents of a byte of data."
    output = '{0}({1:d}) := X"{2}";'.format(_var_name, addr, data)
    if comment is not None and comment != '':
        output += '    -- {0}'.format(comment)
    print(output, file=_file)
