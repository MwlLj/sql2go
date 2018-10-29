import sys
import os
sys.path.append("../base")
from file_handle_re import CFileHandle
from cmdline_handle import CCmdlineHandle
from parse_sql import CSqlParse
from write_param_class import CWriteParamClass
from write_interface import CWriteInterface


class CCmdHandle(CCmdlineHandle):
	def __init__(self):
		CCmdlineHandle.__init__(self)
		self.m_file_path = None
		self.m_obj = "."
		self.m_cpp_obj = None
		self.m_h_obj = None
		self.m_is_help = False
		self.m_is_exe_sql = False
		self.m_is_gen_cfg = False

	def get_register_dict(self):
		return {"-f": 1, "-o": 1, "-h": 0, "-sql": -1, "-gcfg": 1}

	def single_option(self, option, param_list):
		if option == "-h":
			self.m_is_help = True
			self.__print_help_info()
		elif option == "-f":
			file_path = param_list[0]
			self.m_file_path = file_path
		elif option == "-o":
			self.m_obj = param_list[0]
		elif option == "-sql":
			self.m_is_exe_sql = True
			self.__execute_sql(param_list)
		elif option == "-gcfg":
			self.m_is_gen_cfg = True
			self.__write_config(param_list[0])

	def param_error(self, option):
		if option == "-f":
			print("please input filepath")
		elif option == "-o":
			print("please input objpath")

	def parse_end(self):
		if self.m_is_help is True:
			return
		if self.m_is_exe_sql is True:
			return
		if self.m_is_gen_cfg is True:
			return
		if self.m_file_path is None:
			print("please input filepath")
			return
		isExist = os.path.exists(self.m_file_path)
		if isExist is False:
			print("file is not exist")
			return
		# 判断输出目录是否存在
		obj_flag = False
		cpp_obj_flag = False
		h_obj_flag = False
		isExist = os.path.exists(self.m_obj)
		if isExist is False:
			print("dir is not exist")
			return
		parser = CSqlParse(self.m_file_path)
		parser.read()
		info_dict = parser.get_info_dict()
		# 创建命名空间命名的目录
		namespace = info_dict.get(CSqlParse.NAMESPACE)
		if namespace is None:
			raise RuntimeError("no namesapce")
		path = os.path.join(self.m_obj, namespace)
		if os.path.exists(path) is False:
			os.makedirs(path)
		# 写参数类
		writer = CWriteParamClass(parser.get_file_path(), root=path)
		writer.write(info_dict)
		# 写数据库接口类
		writer = CWriteInterface(parser.get_file_path(), root=path)
		writer.write(info_dict)

	def __write_config(self, path):
		content = ""
		content += "host=localhost\n"
		content += "port=3306\n"
		content += "dbname=test\n"
		content += "username=root\n"
		content += "userpwd=123456\n"
		handler = CFileHandle()
		handler.clear_write(content, path, "utf8")

	def __execute_sql(self, param_list):
		host = "localhost"
		port = 3306
		username = "root"
		userpwd = "123456"
		dbname = "test"
		filepath = "./test.sql"
		length = len(param_list)
		for i in range(length):
			param = param_list[i]
			if param == "-sqlh":
				host = param_list[i + 1]
			elif param == "-sqlP":
				port = param_list[i + 1]
			elif param == "-sqlu":
				username = param_list[i + 1]
			elif param == "-sqlp":
				userpwd = param_list[i + 1]
			elif param == "-sqldb":
				dbname = param_list[i + 1]
			elif param == "-sqlf":
				filepath = param_list[i + 1]
		cmd = "mysql -f -h {0} -P {1} -u{2} -p{3} {4} < {5}".format(host, port, username, userpwd, dbname, filepath)
		print(cmd)
		os.system(cmd)

	def __print_help_info(self):
		info = "\n\toptions:\n"
		info += "\t\t-h: help\n"
		info += "\t\t-f: *.sql file path\n"
		info += "\t"*2 + "-o: output file path\n"
		info += "\t"*2 + "-gcfg: output config file path\n"
		info += "\t"*2 + "-sql: execute .sql script\n"
		info += "\t"*2 + "use with -sql:\n"
		info += "\t"*3 + "-sqlh: mysql host\n"
		info += "\t"*3 + "-sqlP: mysql port\n"
		info += "\t"*3 + "-sqlu: mysql username\n"
		info += "\t"*3 + "-sqlp: mysql userpwd\n"
		info += "\t"*3 + "-sqldb: leading_in database name\n"
		info += "\t"*3 + "-sqlf: *.sql file path\n"
		info += "\t"*2 + "-sql example:\n"
		info += "\t"*2 + "python ./main.py -sql -sqlf ./file/user_info.sql -sqldb test\n"
		info += "\n" + "\t"*1 + "for example:\n"
		info += "\t"*2 + "python ./main.py -f ./file/user_info.sql -o ./project/interface"
		info += "\n"
		print(info)


if __name__ == "__main__":
	handle = CCmdHandle()
	handle.parse()
