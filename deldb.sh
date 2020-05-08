#!/bin/bash

DBNAME=
if [ ! -z "$1" ]; then
    DBNAME=$1
fi
USER=-uroot
if [ ! -z "$2" ]; then
    USER=-u$2
fi
PASS=
if [ ! -z "$3" ]; then
    PASS=-p$3
fi

printf "SET FOREIGN_KEY_CHECKS = 0;\n"
#Then dump the db with no data and drop all tables:

printf "#Will run inside deldb: sudo mysqldump --add-drop-table --no-data $USER $PASS $DBNAME | grep 'DROP TABLE'\n"
sudo mysqldump --add-drop-table --no-data $USER $PASS $DBNAME | grep 'DROP TABLE'
#Turn the foreign key check back on:
printf "SET FOREIGN_KEY_CHECKS = 1;\n" 
#Now restore the db with the dump file:
