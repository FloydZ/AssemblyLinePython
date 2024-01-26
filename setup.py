#!/usr/bin/env python3
from AssemblyLinePython import __version__, __author__, __email__
import subprocess
from setuptools import setup
from distutils.command.install import install as _install


def read_text_file(path):
    import os
    with open(os.path.join(os.path.dirname(__file__), path)) as f:
        return f.read()


class install(_install):
    def run(self):
        subprocess.call(['./build.sh'])
        _install.run(self)

setup(
    name="AssemblyLinePython",
    version=__version__,
    description="TODO",
    long_description=read_text_file("README.md"),
    author=__author__,
    author_email=__email__,
    url="https://github.com/FloydZ/python_x86_information",
    packages=["AssemblyLinePython"],
    keywords=["assembly", "assembler", "asm", "opcodes", "x86", "x86-64", "isa", "cpu"],
    install_requires=["setuptools"],
    requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Assembly",
	    "Programming Language :: Python",
	    "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Software Development :: Assemblers",
        "Topic :: Software Development :: Documentation"
    ])