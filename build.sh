# build underlying C projects
git submodule update --init
cd deps/AssemblyLine
./autogen.sh
./configure
make
cd ../..
