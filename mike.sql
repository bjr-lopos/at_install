use mysql;
CREATE USER 'mike'@'%' IDENTIFIED BY 'mpa@ilvo';
insert into db (host,Db,User) values("%","ilvo","mike");
insert into tables_priv values ("%", "ilvo", "mike", "position", "root@localhost", now(), "select", "" );

update db set 
Select_priv = "Y", 
Insert_priv = "N", 
Update_priv = "N", 
Delete_priv = "N", 
Index_priv  = "N", 
Execute_priv  = "Y", 
Create_view_priv = "N", 
Show_view_priv = "Y" 
where user = "mike" AND host="%";

flush privileges;
