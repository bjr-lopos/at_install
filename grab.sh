#!/bin/bash
#GRANT FILE ON *.* TO 'lopos'@'localhost';
mysql -uilvo -pilv0 ilvo -e "select * from position where addr=0x1003 and UNIX_TIMESTAMP(updated) >= UNIX_TIMESTAMP(\"2020-05-15 15:02:19.448\");"
mysql -uilvo -pilv0 ilvo -e "select * from position where addr=0x1003 and UNIX_TIMESTAMP(updated) >= UNIX_TIMESTAMP(\"2020-05-15 15:02:19.448\") INTO OUTFILE '/tmp/exp_15_05_2020.csv' FIELDS ENCLOSED BY '\"'  TERMINATED BY ';'  ESCAPED BY '\"'  LINES TERMINATED BY '\r\n';"

