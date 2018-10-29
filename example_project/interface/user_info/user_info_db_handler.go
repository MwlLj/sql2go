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
)

type CDbHandler struct  {
	m_db *sql.DB
}

func (this *CDbHandler) Connect(host string, port uint, username string, userpwd string, dbname string) (err error) {
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
	this.m_db, err = sql.Open("mysql", b.String())
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
		}
	}
	return this.Connect(host, port, username, userpwd, dbname)
}

func (this *CDbHandler) Disconnect() {
	this.m_db.Close()
}

func (this *CDbHandler) AddUserinfo(input *CAddUserinfoInput) (error) {
	stmt, err := this.m_db.Prepare(fmt.Sprintf(`insert into user_info values(null, ?, ?);`))
	if err != nil {
		return err
	}
	defer stmt.Close()
	rows, err := stmt.Query(input.Username, input.Userage)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
	}
	return nil
}

func (this *CDbHandler) GetUserinfoById(input *CGetUserinfoByIdInput, output *CGetUserinfoByIdOutput) (error) {
	stmt, err := this.m_db.Prepare(fmt.Sprintf(`select * from user_info\
where id = ?;`))
	if err != nil {
		return err
	}
	defer stmt.Close()
	rows, err := stmt.Query(input.Id)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		var id int
		var username string
		var userage int
		scanErr := rows.Scan(&id, &username, &userage)
		if scanErr != nil {
			continue
		}
		output.Id = id
		output.Username = username
		output.Userage = userage
	}
	return nil
}

func (this *CDbHandler) GetAllUserinfo(output *[]CGetAllUserinfoOutput) (error) {
	stmt, err := this.m_db.Prepare(fmt.Sprintf(`select * from user_info;`))
	if err != nil {
		return err
	}
	defer stmt.Close()
	rows, err := stmt.Query()
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
		tmp := CGetAllUserinfoOutput{}
		var id int
		var username string
		var userage int
		scanErr := rows.Scan(&id, &username, &userage)
		if scanErr != nil {
			continue
		}
		tmp.Id = id
		tmp.Username = username
		tmp.Userage = userage
		*output = append(*output, tmp)
	}
	return nil
}

func (this *CDbHandler) DeleteUser(input *[]CDeleteUserInput) (error) {
	stmt, err := this.m_db.Prepare(fmt.Sprintf(`delete from user_info where id = ?;`))
	if err != nil {
		return err
	}
	defer stmt.Close()
	for _, v := range *input {
		rows, err := stmt.Query(v.Id)
		if err != nil {
			continue
		}
		defer rows.Close()
		for rows.Next() {
		}
	}
	return nil
}

func (this *CDbHandler) UpdateUsername(input *CUpdateUsernameInput) (error) {
	stmt, err := this.m_db.Prepare(fmt.Sprintf(`update user_info set username = ? where id = ?;`))
	if err != nil {
		return err
	}
	defer stmt.Close()
	rows, err := stmt.Query(input.Username, input.Id)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
	}
	return nil
}

func (this *CDbHandler) UpdateUsername2(input *CUpdateUsername2Input) (error) {
	stmt, err := this.m_db.Prepare(fmt.Sprintf(`update user_info set username = ? where id = ?;`))
	if err != nil {
		return err
	}
	defer stmt.Close()
	rows, err := stmt.Query(input.Username, input.Id)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
	}
	return nil
}

func (this *CDbHandler) UpdateUsername3(input *CUpdateUsername3Input) (error) {
	stmt, err := this.m_db.Prepare(fmt.Sprintf(`update user_info set username = ? %s;`, input.Condition))
	if err != nil {
		return err
	}
	defer stmt.Close()
	rows, err := stmt.Query(input.Username)
	if err != nil {
		return err
	}
	defer rows.Close()
	for rows.Next() {
	}
	return nil
}

