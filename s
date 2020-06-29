lclDir=`dirname $0`
delay=$((15*60))
if [ ! -z "$1" ]; then
	delay="$1"
        delay="$1"
fi
echo will use delay $delay
sleep 1
source $lclDir/local_cfg
sql=`cat << EndOfMessage
select
    hex(addr),
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
    max(beaconRatio) as maxBR
from 
    stat 
where
    TIMESTAMPDIFF(SECOND,updated,now()) < $delay
group by 
    addr, mac 
order by 
    1;
EndOfMessage`
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$sql"



