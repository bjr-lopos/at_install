USERLOGIN=ilvo
USERPASS=ilv0
TARGET_DB=ilvo

LocalData=/tmp/loposdb_data.sql
strings $LocalData | grep -E ' [`]device[`] V' > $LocalData"_Dev.sql"
strings $LocalData | grep -v -E ' [`]device[`] V| [`]sys[`] V' > $LocalData"_n_DevSys.sql"
strings $LocalData | grep -E ' [`]sys[`] V' > $LocalData"_Sys.sql"
sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData"_Dev.sql"
sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData"_n_DevSys.sql"
sudo mysql -u$USERLOGIN -p$USERPASS $TARGET_DB < $LocalData"_Sys.sql"
 
