#!/bin/bash
loposCoreBin=/usr/local/bin/loposcore
ROOTPASS=LoPoS
USERLOGIN=terec
#USERPASS=nouser
USERPASS=t3r3c
TARGET_DB=terec

installDB() {
createUserTemp=/tmp/loposdb_cu.sql

PARAM="AU IS FD T1"
if [ ! -z "$1" ]; then
    if [ "$1" = "-v" ]; then
        shift
    fi
    PARAM="$*"
fi


if echo "$PARAM" | grep 'AU'; then
    echo "add user, database and access to it"
    ./initdb.sh $TARGET_DB $USERLOGIN $USERPASS > $createUserTemp
    mysql -uroot -p$ROOTPASS < $createUserTemp
fi

if echo "$PARAM" | grep 'IS'; then
    echo "install schema"
    mysql -uroot -p$ROOTPASS $TARGET_DB < lopos_schema.sql
fi

if echo "$PARAM" | grep 'FD'; then
    echo "flood the device table"
    mysql -uroot -p$ROOTPASS $TARGET_DB < device.sql
fi

if echo "$PARAM" | grep 'T1'; then
    echo "Verify, changes to the schema can be store by using CS"
    mysql -uroot -p$ROOTPASS $TARGET_DB
fi
}


createService() {
LOPOSCORE_SERVICE=/tmp/loposcore.service
cat << EOT > $LOPOSCORE_SERVICE
[Unit]
Description=loposcore service
#Requires=mysql.service
#After=mysql.service

[Service]
Environment=SERIAL_PORT=/dev/ttyUSB0
ExecStart=/usr/local/bin/loposcore dev=\${SERIAL_PORT} db_user=$USERLOGIN db_pass=$USERPASS db_name=$TARGET_DB dumpFrames2Log=no dumpHdlInfo2Log=000000000100010000 dumpGenInfo2Log=0101
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=lcs

[Install]
#WantedBy=multi-user.target mysql.service
WantedBy=multi-user.target
EOT

sudo cp $LOPOSCORE_SERVICE /etc/systemd/system/

}


#`service loposcore log | grep unrecognized` 
#if 
if [ ! -e $loposCoreBin ]; then
    sudo apt-get update
    export DEBIAN_FRONTEND=noninteractive
	sudo -E apt-get -q -y install mysql-server
    sudo mysqladmin -u root password $ROOTPASS
    sudo sed 's/\(^.*bind-address.*$\)/#\1/' -i /etc/mysql/mysql.conf.d/mysqld.cnf
    sudo service mysql restart
    installDB
    createService
else 
    sudo service loposcore stop
    sudo systemctl disable loposcore.service
fi

sudo cp loposcore $loposCoreBin
sudo systemctl enable loposcore.service
sudo service loposcore start


