#!/usr/bin/env python3
"""
binary wrapper
"""

from typing import Union
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
import logging
import re
import os
import tempfile
import time


class AssemblyLineBinary:
    """
    Wrapper around the `asmline` binary
    """
    BINARY = "deps/AssemblyLine/tools/asmline"

    def __init__(self, file: Union[Path, str]):
        """
        :param file: the file or str to assemble into memory
        """
        self.__file = tempfile.NamedTemporaryFile(suffix=".asm")
        if isinstance(file, str):
            if os.path.isfile(file):
                self.file = file
            else:
                self.__file.write(file.encode())
                self.__file.seek(0)
                self.file = self.__file.name
        else:
            self.file = file.absolute()
        self.command = []
        self.__print = False

    def run(self):
        """
        :return
        """
        cmd = [AssemblyLineBinary.BINARY] + self.command + [self.file]
        with Popen(cmd, stdout=PIPE, close_fds=True, bufsize=-1) as p:
            p.wait()
            if p.returncode != 0:
                assert p.stdout
                print("could not run: %s %s %s", p.returncode, str(cmd), \
                        p.stdout.read().decode("utf-8"))
                return p.returncode

            assert p.stdout
            data = p.stdout.readlines()
            data = [str(a).replace("b'", "")
                          .replace("\\n'", "")
                          .lstrip() for a in data]
            if self.__print:
                data = "".join(data).replace(" ", "")
                data = bytes(data.encode())
                self.__print = False
            return data

    def assemble(self, length: int=10):
        """
        Assembles FILE. Then executes it with six
        parameters to heap-allocated memory. Each
        pointer points to an array of LEN 64-bit
        elements which can be dereferenced in the asm-
        code, where LEN defaults to 10.
        After execution, it prints out the contents of
        the return (rax) register and frees the heap-
        memory.
        """
        self.command.append("-r" + str(length))
        return self

    def rand(self):
        """
        Implies -r and will additionally initialize the
        memory from with random data. -r=11 can be used
        to alter LEN.
        """
        self.command.append("--rand")
        return self

    def print(self):
        """
        The corresponding machine code will be printed to
        stdout in hex form. Output is similar to
        `objdump`: Byte-wise delimited by space and
        linebreaks after 7 bytes. If -c is given, the
        chunks are delimited by '|' and each chunk is
        on one line.
        """
        self.__print = True
        self.command.append("--print")
        return self

    def Print(self, file: Union[str, Path]):
        """
        The corresponding machine code will be printed to
        FILENAME in binary form. Can be set to
        '/dev/stdout' to write to stdout.
        """
        if isinstance(file, Path):
            file = file.absolute()

        assert isinstance(file, str)
        self.command.append("--printfile " + file)
        return self

    def object_(self, file: Union[str, Path]):
        """
        The corresponding machine code will be printed to
        FILENAME.bin in binary.
        """
        if isinstance(file, Path):
            file = file.absolute()
        
        assert isinstance(file, str)
        self.command.append("--object " + file)
        return self

    def chunk(self, chunk_size: int):
        """
        Sets a given CHUNK_SIZE>1 boundary in bytes. Nop
        padding will be used to ensure no instruction
        opcode will cross the specified CHUNK_SIZE
        boundary.
        """
        if chunk_size <= 0:
            logging.error("smaller than 0")
            return self

        self.command.append("--chunk " + str(chunk_size))
        return self

    def nasm_mov_imm(self):
        """
        Enables nasm-style mov-immediate register-size
        handling. ex: if immediate size for mov is less
        than or equal to max signed 32 bit. Assemblyline
        will emit code to mov to the 32-bit register
        rather than 64-bit. That is:
        "mov rax,0x7fffffff" as "mov eax,0x7fffffff"
        -> b8 ff ff ff 7f note: rax got optimized to
        eax for faster immediate to register transfer
        and produces a shorter instruction.
        """
        self.command.append("--nasm-mov-imm")
        return self

    def strict_mov_imm(self):
        """
        Disables nasm-style mov-immediate register-size
        handling. ex: even if immediate size for mov
        is less than or equal to max signed 32 bit
        assemblyline. Will pad the immediate to fit
        64-bit. That is: "mov rax,0x7fffffff" as
        "mov rax,0x000000007fffffff" ->
        48 b8 ff ff ff 7f 00 00 00 00
        """
        self.command.append("--strict-mov-imm")
        return self

    def smart_mov_imm(self):
        """
        The immediate value will be checked for leading
        0's. Immediate must be zero padded to 64-bits
        exactly to ensure it will not optimize. This is
        currently set as default. ex:
        "mov rax, 0x000000007fffffff" ->
        48 b8 ff ff ff 7f 00 00 00 00
        """
        self.command.append("--smart-mov-imm")
        return self

    def nasm_sib_index_base_swap(self):
        """
        In SIB addressing if the index register is esp or
        rsp then the base and index registers will be
        swapped. That is: "lea r15, [rax+rsp]" ->
        "lea r15, [rsp+rax]"
        """
        self.command.append("--nasm-sib-index-base-swap")
        return self

    def strict_sib_index_base_swap(self):
        """
        In SIB addressing the base and index registers
        will not be swapped even if the index register
        is esp or rsp.
        """
        self.command.append("--strict-sib-index-base-swap")
        return self

    def nasm_sib_no_base(self):
        """
        In SIB addressing if there is no base register
        present and scale is equal to 2; the base
        register will be set to the index register and
        the scale will be reduced to 1. That is:
        "lea r15, [2*rax]" -> "lea r15, [rax+1*rax]"
        """
        self.command.append("--nasm-sib-no-base")
        return self

    def strict_sib_no_base(self):
        """
        In SIB addressing when there is no base register
        present the index and scale would not change
        regardless of scale value. That is:
        "lea r15, [2*rax]" -> "lea r15, [2*rax]"
        """
        self.command.append("--strict-sib-no-base")
        return self

    def nasm_sib(self):
        """
        Is equivalent to --nasm-sib-index-base-swap
        --nasm-sib-no-base
        """
        return self.nasm_sib_index_base_swap().nasm_sib_no_base()

    def strict_sib(self):
        """
        Is equivalent to --strict-sib-index-base-swap
        --strict-sib-no-base
        """
        return self.strict_sib_index_base_swap().strict_sib_no_base()

    def nasm(self):
        """
        Is equivalent to --nasm-mov-imm --nasm-sib
        """
        return self.nasm_mov_imm().nasm_sib()

    def strict(self):
        """
        Is equivalent to --strict-mov-imm --strict-sib
        """
        return self.strict_mov_imm().strict_sib()

    def __version__(self):
        """
        """
        cmd = [AssemblyLineBinary.BINARY, "--version"]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        p.wait()
        if p.returncode != 0:
            assert p.stdout
            logging.error("could not run: %s %s %s", str(p.returncode), str(cmd), \
                    p.stdout.read().decode("utf-8"))
            return p.returncode

        assert p.stdout
        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]
        assert len(data) > 1
        data = data[-1]
        ver = re.findall(r'\d.\d.\d', data)
        assert len(ver) == 1
        return ver[0]
