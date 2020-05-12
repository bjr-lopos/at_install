#!/bin/bash
file="coords.csv"
while IFS= read -r tupple
do
	echo $tupple
	#addr=`echo $tupple | awk '{ print( $1)} '`
	addr=`echo $tupple | cut -c1-6`
	id=`echo $tupple | cut -c6`
	echo $addr $id
	#continue
	echo mysql -uilvo -pilv0 ilvo -e "insert into anchor (id, addr) values ($id,$addr)"
	echo mysql -uilvo -pilv0 ilvo -e "insert into position values ($tupple)"
	mysql -uilvo -pilv0 ilvo -e "insert into device (addr, mac) values ($addr, \"test_$id\")"
	mysql -uilvo -pilv0 ilvo -e "insert into anchor (id, addr) values ($id,$addr)"
	mysql -uilvo -pilv0 ilvo -e "insert into position values ($tupple)"
done <"$file"

