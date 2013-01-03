# Assembly language quick overview

The assembly language is very simple for now:

* Subset of the 68HC11 instructions.
* New instructions for 2D drawing.
* Syntax for data segment elements.
* Simple macros for constants.

For a full description of the grammar, see `asmgrammar.py`.

## Instructions

The basic form of an instruction is:

```
<instruction> ::= <identifier> mnemonic <arguments>
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
<variable> ::= <identifier> RMB <size>
```

Where *size* is the number of bytes.

For example:

``` asm
VAR1   RMB   2
VAR2   RMB   1
```

*Variables* can be used as arguments to instructions and they'll be
replaced by their memory address:

``` asm
       LDX  VAR1
```

## Constants

*Constants* are simply replaced by their value when they're used as arguments
to instructions. They are declared like this:

```
<constant> ::= <identifier> EQU <expr>

<expr> ::= HEX_NUM
       |   NUM
       |   CONST_REF
       |   '(' <expr> ')'
       |   <expr> '+' <expr>
       |   <expr> '-' <expr>
       |   <expr> '*' <expr>
       |   <expr> '/' <expr>
```

So constants can be numeric values (in decimal or hexadecimal format),
references to previously defined constants, and simple arithmetic expressions.

For example:

``` asm
WIDTH   EQU   $00B3
HEIGHT  EQU   480
MIDDLE  EQU   #WIDTH / 2
```

To reference a constant, add a '#' before it's identifier:

``` asm
        LDX   #WIDTH
```
