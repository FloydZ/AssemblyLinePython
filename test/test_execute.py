import os
from AssemblyLinePython import AssemblyLineBinary


def test_version():
    """
    """
    t = AssemblyLineBinary("./dummy")
    version = t.__version__()
    assert version == "1.3.2"


def test_string():
    """
    """
    t = AssemblyLineBinary("./mov rax, 0x0\nadd rax, 0x2; adds two")
    t.print().strict().run()


def test_all():
    BASE_TEST_DIR="deps/AssemblyLine/test"
    for file in os.listdir(BASE_TEST_DIR):
        print(file)
        fpath = os.path.join(BASE_TEST_DIR, file)
        t = AssemblyLineBinary(fpath)
        t.print().strict().run()
