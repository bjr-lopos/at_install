#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector-python

import sys
import time
import numpy as np
import mysql.connector
import functools
print = functools.partial(print, flush=True)
import localConfig as cfg

#-----------------------------------------------------------
#Database
#-----------------------------------------------------------

mydb = None
mycursor = None
positionAnchor = {}
positionCoreAnchor = {}
positionTag = {}
discoveredTag = {} 
sqlInstantCommit = 1

def initDB():
    global mydb
    global mycursor
    mydb = mysql.connector.connect(
        host=cfg.mysql["host"], 
        user=cfg.mysql["user"], 
        passwd=cfg.mysql["passwd"], 
        database=cfg.mysql["db"],
        auth_plugin='mysql_native_password'        
    )
    #print(mydb)
    mycursor = mydb.cursor()


def _wrappedSql(sql, param, expectResults):
    global sqlInstantCommit
    try:
        mycursor.execute(sql, param)
        if expectResults:
            records = mycursor.fetchall()
            return records
        else:
            if sqlInstantCommit == 1:
                mydb.commit()
    except Exception as ex:
        print(ex)        
    except mysql.connector.Error as err:
        s = str(e)
        print ("Error code:", e.errno)        # error number
        print ("SQLSTATE value:", e.sqlstate) # SQLSTATE value
        print ("Error message:", e.msg)       # error message
        print ("Error:", e)                   # errno, sqlstate, msg values
        print ("Error:", s)                   # errno, sqlstate, msg values

def wrappedSql(sql, param):
    return _wrappedSql(sql, param, 1)

def wrappedESql(sql, param):
    _wrappedSql(sql, param, 0)

def wrappedESqlDoCommitAndSetInstant(instantCommit):
    global sqlInstantCommit
    #if sqlInstantCommit == 0:
    mydb.commit()
    sqlInstantCommit = instantCommit


def cleanupSFid(scheduleAT):
    sql="delete from todo where scheduleAT=%(scheduleAT)s"
    wrappedESql(sql, {'scheduleAT':scheduleAT} )

def cleanupScenario(scenario):
    sql="delete from todo where scenario=%(scenario)s"
    wrappedESql(sql, {'scenario':scenario} )


def cleanupScenarioActor(scenario, actor):
    sql="delete from todo where scenario=%(scenario)s and actor=%(actor)s"
    wrappedESql(sql, {'scenario':scenario, 'actor':actor} )

def cleanupScenarioActor4dev(scenario, actor, addr):
    sql="delete from todo where addr=%(addr)s and scenario=%(scenario)s and actor=%(actor)s"
    wrappedESql(sql, {'addr':addr, 'scenario':scenario, 'actor':actor} )


def getNumAnchors():
    sql="""
        SELECT max(id)+%(overdimension)s as maxAnchor
        FROM anchor as a
    """
    records = wrappedSql(sql, {'overdimension':1} )
    for row in records:
        numAnchors = row[0]
        print("Overdimensioned number of anchors is: ", numAnchors)
        return numAnchors

def getPositionAnchors():
    global positionAnchor
    #positionAnchor.clear()
    if len(positionAnchor) > 0:
        return
    sql="""
        SELECT a.id as id, a.addr as addr, hex(a.addr) as addrX, p.x as x, p.y as y, p.z as z
        FROM position as p, anchor as a, (select addr, max(updated) as updated from position group by addr) as recent 
        where p.addr=recent.addr and recent.updated=p.updated and p.addr=a.addr 
        order by 1 
    """
    records = wrappedSql(sql, {})
    for anchor in records:
        id=anchor[0]
        x=anchor[3]
        y=anchor[4]
        z=anchor[5]
        positionAnchor[id] = [x, y, z]

def getPositionCoreAnchors():
    global positionCoreAnchor
    if len(positionCoreAnchor) > 0:
        return
    sql="""
        select anchor.id, x, y, z, anchor.addr from
            position,
            (SELECT core FROM cell group by core having count(*) <= 8) as coreA,
            anchor
        where 
            anchor.id=coreA.core 
            and 
            position.addr=anchor.addr
            and
            numHyperbola = 0;
    """
    records = wrappedSql(sql, {})
    for core in records:
        id=core[0]
        x=core[1]
        y=core[2]
        z=core[3]
        addr=core[4]
        positionCoreAnchor[id]=[x, y, z,addr]

def getNumCoreAnchors():
    return len(positionCoreAnchor)

def getCoreAnchors():
    return positionCoreAnchor.keys()

def localizeDiscoverTags(age, minRxPow):
    global discoveredTag
    discoveredTag.clear()
    #create index uwbstat_devRx on uwbstat (devRx); 
    #create index uwbstat_devTx on uwbstat (devTx); 
    #create index pos_addr on position (addr);
    #create index uwbstat_upd_desc on uwbstat (updated desc);
    sql="""
        select 
            devTx, 
            sum(rxPow * weight) /sum(weight) as rxPow, 
            sum(x * weight) /sum(weight) as x, 
            sum(y * weight) /sum(weight) as y, 
            sum(z * weight) /sum(weight) as z,
            count(*),
            min(devRx),
            max(devRx),
            min(rxPow)
        from 
            (SELECT 
                u.devTx as devTx, u.rxPow as rxPow, x, y, z, u.devRx as devRx, 
                case 
                    when u.rxPow > -70 then 10
                    when u.rxPow > -78 then 7
                    when u.rxPow > -85 then 1
                    else 0
                end as weight
            FROM 
                uwbstat as u left join position as p on u.devRx = p.addr
            where 
                TIMESTAMPDIFF(SECOND,u.updated,now()) < %(age)s
            )
            as wu
        group by devTx
        having sum(rxPow * weight) /sum(weight)  > %(minRxPow)s
    """
    records = wrappedSql(sql, {'age':age, 'minRxPow':minRxPow})
    if records is None:
        return
    for disc in records:
        addr=disc[0]
        x=disc[2]
        y=disc[3]
        z=disc[4]
        discoveredTag[addr] = [x,y,z]
    #print("Discovered:", discoveredTag)

def getPositionTags():
    global positionTag
    positionTag.clear()
    sql="""
        select 
            p.addr, x, y, z, TIMESTAMPDIFF(SECOND,lu.updated,now())
        from
            (   select 
                    addr, max(updated) as updated
                from position
                where addr & 0xF000 = 0x1000
                group by addr
            ) as lu,
            position as p
        where 
            lu.updated = p.updated
    """
    records = wrappedSql(sql, {})
    if records is None:
        return
    for pos in records:
        addr=pos[0]
        x=pos[1]
        y=pos[2]
        z=pos[3]
        age=pos[4]
        positionTag[addr] = [x,y,z,age]

def findCloseCore(dev, maxage):
    global positionCoreAnchor
    global positionTag
    global discoveredTag
    lDist = 10000
    coreIdx = None
    pos =  positionTag.get(dev)
    if (pos is None) or (pos[3]>=maxage):
        pos =  discoveredTag.get(dev)
        if (pos is None):
            return None
    #print("pos is: ", pos)
    dx=float(pos[0])
    dy=float(pos[1])
    dz=float(pos[2])
    for core in positionCoreAnchor.keys():
        cx=float(positionCoreAnchor[core][0])
        cy=float(positionCoreAnchor[core][1])
        cz=float(positionCoreAnchor[core][2])
        cDist = ((dx-cx)**2+(dy-cy)**2+(dz-cy)**2)**(.5)
        if cDist < lDist: 
            coreIdx = core
            lDist = cDist
    #print("Dist is: ", str(lDist))
    return coreIdx


def insertTodo(addr, SFcnt, scenario, actor, repeat, last):
    sql="""
        insert into todo 
            (addr, scheduleAT, scenario, actor, rescheduleSF)
        values (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE 
            updated=now(),
            scenario=%s,
            actor=%s,
            rescheduleSF=%s
    """
    print("S @:", SFcnt, "s:", '{:>2}'.format(scenario), "a:", '{:>2}'.format(actor), "d:", hex(addr), "last @", last)
    wrappedESql(sql, (addr, SFcnt, scenario, actor, repeat, scenario, actor, repeat))

def updateSysBeaconId(beaconID):
    sql="update sys set beaconID=%(beaconID)s"
    print("Will update beaconID", hex(beaconID))
    wrappedESql(sql, {'beaconID':beaconID} )

def deleteOldSchedules(numSF):
    sql="delete from todo using todo,sys where TIMESTAMPDIFF(SECOND,todo.updated,now()) > %(numSF)s*((sys.SFticks * sys.SFmax)/32768) "
    wrappedESql(sql, {'numSF':numSF})

def requestAnchorPerCell(core, max, _reqAnchorCellCB = None):
    sql = """
        SELECT 
            anchor.addr
        FROM 
            cell,
            anchor
        where 
            cell.core = %(core)s 
            and
            anchor.id = cell.edge
        order by 1
        limit %(max)s         
    """
    records = wrappedSql(sql, {'core':core, 'max':max} )
    if (records is None) :
        print("No edges configured for core:", str(core))
        return
    for edge in records:
        if _reqAnchorCellCB:
            #print ("will call cb")
            _reqAnchorCellCB(core, edge[0])


#every planned scenario has a result table, we will search for devices which have an overdue scenario
def checkForSchedules(table, scenario, _reqScheduleCB = None):
    sql = """
        SELECT 
            p.addr, 
            CASE 
                WHEN ref.last_update IS NULL THEN 0 
                else DATE_ADD(ref.last_update, INTERVAL p.interval SECOND) 
            end as schedule,
            CASE 
                WHEN ref.last_update IS NULL THEN p.interval/2
                else TIMESTAMPDIFF(SECOND,ref.last_update,now()) - p.interval
            end as diff
        FROM 
            sys,
            plan as p
        LEFT JOIN 
            (select addr, max(updated) as last_update from """ + table + """ group by addr) as ref
        ON    
            p.addr = ref.addr	
        where 
            scenario = %(scenario)s 
            and (
                    (ref.last_update IS NULL) 
                    or 
                    (TIMESTAMPDIFF(SECOND,ref.last_update,now()) > ( p.interval - (sys.SFmax*sys.SFticks/32768)) ) 
            )
        order by 3 desc;        
    """
    records = wrappedSql(sql, {'scenario':scenario} )
    for needSchedule in records:
        addr = needSchedule[0]
        last = needSchedule[1]
        overdue = needSchedule[2]
        if _reqScheduleCB:
            #print ("will call cb")
            _reqScheduleCB(addr, last, overdue)

#-----------------------------------------------------------
#SFidxRef and SFrepIdxRef
#-----------------------------------------------------------

SFidxRef=0
SFrepIdxRef=0

def keepOutRepeatingAndfixedSF(SFid):
    adjust2allowedOffsets = {0:0, 1:0, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1}  
    if SFid <= cfg.LOPOS_LAST_FIXED_SF:
        SFid = cfg.LOPOS_LAST_FIXED_SF + 1
    if SFid >cfg.LOPOS_LAST_USABLE_SF:
        loposPy.deleteOldSchedules(0)
        print("ERROR: Hyperframe !")
        sys.exit()
    blockOfs = SFid % cfg.LOPOS_SF_BLOCK_SIZE
    SFid += adjust2allowedOffsets[blockOfs]
    return SFid        

def claimRepeatingAndfixedSF(SFid):
    adjust2allowedOffsets = {0:2, 1:1, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}  
    if SFid <= cfg.LOPOS_LAST_FIXED_SF:
        SFid = cfg.LOPOS_LAST_FIXED_SF + 1
    if SFid >cfg.LOPOS_LAST_USABLE_SF:
        loposPy.deleteOldSchedules(0)
        print("ERROR: Hyperframe overstressed!")
        sys.exit()
    blockOfs = SFid % cfg.LOPOS_SF_BLOCK_SIZE
    SFid += adjust2allowedOffsets[blockOfs]
    return SFid        

def initSFidxRef():
    global SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(0)
    return SFidxRef

def getNextSFidxRef():
    global SFidxRef
    SFidxCurr = SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(SFidxCurr+1)
    return SFidxCurr


def initSFrepIdxRef():
    global SFrepIdxRef
    SFrepIdxRef = claimRepeatingAndfixedSF(0)
    return SFrepIdxRef

def getNextSFrepIdxRef():
    global SFrepIdxRef 
    SFrepIdxCurr = SFrepIdxRef
    SFrepIdxRef = claimRepeatingAndfixedSF(SFrepIdxCurr+1)
    return SFrepIdxCurr

