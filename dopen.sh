#!/bin/bash
for I in  `cat $1`;  do
 echo $I
 ./add.sh tag $I 
done
