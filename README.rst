Assembler for the 68112D microprocessor
=======================================

The 68112D is a clone of the 68HC11 microcontroller, with extra instructions
to generate 2D graphics on a VGA display.

The **asm2d** assembler turns the assembly code into an MIF file (Memory
Initialization File) that can be used to initialize a memory block during
compilation and/or simulation.

Installation
------------

Using pip:

.. code:: bash

    pip install asm2d

For development
~~~~~~~~~~~~~~~

.. code:: bash

    python setup.py develop

Running
-------

Compile a file:

.. code:: bash

    asm2d source.s2d

The default output file will have the same name as the source file, but with
a ``.mif`` extension. You can change this with the ``-o`` flag:

.. code:: bash

    asm2d source.s2d -o memory.mif

The size of the memory block will be exactly the number of words needed to
translate the assembly code. You can change this with the ``-w`` argument:

.. code:: bash

    asm2d source.s2d -w 512

Help
~~~~

.. code:: bash

    asm2d -h
