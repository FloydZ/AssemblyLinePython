{ pkgs ? import <nixpkgs> {} }:
let
  mach-nix = import (builtins.fetchGit {
    url = "https://github.com/DavHau/mach-nix";
    ref = "refs/tags/3.5.0";
  }) {};
  pyEnv = mach-nix.mkPython rec {
    providers._default = "wheel,conda,nixpkgs,sdist";
    requirements = builtins.readFile ./requirements.txt;
  };
in
#pkgs.mkShell {
mach-nix.nixpkgs.mkShell {
  buildInputs = with pkgs;[
    clang
    pyEnv

    # needed for AssemblyLine
    autoconf
    automake
    libtool
  ];

  shellHook = ''
    # build underlying C projects
    cd deps/AssemblyLine
    #./autogen.sh
    ./configure
    make
    cd ../..

    # build the python package for development
    pip install --editable .
  '';
}
