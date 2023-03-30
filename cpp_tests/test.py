import clang.cindex

index = clang.cindex.Index.create()
translation_unit = index.parse('cpp_tests/atomic_branching.cpp')

def traverse_cursor(cursor):
    if cursor.kind == (clang.cindex.CursorKind.VAR_DECL or clang.cindex.CursorKind.FIELD_DECL) and cursor.spelling == 'mIsSet':
        node = cursor.get_definition()
        location = node.location
        # Get the source code range of the variable
        range = node.extent
        # Extract the text of the variable declaration
        variable_text = translation_unit.get_source_range(range).lstrip().rstrip()
        # Get the value of the variable using the libclang Python bindings
        value = translation_unit.get_tokens(extent=range)[0].spelling
        print(f"Value of {variable_text} is {value}")
        
    for child_cursor in cursor.get_children():
        traverse_cursor(child_cursor)

traverse_cursor(translation_unit.cursor)