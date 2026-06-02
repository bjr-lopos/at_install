rm motion.sql
touch motion.sql
for bl in `ls  binlog.00*`; do
	mysqlbinlog -v --base64-output=DECODE-ROWS $bl  | grep  --line-buffered '###'  -B  0 | sed -e ':a;N;$!ba;s/\n###/ /g' | grep --line-buffered motion | sed -e ':a;N;$!ba;s/\n--/;\n/g' >>motion.sql
done
