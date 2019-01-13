package user_info

type CAddUserinfoInput struct {
	Username string
	UsernameIsValid bool
	Userage int
	UserageIsValid bool
}

type CGetUserinfoByIdInput struct {
	Id int
	IdIsValid bool
}

type CGetUserinfoByIdOutput struct {
	Id int
	IdIsValid bool
	Username string
	UsernameIsValid bool
	Userage int
	UserageIsValid bool
}

type CGetAllUserinfoOutput struct {
	Id int
	IdIsValid bool
	Username string
	UsernameIsValid bool
	Userage int
	UserageIsValid bool
}

type CDeleteUserInput struct {
	Id int
	IdIsValid bool
}

type CUpdateUsernameInput struct {
	Username string
	UsernameIsValid bool
	Id int
	IdIsValid bool
}

type CUpdateUsername2Input struct {
	Id int
	IdIsValid bool
	Username string
	UsernameIsValid bool
}

type CUpdateUsername3Input struct {
	Condition string
	ConditionIsValid bool
	Username string
	UsernameIsValid bool
}

type CSubTestInput struct {
	UserName string
	UserNameIsValid bool
	UserAge int
	UserAgeIsValid bool
}

type CSubTestProInput struct {
	UserName string
	UserNameIsValid bool
	UserAge int
	UserAgeIsValid bool
}

type CSubOutputTestInput struct {
	UserName string
	UserNameIsValid bool
}

type CSubOutputTestOutput struct {
	UserName string
	UserNameIsValid bool
}

