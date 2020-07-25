#!/bin/bash
lclDir=`dirname $0`
source $lclDir/local_cfg
id=$(($1+4096))
devsql=`printf "insert into device values (%d, \"tag%d\", 3, now());" $id $id`
plansql=`printf "insert into plan values (%d, 12, 320);" $id`
echo $devsql $plansql
echo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$devsql"
echo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$plansql"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$devsql"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$plansql"

