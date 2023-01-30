#!/bin/bash
for I in  `cat $1`;  do
 if [ -z "$1" ]; then
  continue
 fi
 echo "$I"
 echo ./add.sh tag "$I" 
 ./add.sh tag "$I" 
done
