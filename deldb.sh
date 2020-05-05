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
if [ ! -z "$3" ]; then
    PASS=$3
fi

printf "SET FOREIGN_KEY_CHECKS = 0;"
#Then dump the db with no data and drop all tables:
mysqldump --add-drop-table --no-data -u$USER -p$PASS $DBNAME | grep 'DROP TABLE'
#Turn the foreign key check back on:
printf "SET FOREIGN_KEY_CHECKS = 1;" 
#Now restore the db with the dump file:
