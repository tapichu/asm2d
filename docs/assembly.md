# Assembly language quick overview

The assembly language is very simple for now:

* Subset of the 68HC11 instructions.
* New instructions for 2D drawing.
* Syntax for data segment elements.
* Very basic macros for constants.

For a full description of the grammar, see `asmgrammar.py`.

## Instructions

The basic form of an instruction is:

```
<instruction> ::= <label> mnemonic <arguments>
              |   mnemonic <arguments>
```

For example:

``` asm
LABEL   LDX   $00FA
        ABX
```

### Main

The first instruction must start with the label `.main` (variables and
constants may appear before this).

This will be the entry point of the program (mapped to the 0 address).

## Data

*Variables* in the data section are declared like this:

```
<variable> ::= <name> VAR <size>
```

Where *size* is the number of bytes.

For example:

``` asm
VAR1   VAR   2
VAR2   VAR   1
```

*Variables* can be used as arguments to instructions and they will be
replaced by their memory address:

``` asm
     LDX  VAR1
```

## Constants

*Constants* are simply replaced by their value when they're used as arguments
to instructions. They are declared like this:

```
<constant> ::= .<name> CONST <value>
```

For example:

``` asm
.WIDTH   CONST   $00B3
```
