#namespace user_info

#create tables
/*
create table if not exists user_info(
	id integer primary key auto_increment,
	username varchar(32),
	userage int
);

create table if not exists user_info(
	id integer primary key auto_increment,
	username varchar(32),
	userage int
);
*/
#end

#create tables
/*
create table if not exists user_info(
	id integer primary key auto_increment,
	username varchar(32),
	userage int
);
*/
#end

/*
	@bref 插入记录
	@is_brace true
	@in_isarr true
	@out_isarr false
	@in username: string
	@in userage: int
*/
#define addUserinfo
insert into user_info values(null, {0}, {1});
#end

/*
	@bref 通过用户ID获取用户信息
	@is_brace true
	@in_isarr false
	@out_isarr false
	@in id: int
	@out id: int
	@out username: string
	@out userage: int
*/
#define getUserinfoById
select * from user_info
where id = {0};
#end

/*
	@bref 获取全部的人员信息
	@is_brace true
	@in_isarr false
	@out_isarr true
	@out id: int
	@out username: string
	@out userage: int
*/
#define getAllUserinfo
select * from user_info;
#end

/*
	@bref 删除一个或多个用户
	@is_brace true
	@in_isarr true
	@out_isarr false
	@in id: int
*/
#define deleteUser
delete from user_info where id = {0};
#end

/*
	@bref 更新用户名
	@is_brace true
	@in_isarr false
	@out_isarr false
	@in username: string
	@in id: int
*/
#define updateUsername
update user_info set username = {0} where id = {1};
#end

/*
	@bref 更新用户名2
	@is_brace true
	@in_isarr false
	@out_isarr false
	@in id: int
	@in username: string
*/
#define updateUsername2
update user_info set username = {1} where id = {0};
#end

/*
	@bref 更新用户名3
	@is_brace true
	@in_isarr false
	@out_isarr false
	@in condition[cond]: string
	@in username: string
*/
#define updateUsername3
update user_info set username = {1} {0};
#end

/*
	@bref 子句测试
	@is_brace true
	@in_isarr false
	@out_isarr false
	@in userName: string
	@in userAge: int
	@sub updateUsername[-1]
	@sub deleteUser[1]
*/
#define subTest
insert into user_info values(null, {0}, {1});
#end

/*
	@bref 子句测试pro
	@is_brace true
	@in_isarr false
	@out_isarr false
	@in userName: string
	@in userAge: int
	@sub subTest[-1]
	@sub addUserinfo[1]
*/
#define subTestPro
insert into user_info values(null, {0}, {1});
#end
