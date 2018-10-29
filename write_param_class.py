import sys
import os
sys.path.append("../base")
import re
from string_tools import CStringTools
from file_handle_re import CFileHandle
from parse_sql import CSqlParse
from write_base import CWriteBase


class CWriteParamClass(CWriteBase):
	def __init__(self, file_path, root="."):
		self.m_file_handler = CFileHandle()
		self.m_file_path = ""
		self.m_content = ""
		self.__compare_file_path(file_path, root)

	def __compare_file_path(self, file_path, root):
		basename = os.path.basename(file_path)
		filename, fileext = os.path.splitext(basename)
		self.m_file_path = os.path.join(root, filename + "_db_param.go")

	def write(self, info_dict):
		# 获取 namesapce
		namespace = info_dict.get(CSqlParse.NAMESPACE)
		if namespace is None or namespace == "":
			raise RuntimeError("namespace is empty")
		self.__write_header(namespace)
		method_list = info_dict.get(CSqlParse.METHOD_LIST)
		self.m_content += self.__write_structs(method_list)
		# print(self.m_content)
		self.m_file_handler.clear_write(self.m_content, self.m_file_path, "utf8")

	def __write_structs(self, method_list):
		content = ""
		for method in method_list:
			input_params = method.get(CSqlParse.INPUT_PARAMS)
			output_params = method.get(CSqlParse.OUTPUT_PARAMS)
			method_name = method.get(CSqlParse.FUNC_NAME)
			if input_params is not None:
				content += self.__write_struct(method_name, input_params, self.get_input_struct_name(method_name))
			if output_params is not None:
				content += self.__write_struct(method_name, output_params, self.get_output_struct_name(method_name))
		return content

	def __write_struct(self, method_name, params, struct_name):
		content = ""
		content += "type {0} struct".format(struct_name)
		content += " {\n"
		for param in params:
			param_type = param.get(CSqlParse.PARAM_TYPE)
			param_name = param.get(CSqlParse.PARAM_NAME)
			if param_type is None or param_name is None:
				raise SystemExit("[Error] method: {0}, type or name is none".format(method_name))
			param_type = self.type_change(param_type)
			content += "\t" + "{0} {1}\n".format(CStringTools.upperFirstByte(param_name), param_type)
		content += "}\n\n"
		return content

	def __write_header(self, namespace):
		# 写宏定义防止多包含
		self.m_content += "package {0}\n\n".format(namespace)


if __name__ == "__main__":
	parser = CSqlParse("./file/user_info.sql")
	parser.read()
	info_dict = parser.get_info_dict()
	writer = CWriteParamClass(parser.get_file_path(), root="./obj")
	writer.write(info_dict)
