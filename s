lclDir=`dirname $0`
header="SELECT '0xaddr', 'type', 'id', 'mac', 'secSinceLastUpdate', 'vbat', 'rssiAvg', 'rssiMin', 'rssiMax', 'version', 'minDrift', 'avgDrift', 'maxDrift', 'minBR', 'avgBR', 'maxBR', 'minUP', 'maxUP'  UNION ALL"

dumpfile=/tmp/s_`date +%y_%m_%d__%H_%M_%S`.csv
delay=$((15*60))
if [ ! -z "$1" ]; then
	delay="$1"
        delay="$1"
fi
echo will use delay $delay
#sleep 1
source $lclDir/local_cfg
export_sql="INTO OUTFILE \"$dumpfile\" FIELDS ENCLOSED BY '\"'  TERMINATED BY ';'  ESCAPED BY '\"'  LINES TERMINATED BY '\r\n';"
sql=`cat << EndOfMessage
select
    hex(addr) as 0xaddr,
    case
        when addr&0xF000 = 0xA000 then "anchor"
        when addr&0xFFF0 = 0xFFF0 then "sink"
    else
        "tag"
    end
    as type,
    case
        when addr&0xFFF0 = 0xFFF0 then addr&0x000F
    else
        addr&0x0FFF
    end
    as id, 
    mac, 
    TIMESTAMPDIFF(SECOND,max(updated),now()) as secSinceLastUpdate, 
    min(vbattRatio)*20+2200 as vbat, 
    round(avg(beaconRSSI)) as rrsiAvg, 
    min(beaconRSSI) as rrsiMin, 
    max(beaconRSSI) as rrsiMax, 
    max(version),
    min(drift) as minDrift,
    round(avg(drift)) as avgDrift,
    max(drift) as maxDrift,
    min(beaconRatio) as minBR,
    round(avg(beaconRatio)) as avgBR,
    max(beaconRatio) as maxBR,
    ((7 - (min(uwbTxPwr) div 32)) * 3) + round((min(uwbTxPwr) & 0x01F)/2) as UP1,
    ((7 - (max(uwbTxPwr) div 32)) * 3) + round((max(uwbTxPwr) & 0x01F)/2) as UP2
from 
    stat 
where
    TIMESTAMPDIFF(SECOND,updated,now()) < $delay
group by 
    addr, mac 
order by 
    1
EndOfMessage`
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$sql ;"
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$header $sql $export_sql ;" 
