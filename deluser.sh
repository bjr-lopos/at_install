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

printf "use mysql;"
printf "DROP USER '%s'@'localhost';\n" $USER
printf "DROP USER '%s'@'%%';\n" $USER
printf "DROP database IF EXISTS %s;\n" $DBNAME
printf "flush privileges;\n"

