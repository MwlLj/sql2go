import sys
import os
sys.path.append("../base")
import re
from string_tools import CStringTools
from file_handle_re import CFileHandle
from parse_sql import CSqlParse
from write_base import CWriteBase


class CWriteInterface(CWriteBase):
	DICT_KEY_METHOD_DEFINE = "method_define"
	DICT_KEY_PROCEDURE_INFO = "procedure_info"
	DICT_KEY_INPUT_PARAMS = "input_params"
	DICT_KEY_OUTPUT_PARAMS = "output_params"
	DICT_KEY_OUTPUT_CLASSNAME = "output_classname"
	def __init__(self, parser, file_path, root="."):
		self.m_file_handler = CFileHandle()
		self.m_file_name = ""
		self.m_file_path = ""
		self.m_content = ""
		self.m_namespace = ""
		self.m_procedure_info_list = []
		self.m_parser = parser
		self.__compare_file_path(file_path, root)

	def __compare_file_path(self, file_path, root):
		basename = os.path.basename(file_path)
		filename, fileext = os.path.splitext(basename)
		self.m_file_name = filename
		self.m_file_path = os.path.join(root, filename + "_db_handler" + ".go")

	def get_class_name(self):
		return "CDbHandler"

	def write(self, info_dict):
		# 获取 namesapce
		namespace = info_dict.get(CSqlParse.NAMESPACE)
		if namespace is None or namespace == "":
			raise RuntimeError("namespace is empty")
		self.m_namespace = namespace
		self.__write_header(namespace)
		self.m_content += self.__write_stuct()
		self.m_content += self.__write_connect()
		self.m_content += self.__write_connect_by_rule()
		self.m_content += self.__write_connect_by_cfg()
		self.m_content += self.__write_disconnect()
		create_sql = info_dict.get(CSqlParse.CREATE_TABELS_SQL)
		create_functions = info_dict.get(CSqlParse.CREATE_FUNCTION_SQLS)
		self.m_content += self.__write_create(create_sql, create_functions)
		# 获取每一个存储过程的参数
		method_list = info_dict.get(CSqlParse.METHOD_LIST)
		if method_list is None:
			raise SystemExit("[Error] method is None")
		self.m_content += self.__write_struct_method(method_list)
		# print(self.m_content)
		self.m_file_handler.clear_write(self.m_content, self.m_file_path, "utf8")

	def __join_method_param(self, method, method_define, param_no):
		if method is None:
			return method_define
		sub_func_list = method.get(CSqlParse.SUB_FUNC_SORT_LIST)
		func_name = method.get(CSqlParse.FUNC_NAME)
		input_params = method.get(CSqlParse.INPUT_PARAMS)
		output_params = method.get(CSqlParse.OUTPUT_PARAMS)
		def inner(method_define, param_no):
			input_class_name = self.get_input_struct_name(func_name)
			output_class_name = self.get_output_struct_name(func_name)
			in_isarr = method.get(CSqlParse.IN_ISARR)
			out_isarr = method.get(CSqlParse.OUT_ISARR)
			in_ismul = None
			out_ismul = None
			if in_isarr == "true":
				in_ismul = True
			else:
				in_ismul = False
			if out_isarr == "true":
				out_ismul = True
			else:
				out_ismul = False
			input_params_len = 0
			output_params_len = 0
			if input_params is not None:
				input_params_len = len(input_params)
			if output_params is not None:
				output_params_len = len(output_params)
			# 获取输入输出参数的字符串
			input_str = input_class_name
			output_str = output_class_name
			if in_ismul is True:
				input_str = "[]{0}".format(input_class_name)
			if out_ismul is True:
				output_str = "[]{0}".format(output_class_name)
			if input_params_len == 0 and output_params_len == 0:
				method_define += ""
			elif input_params_len > 0 and output_params_len == 0:
				method_define += "input{1} *{0}".format(input_str, str(param_no))
			elif input_params_len == 0 and output_params_len > 0:
				method_define += "output{1} *{0}".format(output_str, str(param_no))
			elif input_params_len > 0 and output_params_len > 0:
				method_define += "input{2} *{0}, output{2} *{1}".format(input_str, output_str, str(param_no))
			else:
				return None
			param_no += 1
			return method_define, param_no
		if sub_func_list is None:
			method_define, param_no = inner(method_define, param_no)
		else:
			i = 0
			length = len(sub_func_list)
			for sub_func_name, sub_func_index in sub_func_list:
				i += 1
				if func_name == sub_func_name:
					method_define, param_no = inner(method_define, param_no)
					if i < length and (input_params is not None or output_params is not None):
						method_define += ", "
					continue
				method_info = self.m_parser.get_methodinfo_by_methodname(sub_func_name)
				method_define, param_no = self.__join_method_param(method_info, method_define, param_no)
				if i < length and (input_params is not None or output_params is not None):
					method_define += ", "
		return method_define, param_no

	def __sub_func_index_change(self, sub_func_index):
		if sub_func_index == "":
			return ""
		result = ""
		if int(sub_func_index) < 0:
			result = "N" + str(int(sub_func_index) * -1)
		elif int(sub_func_index) > 0:
			result = "P" + sub_func_index
		else:
			result = "0"
		return result

	def __write_struct_method(self, method_list):
		content = ""
		for method in method_list:
			# ################################
			is_brace = method.get(CSqlParse.IS_BRACE)
			if is_brace is None:
				continue
			is_group = method.get(CSqlParse.IS_GROUP)
			if is_group is not None and is_group is True:
				continue
			# ################################
			func_name = method.get(CSqlParse.FUNC_NAME)
			method_name = self.get_interface_name(func_name)
			method_define, _ = self.__join_method_param(method, "", 0)
			if method_define is None:
				return content
			else:
				method_define = "{0}({1})".format(method_name, method_define)
			content += "func (this *{0}) ".format(self.get_class_name()) + method_define + " (error, uint64) {\n"
			content += self.get_method_imp(method)
			content += "}\n\n"
		return content

	def __replace_sql_brace(self, input_params, sql, is_group):
		if input_params is None:
			return sql, []
		fulls, max_number = CStringTools.get_brace_format_list(sql)
		param_len = len(input_params)
		full_set = set(fulls)
		full_len = len(full_set)
		if is_group is False:
			if param_len != full_len:
				str_tmp = "[Param Length Error] may be last #define error ? fulllen length({1}) != params length({2})\n[sql] : \t{0}".format(sql, full_len, param_len)
				raise SystemExit(str_tmp)
			if param_len < max_number + 1:
				str_tmp = "[Param Match Error] may be last #define error ? input param length == {1}, max index == {2}\n[sql] : \t{0}".format(sql, param_len, max_number)
				raise SystemExit(str_tmp)
		for number, keyword in list(full_set):
			inpams = input_params[number]
			tmp = ""
			param_type = inpams.get(CSqlParse.PARAM_TYPE)
			if inpams.get(CSqlParse.PARAM_IS_CONDITION) is True:
				tmp = "%s"
			else:
				tmp = "?"
			sql = re.sub(keyword, tmp, sql)
		return sql, fulls

	def get_method_imp(self, method):
		content = ""
		in_isarr = method.get(CSqlParse.IN_ISARR)
		out_isarr = method.get(CSqlParse.OUT_ISARR)
		in_ismul = None
		out_ismul = None
		if in_isarr == "true":
			in_ismul = True
		else:
			in_ismul = False
		if out_isarr == "true":
			out_ismul = True
		else:
			out_ismul = False
		func_name = method.get(CSqlParse.FUNC_NAME)
		input_params = method.get(CSqlParse.INPUT_PARAMS)
		input_class_name = self.get_input_struct_name(func_name)
		content += "\t"*1 + 'var rowCount uint64 = 0\n'
		content += "\t"*1 + "tx, _ := this.m_db.Begin()\n"
		content += "\t"*1 + "var result sql.Result\n"
		content += "\t"*1 + "var _ = result\n"
		content += "\t"*1 + "var err error\n"
		content += "\t"*1 + "var _ error = err\n"
		sub_func_sort_list = method.get(CSqlParse.SUB_FUNC_SORT_LIST)
		c, _ = self.__write_input(method, "", 0)
		content += c
		if in_ismul is True:
			content += "\t"*1 + "tx.Commit()\n"
		content += "\t"*1 + 'return nil, rowCount\n'
		return content

	def __write_input(self, method, content, param_no):
		in_isarr = method.get(CSqlParse.IN_ISARR)
		out_isarr = method.get(CSqlParse.OUT_ISARR)
		in_ismul = None
		out_ismul = None
		if in_isarr == "true":
			in_ismul = True
		else:
			in_ismul = False
		if out_isarr == "true":
			out_ismul = True
		else:
			out_ismul = False
		func_name = method.get(CSqlParse.FUNC_NAME)
		input_params = method.get(CSqlParse.INPUT_PARAMS)
		output_params = method.get(CSqlParse.OUTPUT_PARAMS)
		sub_func_list = method.get(CSqlParse.SUB_FUNC_SORT_LIST)
		output_class_name = self.get_output_struct_name(func_name)
		def inner(content, param_no):
			sql = method.get(CSqlParse.SQL)
			sql = re.sub(r"\\", "", sql)
			tc = 1
			var_name = "input{0}".format(str(param_no))
			if in_ismul is True:
				tc = 2
				var_name = "v"
				content += "\t"*1 + "for _, v := range *input" + str(param_no) + " {\n"
			if output_params is not None and len(output_params) > 0:
				content += "\t"*tc + "rows{0}, err := this.m_db.Query(".format(str(param_no))
			else:
				content += "\t"*tc + "result, err = this.m_db.Exec("
			sql, fulls = self.__replace_sql_brace(input_params, sql, False)
			content += 'fmt.Sprintf(`{0}`'.format(sql)
			if input_params is not None:
				for param in input_params:
					is_cond = param.get(CSqlParse.PARAM_IS_CONDITION)
					if is_cond is True:
						param_name = param.get(CSqlParse.PARAM_NAME)
						content += ", {1}.{0}".format(CStringTools.upperFirstByte(param_name), var_name)
			content += ")"
			content += self.__write_query_params(input_params, var_name, fulls)
			content += ")\n"
			tc = 1
			end_str = "return err, rowCount"
			if in_ismul is True:
				tc = 2
				end_str = "return err, rowCount"
			content += "\t"*tc + 'if err != nil {\n'
			content += "\t"*(tc+1) + 'tx.Rollback()\n'
			content += "\t"*(tc+1) + '{0}\n'.format(end_str)
			content += "\t"*tc + '}\n'
			if in_ismul is False:
				content += "\t"*1 + "tx.Commit()\n"
			if output_params is not None and len(output_params) > 0:
				content += "\t"*tc + 'defer rows{0}.Close()\n'.format(str(param_no))
				content += "\t"*tc + 'for rows' + str(param_no) + '.Next() {\n'
				content += "\t"*(tc+1) + 'rowCount += 1\n'
				content += self.__write_output(tc+1, method, param_no)
				content += "\t"*tc + '}\n'
			else:
				content += "\t"*tc + "var _ = result\n"
			if in_ismul is True:
				content += "\t"*1 + '}\n'
			param_no += 1
			return content, param_no
		if sub_func_list is None:
			content, param_no = inner(content, param_no)
		else:
			for sub_func_name, sub_func_index in sub_func_list:
				if func_name == sub_func_name:
					content, param_no = inner(content, param_no)
					continue
				method_info = self.m_parser.get_methodinfo_by_methodname(sub_func_name)
				content, param_no = self.__write_input(method_info, content, param_no)
		return content, param_no

	def __write_output(self, tc, method, param_no):
		in_isarr = method.get(CSqlParse.IN_ISARR)
		out_isarr = method.get(CSqlParse.OUT_ISARR)
		in_ismul = None
		out_ismul = None
		if in_isarr == "true":
			in_ismul = True
		else:
			in_ismul = False
		if out_isarr == "true":
			out_ismul = True
		else:
			out_ismul = False
		func_name = method.get(CSqlParse.FUNC_NAME)
		output_params = method.get(CSqlParse.OUTPUT_PARAMS)
		output_class_name = self.get_output_struct_name(func_name)
		content = ""
		length = 0
		if output_params is not None:
			length = len(output_params)
		if length == 0:
			return content
		if out_ismul is True:
			content += "\t"*tc + "tmp := {0}".format(output_class_name) + "{}\n"
		else:
			pass
		for param in output_params:
			param_type = param.get(CSqlParse.PARAM_TYPE)
			param_name = param.get(CSqlParse.PARAM_NAME)
			param_type = self.type_null_change(param_type)
			content += "\t"*tc + "var {0} {1}\n".format(param_name, param_type)
		content += "\t"*tc + "scanErr := rows{0}.Scan(".format(str(param_no))
		i = 0
		for param in output_params:
			i += 1
			param_name = param.get(CSqlParse.PARAM_NAME)
			content += "&{0}".format(param_name)
			if i < length:
				content += ", "
		content += ")\n"
		content += "\t"*tc + "if scanErr != nil {\n"
		content += "\t"*(tc+1) + "continue\n"
		content += "\t"*tc + "}\n"
		pre = ""
		if out_ismul is True:
			pre = "tmp"
		else:
			pre = "output{0}".format(str(param_no))
		for param in output_params:
			param_type = param.get(CSqlParse.PARAM_TYPE)
			param_name = param.get(CSqlParse.PARAM_NAME)
			content += "\t"*tc + "{0}.{1} = {2}\n".format(pre, CStringTools.upperFirstByte(param_name), self.type_back(param_type, param_name))
			content += "\t"*tc + "{0}.{1}{3} = {2}.Valid\n".format(pre, CStringTools.upperFirstByte(param_name), param_name, self.get_isvail_join_str())
		if out_ismul is True:
			content += "\t"*tc + "*output{0} = append(*output{0}, tmp)\n".format(str(param_no))
		return content

	def __write_query_params(self, input_params, var_name, fulls):
		content = ""
		if input_params is None:
			return content
		not_cond_params = []
		for param in input_params:
			is_cond = param.get(CSqlParse.PARAM_IS_CONDITION)
			if is_cond is False:
				not_cond_params.append(param)
		length = len(fulls)
		if length > 0:
			content += ", "
		i = 0
		for number, keyword in fulls:
			param = input_params[number]
			# is_cond = param.get(CSqlParse.PARAM_IS_CONDITION)
			# if is_cond is True:
			# 	continue
			i += 1
			param_name = param.get(CSqlParse.PARAM_NAME)
			param_type = param.get(CSqlParse.PARAM_TYPE)
			content += "{0}.{1}".format(var_name, CStringTools.upperFirstByte(param_name))
			if i < length:
				content += ", "
		return content

	def __write_stuct(self):
		content = ""
		content += "type {0} struct ".format(self.get_class_name()) + " {\n"
		content += "\t"*1 + "m_db *sql.DB\n"
		content += "}\n\n"
		return content

	def __write_connect(self):
		content = ""
		content += "func (this *CDbHandler) Connect(host string, port uint, username string, userpwd string, dbname string, dbtype string) (err error) {\n"
		content += "\t"*1 + "b := bytes.Buffer{}\n"
		content += "\t"*1 + "b.WriteString(username)\n"
		content += "\t"*1 + 'b.WriteString(":")\n'
		content += "\t"*1 + 'b.WriteString(userpwd)\n'
		content += "\t"*1 + 'b.WriteString("@tcp(")\n'
		content += "\t"*1 + 'b.WriteString(host)\n'
		content += "\t"*1 + 'b.WriteString(":")\n'
		content += "\t"*1 + 'b.WriteString(strconv.FormatUint(uint64(port), 10))\n'
		content += "\t"*1 + 'b.WriteString(")/")\n'
		content += "\t"*1 + 'b.WriteString(dbname)\n'
		content += "\t"*1 + 'var name string\n'
		content += "\t"*1 + 'if dbtype == "mysql" {\n'
		content += "\t"*2 + 'name = b.String()\n'
		content += "\t"*1 + '} else if dbtype == "sqlite3" {\n'
		content += "\t"*2 + 'name = dbname\n'
		content += "\t"*1 + '} else {\n'
		content += "\t"*2 + 'return errors.New("dbtype not support")\n'
		content += "\t"*1 + '}\n'
		content += "\t"*1 + 'this.m_db, err = sql.Open(dbtype, name)\n'
		content += "\t"*1 + 'if err != nil {\n'
		content += "\t"*2 + 'return err\n'
		content += "\t"*1 + '}\n'
		content += "\t"*1 + 'this.m_db.SetMaxOpenConns(2000)\n'
		content += "\t"*1 + 'this.m_db.SetMaxIdleConns(1000)\n'
		content += "\t"*1 + 'this.m_db.Ping()\n'
		content += "\t"*1 + 'return nil\n'
		content += "}\n\n"
		return content

	def __write_connect_by_rule(self):
		content = ""
		content += "func (this *CDbHandler) ConnectByRule(rule string, dbtype string) (err error) {\n"
		content += "\t"*1 + 'this.m_db, err = sql.Open(dbtype, rule)\n'
		content += "\t"*1 + 'if err != nil {\n'
		content += "\t"*2 + 'return err\n'
		content += "\t"*1 + '}\n'
		content += "\t"*1 + 'this.m_db.SetMaxOpenConns(2000)\n'
		content += "\t"*1 + 'this.m_db.SetMaxIdleConns(1000)\n'
		content += "\t"*1 + 'this.m_db.Ping()\n'
		content += "\t"*1 + 'return nil\n'
		content += "}\n\n"
		return content

	def __write_connect_by_cfg(self):
		content = ""
		content += "func (this *CDbHandler) ConnectByCfg(path string) error {\n"
		content += "\t"*1 + 'fi, err := os.Open(path)\n'
		content += "\t"*1 + 'if err != nil {\n'
		content += "\t"*2 + 'return err\n'
		content += "\t"*1 + '}\n'
		content += "\t"*1 + 'defer fi.Close()\n'
		content += "\t"*1 + 'br := bufio.NewReader(fi)\n'
		content += "\t"*1 + 'var host string = "localhost"\n'
		content += "\t"*1 + 'var port uint = 3306\n'
		content += "\t"*1 + 'var username string = "root"\n'
		content += "\t"*1 + 'var userpwd string = "123456"\n'
		content += "\t"*1 + 'var dbname string = "test"\n'
		content += "\t"*1 + 'var dbtype string = "mysql"\n'
		content += "\t"*1 + 'for {\n'
		content += "\t"*2 + 'a, _, c := br.ReadLine()\n'
		content += "\t"*2 + 'if c == io.EOF {\n'
		content += "\t"*3 + 'break\n'
		content += "\t"*2 + '}\n'
		content += "\t"*2 + 'content := string(a)\n'
		content += "\t"*2 + 'r, _ := regexp.Compile("(.*)?=(.*)?")\n'
		content += "\t"*2 + 'ret := r.FindStringSubmatch(content)\n'
		content += "\t"*2 + 'if len(ret) != 3 {\n'
		content += "\t"*3 + 'continue\n'
		content += "\t"*2 + '}\n'
		content += "\t"*2 + 'k := ret[1]\n'
		content += "\t"*2 + 'v := ret[2]\n'
		content += "\t"*2 + 'switch k {\n'
		content += "\t"*2 + 'case "host":\n'
		content += "\t"*3 + 'host = v\n'
		content += "\t"*2 + 'case "port":\n'
		content += "\t"*3 + 'port_tmp, _ := strconv.ParseUint(v, 10, 32)\n'
		content += "\t"*3 + 'port = uint(port_tmp)\n'
		content += "\t"*2 + 'case "username":\n'
		content += "\t"*3 + 'username = v\n'
		content += "\t"*2 + 'case "userpwd":\n'
		content += "\t"*3 + 'userpwd = v\n'
		content += "\t"*2 + 'case "dbname":\n'
		content += "\t"*3 + 'dbname = v\n'
		content += "\t"*2 + 'case "dbtype":\n'
		content += "\t"*3 + 'dbtype = v\n'
		content += "\t"*2 + '}\n'
		content += "\t"*1 + '}\n'
		content += "\t"*1 + 'return this.Connect(host, port, username, userpwd, dbname, dbtype)\n'
		content += "}\n\n"
		return content

	def __write_disconnect(self):
		content = ""
		content += "func (this *CDbHandler) Disconnect() {\n"
		content += "\t"*1 + 'this.m_db.Close()\n'
		content += "}\n\n"
		return content

	def __write_create(self, create_sql, create_functions):
		content = ""
		create_sql = re.sub(r"\\", "", create_sql)
		sqls = create_sql.split(";")
		content += "func (this *CDbHandler) Create() (error) {\n"
		content += "\t"*1 + "var err error = nil\n"
		content += "\t"*1 + "var _ error = err\n"
		def err_content():
			con = ""
			con += "\t"*1 + "if err != nil {\n"
			con += "\t"*2 + "return err\n"
			con += "\t"*1 + "}\n"
			return con
		for sql in sqls:
			if sql == "":
				continue
			content += "\t"*1 + "_, err = this.m_db.Exec(`{0}`)\n".format(sql + ";")
			content += err_content()
		for sql in create_functions:
			content += "\t"*1 + "_, err = this.m_db.Exec(`{0}`)\n".format(sql)
			content += err_content()
		content += "\t"*1 + "return nil\n"
		content += "}\n\n"
		return content

	def __write_header(self, namespace):
		self.m_content += "package {0}\n\n".format(namespace)
		self.m_content += "import (\n"
		self.m_content += "\t"*1 + '"{0}"\n'.format("bufio")
		self.m_content += "\t"*1 + '"{0}"\n'.format("bytes")
		self.m_content += "\t"*1 + '"{0}"\n'.format("database/sql")
		self.m_content += "\t"*1 + '"{0}"\n'.format("io")
		self.m_content += "\t"*1 + '"{0}"\n'.format("os")
		self.m_content += "\t"*1 + '"{0}"\n'.format("regexp")
		self.m_content += "\t"*1 + '"{0}"\n'.format("strconv")
		self.m_content += "\t"*1 + '"{0}"\n'.format("fmt")
		self.m_content += "\t"*1 + '"{0}"\n'.format("errors")
		self.m_content += ")\n\n"


if __name__ == "__main__":
	parser = CSqlParse("./file/user_info.sql")
	parser.read()
	info_dict = parser.get_info_dict()
	writer = CWriteInterface(parser, parser.get_file_path(), root="./obj")
	writer.write(info_dict)
