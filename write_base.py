import sys
import os
sys.path.append("../base")
from string_tools import CStringTools


class CWriteBase(object):
	def type_change(self, param_type):
		if param_type == "float":
			param_type = "float64"
		elif param_type == "double":
			param_type = "float64"
		return param_type

	def type_null_change(self, param_type):
		if param_type == "float":
			param_type = "sql.NullFloat64"
		elif param_type == "double":
			param_type = "sql.NullFloat64"
		elif param_type == "string":
			param_type = "sql.NullString"
		elif param_type == "int" or param_type == "int64" or param_type == "int32":
			param_type = "sql.NullInt64"
		elif param_type == "bool":
			param_type = "sql.NullBool"
		return param_type

	def type_back(self, param_type, param_name):
		result = ""
		if param_type == "float" or param_type == "double":
			result = "{0}.Float64".format(param_name)
		elif param_type == "string":
			result = "{0}.String".format(param_name)
		elif param_type == "int":
			result = "int({0}.Int64)".format(param_name)
		elif param_type == "int32":
			result = "int32({0}.Int64)".format(param_name)
		elif param_type == "int64":
			result = "int64({0}.Int64)".format(param_name)
		elif param_type == "bool":
			result = "bool({0}.Bool)".format(param_name)
		else:
			raise SystemError("[ERROR] param_type is not support")
		return result

	def get_interface_name(self, method_name):
		return CStringTools.upperFirstByte(method_name)

	def get_input_struct_name(self, method_name):
		return "C{0}Input".format(CStringTools.upperFirstByte(method_name))

	def get_output_struct_name(self, method_name):
		return "C{0}Output".format(CStringTools.upperFirstByte(method_name))

	def get_isvail_join_str(self):
		return "IsValid"
