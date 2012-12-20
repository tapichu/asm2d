# Assembler for the 68112D microprocessor

The 68112D is a clone of the 68HC11 microcontroller, with extra instructions
to generate 2D graphics on a VGA display.

The **asm2d** assembler turns the assembly code into VHDL code to synthesise
a memory using an array of 8 bit vectors.

## Installation

Using pip:

``` bash
pip install asm2d
```

### For development

``` bash
python setup.py develop
```

## Running

Compile a file:

``` bash
asm2d source.s
```

The default output file will have the same name as the source file, but with
a `.vhd` extension. You can change this with the `-o` flag:

```
asm2d source.s -o memory.vhd
```

### Help

``` bash
asm2d -h
```
