from main import *
from contextlib import suppress
import os

def test_save_ast():

    # Our C++ 'file'
    cpp_file = '''
    int main(int x, int y)
    {
        return x + y
    }
    '''

    # The filename we'll be writing to.
    filename = "TESTING.txt"

    # Generate the translation unit from our 'file'.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
    
    # Save the AST of the translation unit
    save_ast(tu, filename)

    # Get the contents of the AST text file.
    file_string = open(filename, "r").read()

    # We don't need the file anymore
    with suppress(FileNotFoundError):
        os.remove(filename)

    # Make sure we get the AST we expect.
    assert file_string == '''int <- type = KEYWORD
main <- type = IDENTIFIER
( <- type = PUNCTUATION
int <- type = KEYWORD
x <- type = IDENTIFIER
, <- type = PUNCTUATION
int <- type = KEYWORD
y <- type = IDENTIFIER
) <- type = PUNCTUATION
{ <- type = PUNCTUATION
return <- type = KEYWORD
x <- type = IDENTIFIER
+ <- type = PUNCTUATION
y <- type = IDENTIFIER
} <- type = PUNCTUATION
'''

def test_count_tokens():

    # Our C++ 'file'
    cpp_file = '''
    int main(x, y)
    {
        return x + y
    }
    '''

    # Generate the translation unit from our 'file'.
    idx = clang.cindex.Index.create()
    tu = idx.parse('tmp.cpp', args=['-std=c++11'],  
                unsaved_files=[('tmp.cpp', cpp_file)],  options=0)
    
    # Make sure we get the number of tokens we expect.
    assert count_tokens(tu) == 13