# DANCE
_Detecting ANtipatterns in a C++ Environment_

Sometimes, when programming with multiple threads, atomics, or concurrent memory accesses, errors slip in that don't show up until runtime (or worse, only in 1/100 runtimes). These include deadlocks, or mismanaged critical sections.

This is what DANCE aims to solve. Finding these bugs pre-compile, saving you from banging your head against a concurrency-shaped wall.

## Setup
__To run as an executable:__ download the latest version from our [releases page](https://github.com/DylanFitzpatrick01/detect-antipatterns/releases/)!

__To pull from Docker Hub:__ ```docker pull elliotlyons/detect-antipatterns:latest```

__If you want to run the native python code:__
- Install LLVM-Clang: https://clang.llvm.org/get_started.html
- Install Python 3: https://www.python.org/downloads/
- Install the Clang Python library: ``` pip install clang ```
- Install the Clang Python library: ``` pip install libclang ```
- Run the program! ```./DANCE [OPTIONS] [CHECKS_DIR] [LOCATIONS TO ANALYSE]```

## Usage
``DANCE [OPTIONS] checks_dir [locations ...]``

Positional arguments:
- _checks_dir_:
The directory holding the antipattern checks. These are python files you can completely change around if you want, drag and drop style.

- _locations_:
A list of places you want DANCE to look. These can be multiple directories or files, comma/whitespace separated.

Optional arguments:
- _-h | --help_:
Displays a help message, then exits.

- _-d | --clang_diags_:
Clang Diagnostics. When this flag is present, the output will start with any and all diagnostics raised by the Clang compiler. These could be compiler errors, header files it can't find, and so on.

- _-v | --verbose_:
Makes the output more friendly to human eyes. Instead of one error per-line, DANCE will print the section of code it's complaining about, with filenames and line numbers. If you're going to use any optional argument, use this one.

- _-i | --ignore_list_:
A list with all of the alert types you don't want to see. The two types currently supported are `warning` and `error`. (E.g, `-i error warning` would make DANCE output nothing)

- _-l | --libclang_dir_:
If you get a `clang.cindex.LibclangError`,  it's most likely because DANCE doesn't know where `libclang(.dll|.so|.dylib)` is. With `-l [LIBCLANG_LOCATION]`, you should be good to go.

- _-c | --clang_args_:
Arguments to be passed directly to Clang. Sometimes Clang doesn't know where a header file is. Other times you might want to specify what C++ installation Clang should use. Both of these are [arguments Clang supports](https://clang.llvm.org/docs/ClangCommandLineReference.html). They should be passed as a single string, with each argument space separated. (E.g., to add `C:\bin` to the path, the argument `-c "-I C:/bin"` would be used)

## Contributors

| Name				| Student Number| Year |
|-------------------|---------------|------|
| Daniel Penrose 	| 20331752 		| 3rd  |
| Elliot Lyons 		| 20333366 		| 3rd  |
|Dylan Fitzpatrick  | 20331794      | 3rd  |    
|Sprina Chen        | 21339184      | 2nd  |
|Antoni Zapedowski  | 21366133		| 2nd  |
|Bryan Chikwendu 	| 21363862		| 2nd  |
|Gráinne Ready 		| 20332706		| 2nd  |
|John Wallace 		| 21364595		| 2nd  |
|Liam Byrne 		| 21364304		| 2nd  |
|Leon Byrne 		| 21365536		| 2nd  |