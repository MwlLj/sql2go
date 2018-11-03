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

	def get_interface_name(self, method_name):
		return CStringTools.upperFirstByte(method_name)

	def get_input_struct_name(self, method_name):
		return "C{0}Input".format(CStringTools.upperFirstByte(method_name))

	def get_output_struct_name(self, method_name):
		return "C{0}Output".format(CStringTools.upperFirstByte(method_name))
