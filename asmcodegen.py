# VHDL code gen: generates the memory contents.

from asmgrammar import Const, Inst, Var
from bitstring import BitArray

OP_CODES = {
        'ABX': 0x3A,
        'ADDD': {'imm': 0xC3, 'ext': 0xF3},
        'ASRD': 0x87,       # TODO: does not exist
        'BEQ': 0x27,
        'BHI': 0x22,
        'BLO': 0x25,
        'BNE': 0x26,
        'BRA': 0x20,
        'CLRS': 0x00,       # TODO: assign
        'CPK': 0x00,        # TODO: assign
        'CPX': 0x8C,
        'DRCL': 0x00,       # TODO: assign
        'DRHLN': 0x00,      # TODO: assign
        'DRRCT': 0x00,      # TODO: assign
        'DRVLN': 0x00,      # TODO: assign
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
        'STAA': 0xB7,
        'STAB': 0xF7,
        'STD': 0xFD,
        'STX': 0xFF,
        'SUBD': 0x83,
        'TDXA': 0x00,       # TODO: assign
        'TDYA': 0x00        # TODO: assign
        }

# memoria(0) := "11111111";

def codegen(ast, data_table, inst_table, matrix_name="memory"):
    "Generate the memory content as a VHDL matrix."
    data_offset = inst_table['__SIZE']
    code_offset = 0

    for elem in ast:
        if isinstance(elem, Var):
            value = BitArray(int=0, length=elem.size*8).bin
            for i in range(elem.size):
                start, end = i*8, (i+1)*8-1
                print 'memory(%d) := "%s";    // %s' % (data_offset, value[start:end], elem.id)
                data_offset += 1
        elif isinstance(elem, Inst):
            if len(elem.inst) == 2:
                code = BitArray(uint=OP_CODES[elem.inst[0]], length=8)
                if elem.label != '':
                    print 'memory(%d) := "%s";    // %s (%s)' % (code_offset, code.bin, elem.inst[0], elem.label)
                else:
                    print 'memory(%d) := "%s";    // %s' % (code_offset, code.bin, elem.inst[0])
                code_offset += 1
            elif len(elem.inst) == 3:
                # TODO
                pass
            elif len(elem.inst) == 4:
                # TODO
                pass
