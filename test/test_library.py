#!/usr/bin/env python3
""" test the library """

import os

from AssemblyLinePython import AssemblyLineLibrary


def test_string():
    """ test the string interface """
    t = AssemblyLineLibrary("mov rax, 0x0\nadd rax, 0x2;\n sub rax, 0x1\nret")
    assert t


def test_all():
    """ test all files """
    base_test_dir = "deps/AssemblyLine/test"
    for file in os.listdir(base_test_dir):
        print(file)
        fpath = os.path.join(base_test_dir, file)
        t = AssemblyLineLibrary(fpath)
        t.print().strict().run()
