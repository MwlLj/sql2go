package main

import (
	"../interface/user_info"
	_ "../package/go-sql-driver/mysql"
	"fmt"
)

func main() {
	handler := user_info.CDbHandler{}
	// 连接数据库
	handler.Connect("localhost", 3306, "root", "123456", "test")
	// handler.ConnectByCfg("./mysql_cfg.txt")
	defer handler.Disconnect()
	// 测试插入一条数据
	err := handler.AddUserinfo(&user_info.CAddUserinfoInput{"liujun", 25})
	if err != nil {
		fmt.Println(err)
	}
	// 测试 cond
	err = handler.UpdateUsername3(&user_info.CUpdateUsername3Input{"where id = 1", "mawenli"})
	if err != nil {
		fmt.Println(err)
	}
}
