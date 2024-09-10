lclDir=`dirname $0`
source $lclDir/local_cfg
sudo mysql -A $ROOTUSER $ROOTPASS $TARGET_DB 
