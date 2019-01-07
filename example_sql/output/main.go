package main

import (
	db "./user_info"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
)

func main() {
	dbHandler := db.CDbHandler{}
	err := dbHandler.Connect("localhost", 3306, "root", "123456", "test", "mysql")
	defer dbHandler.Disconnect()
	if err != nil {
		fmt.Println("connect faild")
		return
	}
	input := db.CUpdateUsername3Input{}
	input.Condition = `where username = ""`
	input.Username = "liujun"
	err, _ = dbHandler.UpdateUsername3(&input)
	if err != nil {
		fmt.Println("update username faild")
		return
	}
	fmt.Println("success")
}
