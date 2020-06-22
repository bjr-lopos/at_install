#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector

import time
import mysql.connector
import functools
print = functools.partial(print, flush=True)
import localConfig as cfg

#-----------------------------------------------------------
#Database
#-----------------------------------------------------------

LOPOS_SF_BLOCK_SIZE=8
mydb = None
mycursor = None

def initDB():
    global mydb
    global mycursor
    mydb = mysql.connector.connect(
        host=cfg.mysql["host"], 
        user=cfg.mysql["user"], 
        passwd=cfg.mysql["passwd"], 
        database=cfg.mysql["db"]
    )
    #print(mydb)
    mycursor = mydb.cursor()

def cleanupSFid(scheduleAT):
    dSql="delete from todo where scheduleAT=%(scheduleAT)s"
    mycursor.execute(dSql, {'scheduleAT':scheduleAT} )
    mydb.commit()

def cleanupScenario(scenario):
    dSql="delete from todo where scenario=%(scenario)s"
    mycursor.execute(dSql, {'scenario':scenario} )
    mydb.commit()

def cleanupScenarioActor4dev(scenario, actor, addr):
    dSql="delete from todo where addr=%(addr)s and scenario=%(scenario)s and actor=%(actor)s"
    mycursor.execute(dSql, {'addr':addr, 'scenario':scenario, 'actor':actor} )
    mydb.commit()

def keepOutRepeatingAndfixedSF(SFid):
    global LOPOS_SF_BLOCK_SIZE
    if SFid < 85:
        SFid = 85
    if SFid >250:
        SFid = 85
    if SFid % LOPOS_SF_BLOCK_SIZE >= 2:
        SFid += LOPOS_SF_BLOCK_SIZE - (SFid % LOPOS_SF_BLOCK_SIZE)
    return SFid        

def claimRepeatingAndfixedSF(SFid):
    global LOPOS_SF_BLOCK_SIZE
    if SFid < 85:
        SFid = 85
    if SFid >250:
        SFid = 85
    if SFid % LOPOS_SF_BLOCK_SIZE <= 2:
        SFid += 2 - (SFid % LOPOS_SF_BLOCK_SIZE)
    if SFid % LOPOS_SF_BLOCK_SIZE == LOPOS_SF_BLOCK_SIZE -1:
        SFid += 3
    return SFid        

def insertTodo(addr, SFcnt, scenario, actor, repeat, last):
    iSql="""
        insert into todo 
            (addr, scheduleAT, scenario, actor, rescheduleSF)
        values (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE 
            updated=now(),
            scenario=%s,
            actor=%s,
            rescheduleSF=%s
    """
    try:
        print("S @:", SFcnt, "s:", scenario, "a:", actor, "d:", hex(addr), "last @", last)
        mycursor.execute(iSql, (addr, SFcnt, scenario, actor, repeat, scenario, actor, repeat))
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

def updateSysBeaconId(beaconID):
    uSql="update sys set beaconID=%(beaconID)s"
    try:
        print("Will update beaconID", hex(beaconID))
        mycursor.execute(uSql, {'beaconID':beaconID} )
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


def deleteOldSchedules(numSF):
    dSql="delete from todo using todo,sys where TIMESTAMPDIFF(SECOND,todo.updated,now()) > %(numSF)s*((sys.SFticks * sys.SFmax)/32768) "
    mycursor.execute(dSql, {'numSF':numSF})
    mydb.commit()

def checkForSchedules(table, scenario, maxActors, _reqScheduleCB = None):
    ssSql = """
        SELECT p.addr, CASE WHEN s.last_update IS NULL THEN 0 else DATE_ADD(s.last_update, INTERVAL p.interval SECOND) end as schedule
        FROM 
            plan as p
        LEFT JOIN 
            (select addr, max(updated) as last_update from """ + table + """ group by addr) as s
        ON    
            p.addr = s.addr	
        where 
            scenario = %(scenario)s and ((s.last_update IS NULL) or (TIMESTAMPDIFF(SECOND,s.last_update,now()) > ( p.interval -10) ) )
        order by 2;        
    """
    try:
        mycursor.execute(ssSql, {'table':table, 'scenario':scenario} )
        records = mycursor.fetchall()
        actorCnt = 0
        SFcnt = geNextSFidxRef()
        for needSchedule in records:
            addr = needSchedule[0]
            last = needSchedule[1]
            if actorCnt == 0:
                insertTodo(0xFFF0, SFcnt,  cfg.LOPOS_SCENARIO_Stat, actorCnt, 0, last)
                actorCnt +=1
            insertTodo(addr, SFcnt, cfg.LOPOS_SCENARIO_Stat, actorCnt, 0, last)
            if _reqScheduleCB:
                print ("will call cb")
                _reqScheduleCB(addr, last)
            actorCnt +=1
            if actorCnt > maxActors:
                actorCnt = 0
                SFcnt = geNextSFidxRef()

    except Exception as ex:
        print(ex)        
    except mysql.connector.Error as err:
        s = str(e)
        print ("Error code:", e.errno)        # error number
        print ("SQLSTATE value:", e.sqlstate) # SQLSTATE value
        print ("Error message:", e.msg)       # error message
        print ("Error:", e)                   # errno, sqlstate, msg values
        print ("Error:", s)                   # errno, sqlstate, msg values

#-----------------------------------------------------------
#SFidxRef and SFrepIdxRef
#-----------------------------------------------------------

SFidxRef=0
SFrepIdxRef=0

def initSFidxRef():
    global SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(0)
    return SFidxRef

def geNextSFidxRef():
    global SFidxRef
    SFidxCurr = SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(SFidxCurr+1)
    return SFidxCurr


def initSFrepIdxRef():
    global SFrepIdxRef
    SFrepIdxRef = claimRepeatingAndfixedSF(0)
    return SFrepIdxRef

def geNextSFrepIdxRef():
    global SFrepIdxRef 
    SFrepIdxCurr = SFrepIdxRef
    SFrepIdxRef = claimRepeatingAndfixedSF(SFrepIdxCurr+1)
    return SFrepIdxCurr

