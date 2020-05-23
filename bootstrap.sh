#!/bin/bash
loposMathBin=/usr/local/bin/loposTDoA2Pos.py
LoposMathService=/etc/systemd/system/loposmath.service
loposCoreBin=/usr/local/bin/loposcore
LoposCoreService=/etc/systemd/system/loposcore.service
LocalData=/tmp/loposdb_data.sql

source ./local_cfg

buildDB() {
createUserTemp=/tmp/loposdb_cu.sql
delUserTemp=/tmp/loposdb_du.sql
delDBTemp=/tmp/loposdb_dd.sql
filteredSchema=/tmp/loposdb_schema.sql

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
    grep -v -E 'DEFINER=' lopos_schema.sql > $filteredSchema
    sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB < $filteredSchema
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



createMathService() {
LoposMathServiceTmp=/tmp/`basename $LoposMathService`
cat << EOT > $LoposMathServiceTmp
[Unit]
Description=loposmath service
#Requires=mysql.service
#After=mysql.service

[Service]
User=lopos
Group=lopos
ExecStart=/usr/bin/python3 $loposMathBin
Restart=always
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=lcs

[Install]
#WantedBy=multi-user.target mysql.service
WantedBy=multi-user.target
EOT

sudo cp $LoposMathServiceTmp $LoposMathService

}


createCoreService() {
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

if [ "$1" = "fixuser" ]; then
    PARAM="DU"
    buildDB

    PARAM="AU"
    buildDB
    exit
fi

if [ "$1" = "fixdb" ]; then
    PARAM="DU"
    buildDB
    PARAM="AU IS FD"
    buildDB
    mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e 'insert into sys values (FROM_UNIXTIME(1585692000), 165, 60, 4915);'    
    exit
fi


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
    pip3 install --user numpy

    PARAM="AU IS FD"
    buildDB
    mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e 'insert into sys values (FROM_UNIXTIME(1585692000), 165, 60, 4915);'    
    ldconfig /usr/local/lib
else 
    echo "Will run: sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB -e 'DROP VIEW IF EXISTS timeInfo' "
    sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB -e 'DROP VIEW IF EXISTS timeInfo'
    echo "will run: sudo mysqldump -u$USERLOGIN -p$USERPASS --skip-triggers --compact --no-create-info --hex-blob $TARGET_DB >> $LocalData"
    sudo mysqldump -u$USERLOGIN -p$USERPASS --skip-triggers --compact --no-create-info --hex-blob $TARGET_DB > $LocalData
    if [ -z "`cat $LocalData`" ]; then
        echo failed to store DATA with Locks.
            sudo mysqldump -u$USERLOGIN -p$USERPASS --skip-triggers --compact --no-create-info --hex-blob --single-transaction $TARGET_DB > $LocalData
            if [ -z "`cat $LocalData`" ]; then
            echo failed to store DATA. Please check!!!!!
            exit
        fi
    fi

    PARAM="DD"
    buildDB

    PARAM="IS"
    buildDB
    echo
    echo "Will run: sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData"

    #sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB -e 'SET FOREIGN_KEY_CHECKS=0'
    echo "SET SESSION sql_mode='NO_AUTO_VALUE_ON_ZERO'" > $LocalData"_n_DevSys.sql"
    strings $LocalData | grep -E ' [`]device[`] V' > $LocalData"_Dev.sql"
    strings $LocalData | grep -v -E ' [`]device[`] V| [`]sys[`] V' >> $LocalData"_n_DevSys.sql"
    strings $LocalData | grep -E ' [`]sys[`] V' > $LocalData"_Sys.sql" 

    sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData"_Dev.sql"
    sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData"_n_DevSys.sql"
    sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData"_Sys.sql"
    #sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB -e 'SET FOREIGN_KEY_CHECKS=1'

    echo "please check for errors above! If schema is not compatible. Data may be lost! Please run manualy!"
    echo
    echo "Will run: mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e 'insert into sys values (FROM_UNIXTIME(1585692000), 165, 60, 4915);'"
    mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e 'insert into sys values (FROM_UNIXTIME(1585692000), 165, 60, 4915);'    

    sudo service loposmath stop
    sudo systemctl disable loposmath.service

    sudo service loposcore stop
    sudo systemctl disable loposcore.service

fi


sudo cp `basename $loposMathBin` $loposMathBin
createMathService
sudo systemctl enable loposmath.service
sudo systemctl start loposmath.service

sudo cp `basename $loposCoreBin` $loposCoreBin
sudo cp libpaho-mqtt3c.so.1 /usr/local/lib/
createCoreService
sudo systemctl enable loposcore.service
sudo systemctl start loposcore.service


