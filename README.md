TODO:
====

- Currently the class `AssemblyLineLibrary` currently cannot execute an assembled
function. This is due to the fact that the mem allocated by `create_string_buffer`
is not executeable. And my `mmap` wrapper is not really working.

- README, CI, tests
