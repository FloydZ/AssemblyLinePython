#!/usr/bin/env python3
from typing import Union
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
import logging
import ctypes
import re
import os
import tempfile
import mmap
from mmap import MAP_ANONYMOUS, MAP_PRIVATE, PROT_EXEC, PROT_READ, PROT_WRITE


DEBUG = True
SUCCESS = 0
FAILURE = 1


class AssemblyLineLibrary:
    """
    wrapper around `assemblyline.{so}`
    """
    LIBRARY = Path("deps/AssemblyLine/.libs/libassemblyline.so").absolute()

    def __init__(self):
        """
        """
        self.C_LIBRARY = ctypes.CDLL(AssemblyLineLibrary.LIBRARY)

        # needed for `mmap`
        self.LIBC = ctypes.CDLL("libc.so.6")     
        self.mmap = None
        self.struct = None
        self.size = 4000
        self.__asm_create_instance(self.size)
        self.__asm_set_debug(True)
        self.asm_assemble_str("mov rax, 0x0\nadd rax, 0x2; adds two")
        #self.asm_get_code()
        self.__asm_destroy_instance()

    def __asm_create_instance(self, size: int):
        """
        calls the C function: `asm_create_instance`
        :param size: number of bytes to preallocate. The buffer must be big 
                    enough to hold the assembled output.
        :return: 0 on success, 1 on failure
        """
        assert size > 0

        # TODO not working: (mmap code is either not executable or not writeable)
        self.mmap = self.LIBC.mmap(0, size, PROT_READ|PROT_WRITE|PROT_EXEC, 
                                                 MAP_ANONYMOUS|MAP_PRIVATE, -1, 0)
        self.mmap = ctypes.c_char_p(self.mmap)
        if self.mmap == -1:
            logging.error("asm_create_instance: coulnd allocate memory")
            return FAILURE

        #self.mmap = mmap.mmap(-1, size, MAP_ANONYMOUS|MAP_PRIVATE,PROT_READ|PROT_WRITE|PROT_EXEC)
        #self.mmap = ctypes.c_void_p.from_buffer(self.mmap)
        #print(self.mmap)
        
        self.mmap = ctypes.create_string_buffer(size)

        self.instance = self.C_LIBRARY.asm_create_instance(self.mmap, size)
        assert self.mmap
        assert self.instance
        return SUCCESS

    def __asm_destroy_instance(self):
        """
        calls the C function: `asm_destroy_instance`
        Note: `__asm_create_instance()` must be called first, otherwise will
            this function crash.

        :return: 0 on success, 1 on failure
        """
        assert self.instance
        ret = self.C_LIBRARY.asm_destroy_instance(self.instance)
        if ret == FAILURE:
            logging.error("asm_destroy_instance failed")
        return ret
    
    def __asm_set_debug(self, debug: bool):
        """
        calls the C function: `asm_set_debug`
        Note: `__asm_create_instance()` must be called first, otherwise will
            this function crash.

        :param debug: if true: enable debugging, else disable it.
        :return: nothing
        """
        assert self.instance
        self.C_LIBRARY.asm_set_debug(self.instance, debug)
    
    def asm_assemble_str(self, asm: str):
        """
        calls the C function: `asm_assemble_str`

        :param str: string c
        :return: 0 on success, 1 on failure
        """
        c_asm = ctypes.c_char_p(str.encode(asm))
        ret = self.C_LIBRARY.asm_assemble_str(self.instance, c_asm)
        print(self.mmap)
        if ret == FAILURE:
            logging.error("asm_assemble_str failed on: " + asm)
        return ret

    
    def asm_assemble_file(self, file: str):
        """
        calls the C function: `asm_assemble_file`

        :param file: string/path to the file to assemble
        :return: 0 on success, 1 on failure
        """
        ret = self.C_LIBRARY.asm_assemble_file(self.instance, file)
        if ret == FAILURE:
            logging.error("asm_assemble_file failed on: " + file)
        return ret

    def asm_get_code(self):
        """
        Gets the assembled code.

        :return f: a function of the assembled 
        """
        FUNC = ctypes.CFUNCTYPE(None)
        ret_ptr = self.C_LIBRARY.asm_get_code(self.instance)
        assert ret_ptr
        f = FUNC(ret_ptr)
        return f

    def asm_create_bin_file(self, file: Union[str, Path]):
        """
        Generates a binary file @param file_name from assembled machine code up to
        the memory offset of the current instance @param al. 

        :return 0 on success, 1 on failure
        """
        raise NotImplemented

    def asm_mov_imm(self, option: int):
        """
        Nasm optimizes a `mov rax, IMM` to `mov eax, imm`, iff imm is <= 0x7fffffff
        for all destination registers. The following three methods allow the user to
        specify this behavior.

        :param option:
            enum asm_opt { STRICT, NASM, SMART };
        :return nothing
        """
        assert option < 3
        raise NotImplemented

    def asm_sib_index_base_swap(self, option: int):
        raise NotImplemented
    def asm_sib_no_base(self, option: int):
        raise NotImplemented
    def asm_sib(self, option: int):
        raise NotImplemented
    def asm_set_all(self, option: int):
        raise NotImplemented


class AssemblyLineBinary:
    """
    Wrapper around the `asmline` binary
    """
    BINARY = "deps/AssemblyLine/tools/asmline"

    def __init__(self, file: Union[Path, str]):
        """
        :param file: the file to assemble into memory
        """
        if type(file) ==  str:
            if os.path.isfile(file):
                self.file = file
            else:
                self.__file = tempfile.NamedTemporaryFile()
                self.file = self.__file.name
                self.__file.write(file.encode())
        else:
            self.file =  file.absolute()
        self.command = []

    def run(self):
        """

        :return
        """
        
        cmd = [AssemblyLineBinary.BINARY] + self.command + [self.file]
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        p.wait()
        if p.returncode != 0:
            assert p.stdout
            logging.error("could not run:" + str(p.returncode) + str(cmd) + p.stdout.read().decode("utf-8"))
            return p.returncode
       
        assert p.stdout
        data = p.stdout.readlines()
        data = [str(a).replace("b'", "")
                      .replace("\\n'", "")
                      .lstrip() for a in data]
        print(data)
    
    def assemble(self, len:int=10):
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
        self.command.append("-r" + str(len))
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
        self.command.append("--print")
        return self

    def Print(self, file: Union[str, Path]):
        """
        The corresponding machine code will be printed to
        FILENAME in binary form. Can be set to 
        '/dev/stdout' to write to stdout.
        """
        if type(file) == Path:
            file = file.absolute()
        self.command.append("--printfile " + file)
        return self

    def object_(self, file: Union[str, Path]):
        """
        The corresponding machine code will be printed to
        FILENAME.bin in binary.
        """
        if type(file) == Path:
            file = file.absolute()
        self.command.append("--object " + file)
        return self

    def chunk(self, chunk_size: int):
        """
        Sets a given CHUNK_SIZE>1 boundary in bytes. Nop 
        padding will be used to ensure no instruction 
        opcode will cross the specified CHUNK_SIZE 
        boundary.    """
        if chunk_size <= 0:
            logging.error("smaller than 0")
            return self

        self.command.append("--chunk " + str(chunk_size))
        return self

    def nasm_mov_imm(self):
        """
        Enables nasm-style mov-immediate register-size
        handling. ex: if immediate size for mov is les
        than or equal to max signed 32 bit assemblyline
        will emit code to mov to the 32-bit register 
        rather than 64-bit. That is: 
        "mov rax,0x7fffffff" as "mov eax,0x7fffffff"
        -> b8 ff ff ff 7f note: rax got optimized to 
        eax for faster immediate to register transfer
        and produces a shorter instruction        
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
            logging.error("could not run:" + str(p.returncode) + str(cmd) + p.stdout.read().decode("utf-8"))
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




# a = AssemblyLineLibrary()
b = AssemblyLineBinary("../deps/AssemblyLine/test/or.asm")
print(b.__version__())
b.print().strict().run()
