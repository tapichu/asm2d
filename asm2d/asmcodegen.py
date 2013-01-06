# Outputs the memory contents in .mif (Memory Initialization File) format.

from __future__ import print_function
import math
import sys
from bitstring import BitArray
from asmconstants import KEY_TABLE, OP_CODES, SIZE, SYM_TABLE
from asmgrammar import Inst, Var

_file = sys.stdout
_addr_bits = 0

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
                inst_type = elem.inst[2]
                if inst_type == 'ind':
                    codegen_indexed(elem, code_offset)
                elif inst_type == 'imm-rel':
                    codegen_immediate_relative(elem, code_offset, inst_table)
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

def codegen_immediate_relative(elem, addr, inst_table):
    """Output the memory contents of an immediate and relative instruction
    like BKE (3 bytes).
    """
    inst_name, _, _, key, label = elem.inst
    output_opcode(inst_name, elem.label, addr)

    addr += 1
    data = KEY_TABLE[key]
    output_data(data, addr, comment="KEY_{0:d}".format(key))

    addr += 1
    relative_addr = inst_table[label].addr - (addr + 1)
    data = BitArray(int=relative_addr, length=8).hex.upper()
    output_data(data, addr, comment="{0} (rel {1:d})".format(label, relative_addr))

def codegen_relative(elem, addr, inst_table):
    "Output the memory contents of a relative instruction (2 bytes)."
    inst_name, _, label = elem.inst
    output_opcode(inst_name, elem.label, addr)

    addr += 1
    relative_addr = inst_table[label].addr - (addr + 1)
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
        next_addr = inst_table[label].addr
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
