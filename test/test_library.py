#!/usr/bin/env python3
from AssemblyLinePython import AssemblyLineLibrary
import os

# TODO implement incremental API
def test_string():
    """
    test the string interface
    """
    t = AssemblyLineLibrary("mov rax, 0x0\nadd rax, 0x2;\n sub rax, 0x1\nret")


def test_all():
    BASE_TEST_DIR="deps/AssemblyLine/test"
    for file in os.listdir(BASE_TEST_DIR):
        print(file)
        fpath = os.path.join(BASE_TEST_DIR, file)
        t = AssemblyLineLibrary(fpath)
        t.print().strict().run()
