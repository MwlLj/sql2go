package user_info

import (
	"bufio"
	"bytes"
	"database/sql"
	"io"
	"os"
	"regexp"
	"strconv"
	"fmt"
	"errors"
)

type CDbHandler struct  {
	m_db *sql.DB
}

func (this *CDbHandler) Connect(host string, port uint, username string, userpwd string, dbname string, dbtype string) (err error) {
	b := bytes.Buffer{}
	b.WriteString(username)
	b.WriteString(":")
	b.WriteString(userpwd)
	b.WriteString("@tcp(")
	b.WriteString(host)
	b.WriteString(":")
	b.WriteString(strconv.FormatUint(uint64(port), 10))
	b.WriteString(")/")
	b.WriteString(dbname)
	var name string
	if dbtype == "mysql" {
		name = b.String()
	} else if dbtype == "sqlite3" {
		name = dbname
	} else {
		return errors.New("dbtype not support")
	}
	this.m_db, err = sql.Open(dbtype, name)
	if err != nil {
		return err
	}
	this.m_db.SetMaxOpenConns(2000)
	this.m_db.SetMaxIdleConns(1000)
	this.m_db.Ping()
	return nil
}

func (this *CDbHandler) ConnectByCfg(path string) error {
	fi, err := os.Open(path)
	if err != nil {
		return err
	}
	defer fi.Close()
	br := bufio.NewReader(fi)
	var host string = "localhost"
	var port uint = 3306
	var username string = "root"
	var userpwd string = "123456"
	var dbname string = "test"
	var dbtype string = "mysql"
	for {
		a, _, c := br.ReadLine()
		if c == io.EOF {
			break
		}
		content := string(a)
		r, _ := regexp.Compile("(.*)?=(.*)?")
		ret := r.FindStringSubmatch(content)
		if len(ret) != 3 {
			continue
		}
		k := ret[1]
		v := ret[2]
		switch k {
		case "host":
			host = v
		case "port":
			port_tmp, _ := strconv.ParseUint(v, 10, 32)
			port = uint(port_tmp)
		case "username":
			username = v
		case "userpwd":
			userpwd = v
		case "dbname":
			dbname = v
		case "dbtype":
			dbtype = v
		}
	}
	return this.Connect(host, port, username, userpwd, dbname, dbtype)
}

func (this *CDbHandler) Disconnect() {
	this.m_db.Close()
}

func (this *CDbHandler) Create() (error) {
	var err error = nil
	var _ error = err
	_, err = this.m_db.Exec(`create table if not exists user_info(
	id integer primary key auto_increment,
	username varchar(32),
	userage int
);`)
	if err != nil {
		return err
	}
	_, err = this.m_db.Exec(`
create table if not exists user_info(
	id integer primary key auto_increment,
	username varchar(32),
	userage int
);`)
	if err != nil {
		return err
	}
	_, err = this.m_db.Exec(`
create table if not exists user_info(
	id integer primary key auto_increment,
	username varchar(32),
	userage int
);`)
	if err != nil {
		return err
	}
	return nil
}

func (this *CDbHandler) AddUserinfo(input0 *[]CAddUserinfoInput) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	for _, v := range *input0 {
		result, err = this.m_db.Exec(fmt.Sprintf(`insert into user_info values(null, ?, ?);`), v.Username, v.Userage)
		if err != nil {
			tx.Rollback()
			return err, rowCount
		}
	}
		var _ = result
	tx.Commit()
	return nil, rowCount
}

func (this *CDbHandler) GetUserinfoById(input0 *CGetUserinfoByIdInput, output0 *CGetUserinfoByIdOutput) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	result, err = this.m_db.Exec(fmt.Sprintf(`select * from user_info
where id = ?;`), input0.Id)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	tx.Commit()
	var _ = result
	return nil, rowCount
}

func (this *CDbHandler) GetAllUserinfo(output0 *[]CGetAllUserinfoOutput) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	rows, err := this.m_db.Query(fmt.Sprintf(`select * from user_info;`))
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	tx.Commit()
	defer rows.Close()
	for rows.Next() {
		rowCount += 1
		tmp := CGetAllUserinfoOutput{}
		var id sql.NullInt64
		var username sql.NullString
		var userage sql.NullInt64
		scanErr := rows.Scan(&id, &username, &userage)
		if scanErr != nil {
			continue
		}
		tmp.Id = int(id.Int64)
		tmp.Username = username.String
		tmp.Userage = int(userage.Int64)
		*output0 = append(*output0, tmp)
	}
	return nil, rowCount
}

func (this *CDbHandler) DeleteUser(input0 *[]CDeleteUserInput) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	for _, v := range *input0 {
		result, err = this.m_db.Exec(fmt.Sprintf(`delete from user_info where id = ?;`), v.Id)
		if err != nil {
			tx.Rollback()
			return err, rowCount
		}
	}
		var _ = result
	tx.Commit()
	return nil, rowCount
}

func (this *CDbHandler) UpdateUsername(input0 *CUpdateUsernameInput) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	result, err = this.m_db.Exec(fmt.Sprintf(`update user_info set username = ? where id = ?;`), input0.Username, input0.Id)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	tx.Commit()
	var _ = result
	return nil, rowCount
}

func (this *CDbHandler) UpdateUsername2(input0 *CUpdateUsername2Input) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	result, err = this.m_db.Exec(fmt.Sprintf(`update user_info set username = ? where id = ?;`), input0.Username, input0.Id)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	tx.Commit()
	var _ = result
	return nil, rowCount
}

func (this *CDbHandler) UpdateUsername3(input0 *CUpdateUsername3Input) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	result, err = this.m_db.Exec(fmt.Sprintf(`update user_info set username = ? %s;`, input0.Condition), input0.Username)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	tx.Commit()
	var _ = result
	return nil, rowCount
}

func (this *CDbHandler) SubTest(input0 *CUpdateUsernameInput, input1 *CSubTestInput, input2 *[]CDeleteUserInput) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	result, err = this.m_db.Exec(fmt.Sprintf(`update user_info set username = ? where id = ?;`), input0.Username, input0.Id)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	result, err = this.m_db.Exec(fmt.Sprintf(`insert into user_info values(null, ?, ?);`), input1.UserName, input1.UserAge)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	for _, v := range *input2 {
		result, err = this.m_db.Exec(fmt.Sprintf(`delete from user_info where id = ?;`), v.Id)
		if err != nil {
			tx.Rollback()
			return err, rowCount
		}
	}
	tx.Commit()
	var _ = result
	return nil, rowCount
}

func (this *CDbHandler) SubTestPro(input0 *CUpdateUsernameInput, input1 *CSubTestInput, input2 *[]CDeleteUserInput, input3 *CSubTestProInput, input4 *[]CAddUserinfoInput) (error, uint64) {
	var rowCount uint64 = 0
	tx, _ := this.m_db.Begin()
	var result sql.Result
	var _ = result
	var err error
	result, err = this.m_db.Exec(fmt.Sprintf(`update user_info set username = ? where id = ?;`), input0.Username, input0.Id)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	result, err = this.m_db.Exec(fmt.Sprintf(`insert into user_info values(null, ?, ?);`), input1.UserName, input1.UserAge)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	for _, v := range *input2 {
		result, err = this.m_db.Exec(fmt.Sprintf(`delete from user_info where id = ?;`), v.Id)
		if err != nil {
			tx.Rollback()
			return err, rowCount
		}
	}
	result, err = this.m_db.Exec(fmt.Sprintf(`insert into user_info values(null, ?, ?);`), input3.UserName, input3.UserAge)
	if err != nil {
		tx.Rollback()
		return err, rowCount
	}
	for _, v := range *input4 {
		result, err = this.m_db.Exec(fmt.Sprintf(`insert into user_info values(null, ?, ?);`), v.Username, v.Userage)
		if err != nil {
			tx.Rollback()
			return err, rowCount
		}
	}
	tx.Commit()
	var _ = result
	return nil, rowCount
}

