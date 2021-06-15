#!/bin/bash
lclDir=`dirname $0`
source $lclDir/local_cfg
offset=4096
profile=tag
if [ "$1" = "tag" ]; then
    offset=4096
    profile=tag
    shift
elif [ "$1" = "anchor" ]; then
    offset=40960
    profile=anchor
    shift
elif [ "$1" = "sink" ]; then
    offset=65520
    profile=sink
    shift
else
    echo "Warning default profile is $profile"
fi
id=$1
addr=$(($id+$offset))
interval=320
if [ ! -z "$2" ]; then
    interval=$2
fi
devsql=`printf "insert into device values (%d, \"%s%d\", 3, now(),0);" $addr $profile $id`
plansql=`printf "insert into plan values (%d, 12, $interval);" $addr`
prosql=`printf "insert into %s values (%d, %d, 1);" $profile $id $addr`
echo $devsql $plansql $prosql
echo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$devsql"
echo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$plansql"
echo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$plansql"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$devsql"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$plansql"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$prosql"

