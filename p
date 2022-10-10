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
    scheduleAT,
    scenario,
    actor,
    rescheduleSF,
    TIMESTAMPDIFF(SECOND,updated,now()) as secSinceLastUpdate
from 
    todo
order by 
    4,6;
EndOfMessage`
mysql -u$USERLOGIN -p$USERPASS $TARGET_DB -e "$sql"
