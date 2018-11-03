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
	def __init__(self, file_path, root="."):
		self.m_file_handler = CFileHandle()
		self.m_file_name = ""
		self.m_file_path = ""
		self.m_content = ""
		self.m_namespace = ""
		self.m_procedure_info_list = []
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
			method_define = ""
			func_name = method.get(CSqlParse.FUNC_NAME)
			method_name = self.get_interface_name(func_name)
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
			input_params = method.get(CSqlParse.INPUT_PARAMS)
			output_params = method.get(CSqlParse.OUTPUT_PARAMS)
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
				method_define += "{0}()".format(method_name)
			elif input_params_len > 0 and output_params_len == 0:
				method_define += "{0}(input *{1})".format(method_name, input_str)
			elif input_params_len == 0 and output_params_len > 0:
				method_define += "{0}(output *{1})".format(method_name, output_str)
			elif input_params_len > 0 and output_params_len > 0:
				method_define += "{0}(input *{1}, output *{2})".format(method_name, input_str, output_str)
			else:
				return content
			content += "func (this *{0}) ".format(self.get_class_name()) + method_define + " (error) {\n"
			sql = method.get(CSqlParse.SQL)
			sql = re.sub(r"\\", "", sql)
			content += self.get_method_imp(input_params, output_params, output_class_name, in_ismul, out_ismul, sql)
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

	def get_method_imp(self, input_params, output_params, output_class_name, in_ismul, out_ismul, sql):
		content = ""
		sql, fulls = self.__replace_sql_brace(input_params, sql, False)
		content += "\t"*1 + 'stmt, err := this.m_db.Prepare(fmt.Sprintf(`{0}`'.format(sql)
		if input_params is not None:
			for param in input_params:
				is_cond = param.get(CSqlParse.PARAM_IS_CONDITION)
				if is_cond is True:
					param_name = param.get(CSqlParse.PARAM_NAME)
					content += ", input.{0}".format(CStringTools.upperFirstByte(param_name))
		content += "))\n"
		content += "\t"*1 + 'if err != nil {\n'
		content += "\t"*2 + 'return err\n'
		content += "\t"*1 + '}\n'
		content += "\t"*1 + 'defer stmt.Close()\n'
		content += self.__write_input(in_ismul, input_params, fulls)
		tc = 1
		end_str = "return err"
		if in_ismul is True:
			tc = 2
			end_str = "continue"
		if in_ismul is False:
			content += "\t"*1 + "tx.Commit()\n"
		content += "\t"*tc + 'if err != nil {\n'
		content += "\t"*(tc+1) + '{0}\n'.format(end_str)
		content += "\t"*tc + '}\n'
		content += "\t"*tc + 'defer rows.Close()\n'
		content += "\t"*tc + 'for rows.Next() {\n'
		content += self.__write_output(output_class_name, output_params, out_ismul)
		content += "\t"*tc + '}\n'
		if in_ismul is True:
			content += "\t"*1 + "}\n"
			content += "\t"*1 + "tx.Commit()\n"
		content += "\t"*1 + 'return nil\n'
		return content

	def __write_input(self, in_ismul, input_params, fulls):
		content = ""
		tc = 1
		var_name = "input"
		content += "\t"*1 + "tx, _ := this.m_db.Begin()\n"
		if in_ismul is True:
			tc = 2
			var_name = "v"
			content += "\t"*1 + "for _, v := range *input {\n"
		content += "\t"*tc + "rows, err := stmt.Query("
		content += self.__write_query_params(input_params, var_name, fulls)
		content += ")\n"
		return content

	def __write_output(self, output_class_name, output_params, out_ismul):
		content = ""
		length = 0
		if output_params is not None:
			length = len(output_params)
		if length == 0:
			return content
		if out_ismul is True:
			content += "\t"*2 + "tmp := {0}".format(output_class_name) + "{}\n"
		else:
			pass
		for param in output_params:
			param_type = param.get(CSqlParse.PARAM_TYPE)
			param_name = param.get(CSqlParse.PARAM_NAME)
			param_type = self.type_change(param_type)
			content += "\t"*2 + "var {0} {1}\n".format(param_name, param_type)
		content += "\t"*2 + "scanErr := rows.Scan("
		i = 0
		for param in output_params:
			i += 1
			param_name = param.get(CSqlParse.PARAM_NAME)
			content += "&{0}".format(param_name)
			if i < length:
				content += ", "
		content += ")\n"
		content += "\t"*2 + "if scanErr != nil {\n"
		content += "\t"*3 + "continue\n"
		content += "\t"*2 + "}\n"
		pre = ""
		if out_ismul is True:
			pre = "tmp"
		else:
			pre = "output"
		for param in output_params:
			param_name = param.get(CSqlParse.PARAM_NAME)
			content += "\t"*2 + "{0}.{1} = {2}\n".format(pre, CStringTools.upperFirstByte(param_name), param_name)
		if out_ismul is True:
			content += "\t"*2 + "*output = append(*output, tmp)\n"
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
		length = len(not_cond_params)
		i = 0
		for number, keyword in fulls:
			param = input_params[number]
			is_cond = param.get(CSqlParse.PARAM_IS_CONDITION)
			if is_cond is True:
				continue
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
		content += "func (this *CDbHandler) Connect(host string, port uint, username string, userpwd string, dbname string) (err error) {\n"
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
		content += "\t"*1 + 'this.m_db, err = sql.Open("mysql", b.String())\n'
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
		content += "\t"*2 + '}\n'
		content += "\t"*1 + '}\n'
		content += "\t"*1 + 'return this.Connect(host, port, username, userpwd, dbname)\n'
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
		self.m_content += ")\n\n"


if __name__ == "__main__":
	parser = CSqlParse("./file/user_info.sql")
	parser.read()
	info_dict = parser.get_info_dict()
	writer = CWriteInterface(parser.get_file_path(), root="./obj")
	writer.write(info_dict)
