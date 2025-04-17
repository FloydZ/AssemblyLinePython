#!/usr/bin/env python3
""" install script """
import os
import sys
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from AssemblyLinePython import __version__, __author__, __email__


def read_text_file(path):
    """ read a test file and returns its content"""
    with open(os.path.join(os.path.dirname(__file__), path)) as file:
        return file.read()

def custom_command():
    """ build the needed `AssemblyLine` package """
    if sys.platform in ['linux']:
        os.system('./build.sh')


class CustomInstallCommand(install):
    """ install script """
    def run(self):
        custom_command()
        install.run(self)


class CustomDevelopCommand(develop):
    """ develop script """
    def run(self):
        custom_command()
        develop.run(self)


class CustomEggInfoCommand(egg_info):
    """ custom script """
    def run(self):
        custom_command()
        egg_info.run(self)


setup(
    name="AssemblyLinePython",
    author=__author__,
    author_email=__email__,
    version=__version__,
    description="assemble with python",
    long_description="assembler with python, based on AssemblyLie",
    url="https://github.com/FloydZ/AssemblyLinePython",
    package_dir={"": "AssemblyLinePython"},
    keywords=["assembly", "assembler", "asm", "opcodes", "x86", "x86-64", "isa", "cpu"],
    install_requires=["setuptools",],
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
    package_data={'': ['deps/']},
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
    ]
)
