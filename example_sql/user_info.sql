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
	@bref 插入一条记录
	@is_brace true
	@in_isarr false
	@out_isarr false
	@in username: string
	@in userage: int
*/
#define add_userinfo
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
#define get_userinfo_by_id
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
#define get_all_userinfo
select * from user_info;
#end

/*
	@bref 删除一个或多个用户
	@is_brace true
	@in_isarr true
	@out_isarr false
	@in id: int
*/
#define delete_user
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
#define update_username
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
#define update_username_2
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
#define update_username_3
update user_info set username = {1} {0};
#end
