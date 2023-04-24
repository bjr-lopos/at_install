while read -r line; do 
	echo $line | sed "s/@7=/@7=from_unixtime(/g" | sed "s/([^()]*)//g" | sed "s/@.=/,/g" | sed "s/SET[^,]*,/values \(/g" | sed "s/;/));/" | sed 's/`wish`.`motion`/motion/g' >> motion_fix.sql
done < motion.sql
