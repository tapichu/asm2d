# VHDL code gen: generates the memory contents.

from __future__ import print_function
import sys
from bitstring import BitArray
from asmgrammar import Inst, Var

_var_name = 'memory'
_file = sys.stdout

OP_CODES = {
        'ABX': 0x3A,
        'ADDD': {'imm': 0xC3, 'ext': 0xF3},
        'ASRD': 0x87,           # TODO: does not exist
        'BEQ': 0x27,
        'BHI': 0x22,
        'BLO': 0x25,
        'BNE': 0x26,
        'BRA': 0x20,
        'CLRS': 0x00,           # TODO: assign
        'CPK': {'imm': 0x00},   # TODO: assign
        'CPX': {'imm': 0x8C},
        'DRCL': 0x00,           # TODO: assign
        'DRHLN': 0x00,          # TODO: assign
        'DRRCT': 0x00,          # TODO: assign
        'DRVLN': 0x00,          # TODO: assign
        'JSR': 0xBD,
        'LDAA': {'imm': 0x86, 'ext': 0xB6},
        'LDAB': {'imm': 0xC6, 'ext': 0xF6},
        'LDB': {'imm': 0x00, 'ext': 0x00},  # TODO: assign
        'LDD': {'imm': 0xCC, 'ext': 0xFC},
        'LDG': {'imm': 0x00, 'ext': 0x00},  # TODO: assign
        'LDK': {'imm': 0x00, 'ext': 0x00},  # TODO: assign
        'LDR': {'imm': 0x00, 'ext': 0x00},  # TODO: assign
        'LDX': {'imm': 0xCE, 'ext': 0xFE},
        'LDXA': {'imm': 0x00, 'ext': 0x00}, # TODO: assign
        'LDXB': {'imm': 0x00, 'ext': 0x00}, # TODO: assign
        'LDYA': {'imm': 0x00, 'ext': 0x00}, # TODO: assign
        'LDYB': {'imm': 0x00, 'ext': 0x00}, # TODO: assign
        'NEGA': 0x40,
        'RTS': 0x39,
        'STAA': {'ext': 0xB7},
        'STAB': {'ext': 0xF7},
        'STD': {'ext': 0xFD},
        'STX': {'ext': 0xFF},
        'SUBD': {'imm': 0x83},
        'TDXA': 0x00,       # TODO: assign
        'TDYA': 0x00        # TODO: assign
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
