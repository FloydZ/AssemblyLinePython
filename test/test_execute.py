#!/usr/bin/env python3
""" simple test """

import os
from AssemblyLinePython import AssemblyLineBinary


def test_version():
    """
    test the version
    """
    tmp = AssemblyLineBinary("./dummy")
    version = tmp.__version__()
    assert version == "1.4.0"


def test_string():
    """
    test the string interface
    """
    tmp = AssemblyLineBinary("mov rax, 0x0\nadd rax, 0x2\n"
                             "sub rax, 0x1\nret")
    out = tmp.print().run()
    assert out == b'b8000000004883c0024883e801c3'


def test_all():
    """
    test everything
    """
    BASE_TEST_DIR="deps/AssemblyLine/test"
    ctr = 0
    files = [f for f in os.listdir(BASE_TEST_DIR) if f.endswith('.asm')]
    # NOTE: we need some of the tests, because the files are too big
    skip = [
        "bextr.asm",
        "imul.asm",
        "lea.asm",
        "mov.asm",
        "mulx.asm",
        "sarx.asm",
        "shlx.asm",
        "shrx.asm",
        "vaddpd.asm",
        "vperm2i128.asm",
        "vsubpd.asm",
    ]

    for file in files:
        if file in skip:
            continue

        fpath = os.path.join(BASE_TEST_DIR, file)
        print(fpath)
        tmp = AssemblyLineBinary(fpath)
        data = tmp.print().run()
        assert data
        ctr += 1


if __name__ == '__main__':
    #test_version()
    #test_string()
    test_all()
