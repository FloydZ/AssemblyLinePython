#!/usr/bin/env python3
from typing import Union
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
import logging
import ctypes
import re
import mmap
from mmap import MAP_ANONYMOUS, MAP_PRIVATE, PROT_EXEC, PROT_READ, PROT_WRITE


DEBUG = True
SUCCESS = 0
FAILURE = 1


class AssemblyLineLibrary:
    """
    wrapper around `assemblyline.{so}`
    """
    LIBRARY = Path("../deps/AssemblyLine/.libs/libassemblyline.so").absolute()
    C_LIBRARY = ctypes.CDLL(LIBRARY)

    # needed for `mmap`
    LIBC = ctypes.CDLL("libc.so.6")     

    def __init__(self):
        """
        """
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
        self.mmap = AssemblyLineLibrary.LIBC.mmap(0, size, PROT_READ|PROT_WRITE|PROT_EXEC, 
                                                 MAP_ANONYMOUS|MAP_PRIVATE, -1, 0)
        self.mmap = ctypes.c_char_p(self.mmap)
        if self.mmap == -1:
            logging.error("asm_create_instance: coulnd allocate memory")
            return FAILURE

        #self.mmap = mmap.mmap(-1, size, MAP_ANONYMOUS|MAP_PRIVATE,PROT_READ|PROT_WRITE|PROT_EXEC)
        #self.mmap = ctypes.c_void_p.from_buffer(self.mmap)
        #print(self.mmap)
        
        self.mmap = ctypes.create_string_buffer(size)

        self.instance = AssemblyLineLibrary.C_LIBRARY.asm_create_instance(self.mmap, size)
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
        ret = AssemblyLineLibrary.C_LIBRARY.asm_destroy_instance(self.instance)
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
        AssemblyLineLibrary.C_LIBRARY.asm_set_debug(self.instance, debug)
    
    def asm_assemble_str(self, asm: str):
        """
        calls the C function: `asm_assemble_str`

        :param str: string c
        :return: 0 on success, 1 on failure
        """
        c_asm = ctypes.c_char_p(str.encode(asm))
        print("lel")
        ret = AssemblyLineLibrary.C_LIBRARY.asm_assemble_str(self.instance, c_asm)
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
        ret = AssemblyLineLibrary.C_LIBRARY.asm_assemble_file(self.instance, file)
        if ret == FAILURE:
            logging.error("asm_assemble_file failed on: " + file)
        return ret

    def asm_get_code(self):
        """
        Gets the assembled code.

        :return f: a function of the assembled 
        """
        FUNC = ctypes.CFUNCTYPE(None)
        ret_ptr = AssemblyLineLibrary.C_LIBRARY.asm_get_code(self.instance)
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

        # TODO asm_sib_index_base_swap, asm_sib_no_base, asm_sib, asm_set_all



class AssemblyLineBinary:
    """
    Wrapper around the `asmline` binary
    """
    BINARY = "../deps/AssemblyLine/tools/asmline"

    def __init__(self, file: Union[Path, str]):
        """
        :param file: the file to assemble into memory
        """
        self.file = file
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
        """
        self.command.append("-r" + str(len))
        return self

    def rand(self):
        """
        """
        self.command.append("--rand")
        return self

    def print(self):
        """
        """
        self.command.append("--print")
        return self

    def Print(self, file: Union[str, Path]):
        """
        """
        if type(file) == Path:
            file = file.absolute()
        self.command.append("--printfile " + file)
        return self

    def object_(self, file: Union[str, Path]):
        """
        """
        if type(file) == Path:
            file = file.absolute()
        self.command.append("--object " + file)
        return self

    def chunk(self, chunk_size: int):
        """
        """
        if chunk_size <= 0:
            logging.error("smaller than 0")
            return self

        self.command.append("--chunk " + str(chunk_size))
        return self

    def nasm_mov_imm(self):
        """
        """
        self.command.append("--nasm-mov-imm")
        return self

    def strict_mov_imm(self):
        """
        """
        self.command.append("--strict-mov-imm")
        return self

    def smart_mov_imm(self):
        """
        """
        self.command.append("--smart-mov-imm")
        return self

    def nasm_sib_index_base_swap(self):
        """
        """
        self.command.append("--nasm-sib-index-base-swap")
        return self

    def strict_sib_index_base_swap(self):
        """
        """
        self.command.append("--strict-sib-index-base-swap")
        return self

    def nasm_sib_no_base(self):
        """
        """
        self.command.append("--nasm-sib-no-base")
        return self

    def strict_sib_no_base(self):
        """
        """
        self.command.append("--strict-sib-no-base")
        return self

    def nasm_sib(self):
        """
        """
        return self.nasm_sib_index_base_swap().nasm_sib_no_base()

    def strict_sib(self):
        """
        """
        return self.strict_sib_index_base_swap().strict_sib_no_base()
    
    def nasm(self):
        """
        """
        return self.nasm_mov_imm().nasm_sib()

    def strict(self):
        """
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
