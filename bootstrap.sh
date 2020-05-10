#!/bin/bash
loposCoreBin=/usr/local/bin/loposcore
LoposCoreService=/etc/systemd/system/loposcore.service
LocalData=/tmp/loposdb_data.sql

ROOTUSER=-uroot
ROOTPASS=-pLoPoS
if [ -e ./rootpass ]; then
    ROOTPASS=`cat ./rootpass`
fi  
echo will use :$ROOTUSER:$ROOTPASS:
sleep 2
USERLOGIN=terec
#USERPASS=nouser
USERPASS=t3r3c
TARGET_DB=terec

buildDB() {
createUserTemp=/tmp/loposdb_cu.sql
delUserTemp=/tmp/loposdb_du.sql
delDBTemp=/tmp/loposdb_dd.sql

if [ -z "$PARAM" ]; then
    PARAM="AU IS FD T1"
fi
if [ ! -z "$1" ]; then
    if [ "$1" = "-v" ]; then
        shift
    fi
    PARAM="$*"
fi

echo "Will prep deldb, in case we would need in a next run/update and schema is updated"
if [ ! -e $delDBTemp ]; then
    ./deldb.sh $TARGET_DB `echo $ROOTUSER | cut -c 3-` `echo $ROOTPASS | cut -c 3-` > $delDBTemp
fi

echo "Will prep deluser, in case we would need in a next run/update, and is updated."
if [ ! -e $delUserTemp ]; then
    ./deluser.sh $TARGET_DB $USERLOGIN $USERPASS > $delUserTemp
fi


if echo "$PARAM" | grep 'AU'; then
    echo "add user, database and access to it: sudo mysql  $ROOTUSER $ROOTPASS < $createUserTemp"
    ./initdb.sh $TARGET_DB $USERLOGIN $USERPASS > $createUserTemp
    sudo mysql  $ROOTUSER $ROOTPASS < $createUserTemp
fi

if echo "$PARAM" | grep 'IS'; then
    echo "install schema: sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB < lopos_schema.sql"
    sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB < lopos_schema.sql
fi

if echo "$PARAM" | grep 'FD'; then
    echo "flood the device table: sudo mysql  $ROOTUSER $ROOTPASS $TARGET_DB < device.sql"
    sudo mysql  $ROOTUSER $ROOTPASS $TARGET_DB < device.sql
fi

if echo "$PARAM" | grep 'T1'; then
    echo "Verify, changes to the schema can be store by using CS"
    sudo mysql  $ROOTUSER $ROOTPASS $TARGET_DB
fi

if echo "$PARAM" | grep 'DD'; then
    echo "delete database: sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB < $delDBTemp"
    sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB < $delDBTemp
    rm $delDBTemp
fi

if echo "$PARAM" | grep 'DU'; then
    echo "delete user: sudo  mysql $ROOTUSER $ROOTPASS < $delUserTemp"
    sudo mysql $ROOTUSER $ROOTPASS < $delUserTemp
    rm $delUserTemp    
fi

}


createService() {
LoposCoreServiceTmp=/tmp/`basename $LoposCoreService`
cat << EOT > $LoposCoreServiceTmp
[Unit]
Description=loposcore service
#Requires=mysql.service
#After=mysql.service

[Service]
Environment=SERIAL_PORT=/dev/ttyUSB0
ExecStart=$loposCoreBin dev=\${SERIAL_PORT} db_user=$USERLOGIN db_pass=$USERPASS db_name=$TARGET_DB dumpFrames2Log=no dumpHdlInfo2Log=0000000000100000000 dumpGenInfo2Log=01001
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=lcs

[Install]
#WantedBy=multi-user.target mysql.service
WantedBy=multi-user.target
EOT

sudo cp $LoposCoreServiceTmp $LoposCoreService

}


#`service loposcore log | grep unrecognized` 
#if 
if [ ! -e $LoposCoreService ]; then
    echo "$LoposCoreService not found"
    sudo apt-get update
    export DEBIAN_FRONTEND=noninteractive
    if [ -z "`dpkg -l | grep mysql-server`"]; then
        sudo -E apt-get -q -y install mysql-server
        sudo mysqladmin `echo $ROOTPASS | cut -c 3-` 
        sudo sed 's/\(^.*bind-address.*$\)/#\1/' -i /etc/mysql/mysql.conf.d/mysqld.cnf
        sudo service mysql restart
    fi
    if [ -z "`dpkg -l | grep libmysqlclient-dev`"]; then
        sudo -E apt-get -q -y install libmysqlclient-dev
    fi
    PARAM="AU IS FD"
    mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e 'insert into sys values (FROM_UNIXTIME(1585692000), 165, 60, 4915);'    
    ldconfig /usr/local/lib
    buildDB
else 
    echo "will run: sudo mysqldump -u$USERLOGIN -p$USERPASS --skip-triggers --compact --no-create-info $TARGET_DB > $LocalData"
    sudo mysqldump -u$USERLOGIN -p$USERPASS --skip-triggers --compact --no-create-info $TARGET_DB > $LocalData

    PARAM="DD"
    buildDB

    sudo service loposcore stop
    sudo systemctl disable loposcore.service
    PARAM="IS"
    buildDB
    echo "Will run: mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e 'insert into sys values (FROM_UNIXTIME(1585692000), 165, 60, 4915);'"
    mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e 'insert into sys values (FROM_UNIXTIME(1585692000), 165, 60, 4915);'    
    sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData
fi

createService
sudo cp loposcore $loposCoreBin
sudo cp libpaho-mqtt3c.so.1 /usr/local/lib/
sudo systemctl enable loposcore.service
sudo systemctl start loposcore.service


