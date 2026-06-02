lclDir=`dirname $0`
source $lclDir/local_cfg
sudo mysql $ROOTUSER $ROOTPASS $TARGET_DB 
