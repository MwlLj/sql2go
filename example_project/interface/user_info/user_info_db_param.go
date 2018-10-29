package user_info

type CAddUserinfoInput struct {
	Username string
	Userage int
}

type CGetUserinfoByIdInput struct {
	Id int
}

type CGetUserinfoByIdOutput struct {
	Id int
	Username string
	Userage int
}

type CGetAllUserinfoOutput struct {
	Id int
	Username string
	Userage int
}

type CDeleteUserInput struct {
	Id int
}

type CUpdateUsernameInput struct {
	Username string
	Id int
}

type CUpdateUsername2Input struct {
	Id int
	Username string
}

type CUpdateUsername3Input struct {
	Condition string
	Username string
}

