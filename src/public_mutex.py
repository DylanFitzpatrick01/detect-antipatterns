import clang
import main


# def public_mutex_members(dataPairs):
#     is_public = False
#     war = False
#     curly_brackets_count = 0
#
#     for index, pair in enumerate(dataPairs):
#         if pair.variable == "public":
#             is_public = True
#         elif pair.variable == "private" or pair.variable == "protected":
#             is_public = False
#         elif pair.variable == "{":
#             curly_brackets_count = curly_brackets_count + 1
#         elif pair.variable == "}":
#             curly_brackets_count = curly_brackets_count - 1
#         elif is_public and curly_brackets_count == 1 and pair.variable == "mutex":
#             print("public_mutex_members - Are you sure you want to have a public mutex called " + dataPairs[index+1].variable + ", Line - " + str(dataPairs[index+1].line_number))
#             war = True
#
#     if not war:
#         print("No errors found for public mutex members.")

def public_mutex_members_API(cursor: clang.cindex.Cursor):
    if str(cursor.access_specifier) == "AccessSpecifier.PUBLIC":
        count = 0
        contains = False
        for cursor1 in cursor.get_children():
            count += 1
            if str(cursor1.displayname) == "class std::mutex" and str(cursor1.kind) == "CursorKind.TYPE_REF":
                contains = True
            if count > 2:
                break
        if contains and count == 2:
            main.cursor_lines += str(cursor.location.line) + " "
            print("public_mutex_members - Are you sure you want to have a public mutex called " + str(
                cursor.displayname) + ", Line - " + str(cursor.location.line))
