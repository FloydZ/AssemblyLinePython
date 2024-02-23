#!/usr/bin/env python3
from typing import Union
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
import logging
import os
import ctypes
from mmap import MAP_ANONYMOUS, MAP_PRIVATE, PROT_EXEC, PROT_READ, PROT_WRITE
#from ctypes import CFUNCTYPE
from .common import SUCCESS, FAILURE
#import tempfile
#import re
#import mmap


class AssemblyLineLibrary:
    """
    wrapper around `assemblyline.{so}`
    """
    LIBRARY = "deps/AssemblyLine/.libs/libassemblyline.so"

    def __init__(self, file: Union[Path, str]):
        """
        :param file: the file or str to assemble into memory
        """
        self.__data = ""
        if type(file) is str:
            if os.path.isfile(file):
                with open(file) as fp:
                    self.__data = str(fp.read())
            else:
                self.__data = file
        else:
            with open(file.absolute()) as fp:
                self.__data = str(fp.read())

        self.command = []
        self.C_LIBRARY = ctypes.CDLL(AssemblyLineLibrary.LIBRARY)

        # needed for `mmap`
        self.LIBC = ctypes.CDLL("libc.so.6")
        self.mmap = None
        self.struct = None
        self.size = 4000
        self.__asm_create_instance(self.size)
        self.__asm_set_debug(True)
        self.asm_assemble_str(self.__data)
        f = self.asm_get_code()
        print("pid", os.getpid())
        input()
        a = f()
        self.__f = f
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
        self.mmap = self.LIBC.mmap(0, size, PROT_READ | PROT_WRITE | PROT_EXEC,
                                   MAP_ANONYMOUS | MAP_PRIVATE, -1, 0)
        self.mmap = ctypes.c_char_p(self.mmap)
        if self.mmap == -1:
            logging.error("asm_create_instance: coulnd allocate memory")
            return FAILURE

        # self.mmap = mmap.mmap(-1, size, MAP_ANONYMOUS|MAP_PRIVATE,PROT_READ|PROT_WRITE|PROT_EXEC)
        # self.mmap = ctypes.c_void_p.from_buffer(self.mmap)
        # print(self.mmap)

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
        self.C_LIBRARY.asm_get_code.restype = FUNC
        ret_ptr = self.C_LIBRARY.asm_get_code(self.instance)
        assert ret_ptr
        return ret_ptr
        # f = FUNC(ret_ptr)
        # return f

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


# t = AssemblyLineLibrary("mov rax, 0x0\nadd rax, 0x2;\n sub rax, 0x1\nret")
