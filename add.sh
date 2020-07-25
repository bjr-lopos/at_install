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
id=$(($1+$offset))
interval=320
if [ ! -z "$2" ]; then
    interval=$2
fi
devsql=`printf "insert into device values (%d, \"$profile%d\", 3, now());" $id $1`
plansql=`printf "insert into plan values (%d, 12, $interval);" $id`
echo $devsql $plansql
echo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$devsql"
echo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$plansql"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$devsql"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$plansql"

