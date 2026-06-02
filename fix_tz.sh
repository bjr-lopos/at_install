
lclDir=`dirname $0`
. $lclDir/local_cfg
sql=`cat << EndOfMessage
SET GLOBAL time_zone = 'Europe/Brussels';
EndOfMessage`
sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB -e "$sql"
