#!/bin/bash
DBNAME=lopos
if [ ! -z "$1" ]; then
    DBNAME=$1
fi
USER=lopos
if [ ! -z "$2" ]; then
    USER=$2
fi
PASS=lopos
#pass equal to nouser will no create a new user!
if [ ! -z "$3" ]; then
    PASS=$3
fi

printf "uninstall plugin validate_password;"
printf "create database IF NOT EXISTS %s;\n" $DBNAME
printf "use mysql;\n"
if [ ! "$PASS" = "nouser" ]; then  
    printf "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';\n" $USER $PASS
    printf "CREATE USER '%s'@'%%' IDENTIFIED BY '%s';\n" $USER $PASS
fi
printf "insert into db (host,Db,User) values(\"localhost\",\"%s\",\"%s\");\n" $DBNAME $USER
printf "insert into db (host,Db,User) values(\"%%\",\"%s\",\"%s\");\n\n" $DBNAME $USER
printf "insert into tables_priv values ("localhost", \"%%\", \"%%\", \"todo\", \"root@localhost\", now(), \"delete,update\", \"\" );\n\n" $DBNAME $USER
printf "insert into tables_priv values ("localhost", \"%%\", \"%%\", \"sys\", \"root@localhost\", now(), \"update\", \"\" );\n\n" $DBNAME $USER

printf "update db set 
Select_priv = \"Y\", 
Insert_priv = \"Y\", 
Update_priv = \"N\", 
Delete_priv = \"N\", 
Index_priv  = \"Y\", 
Execute_priv  = \"Y\", 
Create_view_priv = \"Y\", 
Show_view_priv = \"Y\" 
where user = \"%s\" AND host=\"localhost\";\n\n"  $USER

printf "update db set 
Select_priv = \"Y\", 
Insert_priv = \"Y\", 
Update_priv = \"N\", 
Delete_priv = \"N\", 
Index_priv  = \"Y\", 
Execute_priv  = \"Y\", 
Create_view_priv = \"Y\", 
Show_view_priv = \"Y\" 
where user = \"%s\" AND host=\"%%\";\n\n" $USER




printf "flush privileges;\n"
printf "use %s;\n"  $DBNAME
printf "#please execute:\n#\tmysql -u root -p < this_output.sql\n"