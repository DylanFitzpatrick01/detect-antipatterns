# Setup
To pull from Docker Hub: ```docker pull elliotlyons/detect-antipatterns:latest```

LLVM install for Windows: https://github.com/llvm/llvm-project/releases/download/llvmorg-15.0.7/LLVM-15.0.7-win64.exe
Other versions: https://github.com/llvm/llvm-project/releases/

Install Python: https://www.python.org/downloads/

If running locally run the following commands:
``` pip install clang ```
``` pip install libclang ```

# Using LLVM/Clang to detect anti-patterns in a large C++codebase
 Tool to find anti-patterns that can lead to deadlocks
 - Set of rules/heuristics which can automatically detect common locking
mistakes.
- Can be automatically run during PR/Review so that mistakes never
make it into the codebase.
- Aims to eliminate/minimise any false positives.
 

### Contributors 

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
