#!/usr/bin/env python3
from AssemblyLinePython import __version__, __author__, __email__
import os
from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from setuptools.command.build import build


def read_text_file(path):
    import os
    with open(os.path.join(os.path.dirname(__file__), path)) as f:
        return f.read()

def custom_command():
    import sys
    if sys.platform in ['linux']:
        os.system('./build.sh')


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        custom_command()


class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)
        custom_command()


class CustomEggInfoCommand(egg_info):
    def run(self):
        egg_info.run(self)
        custom_command()


setup(
    name="AssemblyLinePython",
    version=__version__,
    description="TODO",
    long_description=read_text_file("README.md"),
    author=__author__,
    author_email=__email__,
    url="https://github.com/FloydZ/AssemblyLinePython",
    packages=["AssemblyLinePython"],
    keywords=["assembly", "assembler", "asm", "opcodes", "x86", "x86-64", "isa", "cpu"],
    install_requires=["setuptools",],
   cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
    package_data={'pkgtest': ['deps/AssemblyLine/.libs/libasseblyline.so',
                              'deps/AssemblyLine/.libs/libasseblyline.so.1.2.5'
                              'deps/AssemblyLine/.libs/libasseblyline.a']},
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
