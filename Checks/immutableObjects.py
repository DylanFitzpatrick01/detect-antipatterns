import clang.cindex
from typing import List
from alerts import Alert
from formalCheckInterface import FormalCheckInterface

"""
TODO Write description of the check. This check also needs more comments!
"""

# We only want to run the check once!
checked = False

class Check(FormalCheckInterface):
	def analyse_cursor(self, cursor: clang.cindex.Cursor, alerts):
		global checked

		# If we haven't run the check before...
		if (not checked):

			# Check the top cursor of the tree!
			node = cursor.translation_unit.cursor

			# Our counters
			constant_variable_count = 0
			variable_count = 0

			constant_variable_count +=count_const_string_var_decls(node)
			constant_variable_count += count_const_bool_var_decls(node)
			constant_variable_count += count_const_int_var_decls(node)
			constant_variable_count += count_const_double_var_decls(node)
			constant_variable_count += count_const_char_var_decls(node)

			variable_count += count_string_var_decls(node)
			variable_count += count_bool_total_var_decls(node)
			variable_count += count_int_total_var_decls(node)
			variable_count += count_double_total_var_decls(node)
			variable_count += count_char_total_var_decls(node)

			threshold = 0.70
			
			# Added a check do that it won't cause division by zero error
			# -Leon Byrne
			if variable_count > 0:
				ratio = constant_variable_count / variable_count

				if ( ratio) >= threshold:
					ratio = ratio * 100
					ratio = round(ratio,0)

					newAlert = Alert(cursor.translation_unit, cursor.extent, (str(ratio) +
										"% of Variables are constant. This may cause an immutable object error"))
					if newAlert not in alerts:
						alerts.append(newAlert)
			
			# Set the 'checked' flag, so we don't run this check again.
			checked = True

	
								 

def count_const_string_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if node.type.spelling == "const std::string":
			count += 1
			#print("std::string variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):

			count += count_const_string_var_decls(child)
	return count

def count_const_bool_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const bool" :
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_const_bool_var_decls(child)
	return count 

def count_const_int_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const int" :
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_const_int_var_decls(child)
	return count 

def count_const_double_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const double" :
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_const_double_var_decls(child)
	return count

def count_const_char_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const char" :
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_const_char_var_decls(child)
	return count   



def count_string_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const std::string" or  node.type.spelling == "std::string" :
			count += 1
			#print(" std::string variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_string_var_decls(child)
	return count

def count_bool_total_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const bool" or  node.type.spelling == "bool" :
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_bool_total_var_decls(child)
	return count

def count_int_total_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const int" or  node.type.spelling == "int" :
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_int_total_var_decls(child)
	return count

def count_double_total_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if  node.type.spelling == "const double" or  node.type.spelling == "double" :
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_double_total_var_decls(child)
	return count

def count_char_total_var_decls(node: clang.cindex.Cursor) -> int:
	count = 0
	if node.kind in [clang.cindex.CursorKind.VAR_DECL,
					 clang.cindex.CursorKind.FIELD_DECL,
					 clang.cindex.CursorKind.PARM_DECL]:
		if node.type.spelling == "const char" or node.type.spelling == "char":
			count += 1
			#print("bool variable declaration: " + node.displayname)
	for child in node.get_children():
		if(str(child.translation_unit.spelling) == str(child.location.file)):
			count += count_char_total_var_decls(child)
	return count