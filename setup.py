#!/usr/bin/env python3
from AssemblyLinePython import __version__, __author__, __email__
import subprocess
from setuptools import setup
from distutils.command.install import install as _install
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.build import build


def read_text_file(path):
    import os
    with open(os.path.join(os.path.dirname(__file__), path)) as f:
        return f.read()


class MyBuild(build):
    def run(self):
        subprocess.call(["/usr/bin/env", "bash", './build.sh'])
        build.run(self)

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
    cmdclass={'install': MyBuild},
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
