import clang.cindex

# Returns a list of cursors with scopes that contain search_string.
def cursor_search(cursor:clang.cindex.Cursor, search_string: str):
        
        # BRYAN - This is where your implementation will go!
        #
        # You're going to be working with libclang's CURSORS. Cursors are how we
        # navigate our C++ code, and are represented as a generic tree.
        # https://www.geeksforgeeks.org/generic-treesn-array-trees/?ref=lbp
        #
        # Each cursor is a node in this tree. Each cursor can have any number of cursors
        # as its "children" below it. Cursors all point to a part of the code.
        #
        # You'll find many examples online on how to navigate these trees. Example:
        # https://www.geeksforgeeks.org/generic-tree-level-order-traversal/
        #
        # Your task is to find all of the cursors with scopes that contain a given string.
        #
        # What does that mean?
        # Given the search string "return x + y", and the translation unit of following C++ program:
        '''
        int main(int x, int y)
        {
            return x + y;
        }
        void otherFunc()
        {
            notImportant();
        }
        '''
        # We'd want the function to return the cursor that points to all of 'main', as it 
        # contains "return x + y". This is so we can look at all of the other code contained 
        # in the 'main' scope later.
        #
        # I've already written a function that finds the (line, column) / (y, x) location of every
        # instance of the search string, so all you would need to do is:
        # 
        #       • for every location in search_location...
        #       • go through the generic cursor tree & find the closest cursor to that location
        #       • add it to cursor to cursor_list
        #
        # I believe that would return the cursor that contains the scope where our string is.
        # Run main.py to test this code!
        #
        # The test in main.py is looking for ".lock()". Ideally your function should return the
        # cursor that points to lines 42-46.
        #
        # There's also some documentation on how cursors, translation units, etc. work.
        # It's a bit confusingly written.
        # https://libclang.readthedocs.io/en/latest/
        
        search_locations = find_locations(cursor.translation_unit, search_string)

      
        cursor_list = list()
        # Get all of the children our starting cursor has.
        for cursor in cursor.get_children():

            # Base Theory: Look through each cursor and their children, mark the deepest cursor that contains the search location
            
            # Deepest cursor within this "family" that we've found to contain the search location
            deepest_cursor = cursor
            foundLoc = False


            # cursor.translation_unit.spelling:  The name of the file that our cursor's translation unit is attached to.
            #                                    There is only one translation unit per cursor tree, and all child cursors
            #                                    will share the same translation unit.
            #
            # cursor.location.file:              The name of the source code file that the cursor comes from.
            # 
            # These can sometimes be different, in the case of header files! Because of the
            # line below, we're only looking at the code in OUR file. Remember this!
            if(str(cursor.translation_unit.spelling) == str(cursor.location.file)):

                # Some information you can get out of the cursor that might interest you!
                # Each of these cursors has children, that can be found with 'cursor.get_children()'
                #print("Parent Cursor location:",str(cursor.location.line)+":"+str(cursor.location.column))

                # Check if this cursor contains any of the search locations
                for loc in search_locations:
                    if(is_location_within(loc[0], cursor.extent)):
                        full_list = recursive_cursor_search(cursor, loc)
                        cursor_list.extend(full_list)

        
        return cursor_list

# Recursive function to find the deepest cursor(s) in a given tree containing location,
# assuming the top cursor contains that location
def recursive_cursor_search(cursor:clang.cindex.Cursor, search_location):
    # How many of our children also contain location?
    valid_children = list()
    # The deepest cursors below us that contain location
    cursor_list = list()

    for child_cursor in cursor.get_children():
        if(str(cursor.translation_unit.spelling) == str(cursor.location.file)):
            if(is_location_within(search_location[0], child_cursor.extent)):
                valid_children.append(child_cursor)

    # If zero of our children contain location, then, assuming we do
    # we are the deepest child, return ourself
    if len(valid_children) == 0:
        cursor_list.append(cursor)
        return cursor_list

    # If >= 1 of our children contain location, then 
    # recurse and search for the deepest.
    for valid in valid_children:
        cursor_list.extend( recursive_cursor_search(valid, search_location))

    # At this point cursor_list contains the deepest children we have that contain search_location
    return cursor_list
    


# Given a search string, find every instance of it in the file of our
# translation unit. Returns an array of tuples, with each tuple being
# a line-column location of an instance of the search string.
def find_locations(translation_unit: clang.cindex.TranslationUnit, search_string: str):

    source_file = open(translation_unit.spelling)
    string_locations = list()
    line = 1

    # for every line in our source code file...
    for current_line in source_file.readlines():
        # for every character index in that line...
        for index in range(len(current_line)):
            # If the search_string is found at that index, add it to the string_locations.
            if current_line.startswith(search_string, index): string_locations.append((line, index+1)) 
        line += 1
    
    source_file.close()

    return string_locations

def is_location_within(line, src_range: clang.cindex.SourceRange):
    # TODO: Add in column..
    # TODO: Encode length information, to double check that the sourceRange covers the entire range
    start = src_range.start
    end = src_range.end
    start_line = start.line
    end_line = end.line
    if line >= start_line and line <= end_line:
        return True
    return False