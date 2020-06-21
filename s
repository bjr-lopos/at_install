lclDir=`dirname $0`
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
    min(beaconRSSI)-100 as rrsi, 
    max(version)
from 
    stat 
group by 
    addr, mac 
order by 
    1;
EndOfMessage`
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$sql"
