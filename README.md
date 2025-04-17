AssemblyLineLibrary
===================
Wrapper around [AssemblyLine](https://github.com/0xADE1A1DE/AssemblyLine)
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
t = AssemblyLineBinary(test)
t.assemble()
    # memory will initialize with random memory
    .rand()
    # output the assembly in a hex format
    .print()
    # output the assembly into file
    .Print(file)
    # output the machine code into an object file
    .object_(file)
    # each input will be aligned to the given boundary in bytes. NOP instructions
    # are used for the alignment
    .chunk(chunk_size)
    # Enables nasm-style mov-immediate register-size handling.
    .nasm_mov_imm()
    # Disables nasm-style mov-immediate register-size handling.
    .strict_mov_imm()
    # The immediate value will be checked for leading 0's, to decide if the
    # nasm mov style should be used or not.
    .smart_mov_imm()
    # In SIB addressing if the index register is esp or rsp then the base and
    # index registers will be swapped.
    .nasm_sib_index_base_swap()
    #
    .strict_sib_index_base_swap()
    # In SIB addressing if there is no base register present and scale is equal
    # to 2; the base register will be set to the index register and the scale
    # will be reduced to 1.
    .nasm_sib_no_base()
    #
    .strict_sib_no_base()
    # equivalent to `.nasm_sib_index_base_swap().nasm_sib_no_base()`
    .nasm_sib()
    # equivalent to `.strict_sib_index_base_swap().strict_sib_no_base()`
    .strict_sib()
    # equivalent to `.nasm_mov_imm().nasm_sib()`
    .nasm()
    # equivalent to `.strict_mov_imm().strict_sib()`
    .strict()
```
more details are [here](https://github.com/FloydZ/AssemblyLinePython/blob/ed17efe46a4e474368bb5ded5108643eb90424ab/AssemblyLinePython/execute.py#L159)

Install:
========
via pip:
```bash
pip install git+https://github.com/FloydZ/AssemblyLinePython
```
Note: the following packages need to be accessible via shell:
- `autoconf`
- `automake`
- `libtool`
- `pkg-config`

These can be installed via:
### Ubuntu:
```shell 
sudo apt install autotools make pkg-config
```

### Arch:
```shell 
sudo pacman -S autotools make pkg-config
```

### NixOS:
```shell 
nix-shell
```

Build:
======
You can build the project either via `nix`:
```bash
git clone https://github.com/FloydZ/AssemblyLinePython
cd AssemblyLinePython
nix-shell  
```
which gives you a precompiled development environment or run:
```bash
git clone https://github.com/FloydZ/AssemblyLinePython
cd AssemblyLinePython
pip install -r requirements.txt
./build.sh

# build the python package for development
pip install --editable .
```
