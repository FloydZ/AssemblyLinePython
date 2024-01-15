AssemblyLineLibrary
===================
Wrapper class around [AssemblyLine](https://github.com/0xADE1A1DE/AssemblyLine)
to generate machine of x86_64 assembly code on the fly without calling an 
assembler or compiler.

Usage:
-----
One can either assemble a file:
```python
t = AssemblyLineBinary(path_to_file)
t.print().strict().run()
```

or a string:
```python
tesxt = "mov rax, 0x0\nadd rax, 0x2; adds two"
t = AssemblyLineBinary(test)
t.print().strict().run()
```

Flags:
------
The wrapper library supports the same flags as [asmline](https://github.com/0xADE1A1DE/AssemblyLine/tree/main/tools).
E.g.:
```python
t.assemble()
.rand()
.print()
.Print()
.object_()
.chunk(chunk_size)
.nasm_mov_imm()
.strict_mov_imm()
.smart_mov_imm()
.nasm_sib_index_base_swap()
.strict_sib_index_base_swap()
.nasm_sib_no_base()
.strict_sib_no_base()
.nasm_sib()
.strict_sib()
.nasm()
.strict()
```

more details are [here](https://github.com/FloydZ/AssemblyLinePython/blob/ed17efe46a4e474368bb5ded5108643eb90424ab/AssemblyLinePython/execute.py#L159)

Install:
========
via pip:
```bash
pip install git+https://github.com/FloydZ/AssemblyLinePython
```

Build:
======
You can build the project either via nix:
```bash
git clone https://github.com/FloydZ/AssemblyLinePython
cd AssemblyLineLibrary
nix-shell  
```        
which gives you a precompiled development environment or run:
```bash
git clone https://github.com/FloydZ/AssemblyLinePython
cd AssemblyLineLibrary
pip install -r requirements.txt

cd deps/AssemblyLine
#./autogen.sh
./configure
make
cd ../..

# build the python package for development
pip install --editable .
```

Known bugs:
===========
Currently the class `AssemblyLineLibrary` currently cannot execute an assembled
function. This is due to the fact that the mem allocated by `create_string_buffer`
is not executeable. And my `mmap` wrapper is not really working.
