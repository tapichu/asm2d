# Internal memory

Altera provides two megafunctions that implement the following memory modes:

* RAM: single-port.
* RAM: dual-port.
* ROM: single-port.
* ROM: dual-port.

One big advantage of using these internal memory blocks is that their contents
can be initialized during compile time using `.hex` or `.mif` files.

Changes to these files can be compiled quickly without having to compile the
whole project:

* Processing -> Update Memory Initialization File.
* Processing -> Start -> Start Assembler.

More information can be found in [this guide](http://www.altera.com/literature/ug/ug_ram_rom.pdf).
