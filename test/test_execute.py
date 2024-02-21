#!/usr/bin/env python3
""" simple test """
import os
from AssemblyLinePython import AssemblyLineBinary


def test_version():
    """
    test the version 1.3.2
    """
    tmp = AssemblyLineBinary("./dummy")
    version = tmp.__version__()
    assert version == "1.3.2"


def test_string():
    """
    test the string interface
    """
    tmp = AssemblyLineBinary("./mov rax, 0x0\nadd rax, 0x2; adds two")
    tmp.print().strict().run()


def test_all():
    """
    test everything
    """
    BASE_TEST_DIR="deps/AssemblyLine/test"
    for file in os.listdir(BASE_TEST_DIR):
        print(file)
        fpath = os.path.join(BASE_TEST_DIR, file)
        tmp = AssemblyLineBinary(fpath)
        tmp.print().strict().run()
