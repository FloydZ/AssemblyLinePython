# build underlying C projects
cd deps/AssemblyLine
./autogen.sh
./configure
make
cd ../..
