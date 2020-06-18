#!/usr/bin/env python
#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector

import json
import time
import paho.mqtt.client as mqtt
import mysql.connector
import functools
from datetime import datetime
import localConfig as cfg



print = functools.partial(print, flush=True)
LOPOS_SF_BLOCK_SIZE=8
SFidxRef=0
SFrepIdxRef=0
#-----------------------------------------------------------
#Database
#-----------------------------------------------------------
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

def initSFidxRef():
    global SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(0)
    return SFidxRef

def geNextSFidxRef():
    global SFidxRef
    SFidxCurr = SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(SFidxRef+1)
    return SFidxCurr


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

def testFwd(dev,anchor): 
    print("Schedule testFwd: ")
    SF2fwd = geNextSFidxRef()
    SF2sink = geNextSFidxRef()
    cleanupSFid(SF2fwd)
    cleanupSFid(SF2sink)
    insertTodo(anchor, SF2fwd, cfg.LOPOS_SCENARIO_Stat, 11, 0, 0)
    insertTodo(dev, SF2fwd, cfg.LOPOS_SCENARIO_Stat, 1, 0, 0)
    insertTodo(0xFFF0, SF2sink, cfg.LOPOS_SCENARIO_Fwd, 0, 0, 0)
    insertTodo(anchor, SF2sink, cfg.LOPOS_SCENARIO_Fwd, 1, 0, 0)
    #geNextSFidxRef()

def testTDoA(): 
    print("Schedule testTDoA: ")
    SFidx = geNextSFidxRef()
    cleanupSFid(SFidx)
    insertTodo(0xFFF0, SFidx, cfg.LOPOS_SCENARIO_TDoA, 0, 0, 0)
    insertTodo(0xA000, SFidx, cfg.LOPOS_SCENARIO_TDoA, 1, 0, 0)
    insertTodo(0xA01E, SFidx, cfg.LOPOS_SCENARIO_TDoA, 2, 0, 0)
    insertTodo(0xA009, SFidx, cfg.LOPOS_SCENARIO_TDoA, 3, 0, 0)
    insertTodo(0x1001, SFidx, cfg.LOPOS_SCENARIO_TDoA, 10, 0, 0)
    insertTodo(0x1002, SFidx, cfg.LOPOS_SCENARIO_TDoA, 11, 0, 0)
    insertTodo(0x1004, SFidx, cfg.LOPOS_SCENARIO_TDoA, 12, 0, 0)
    insertTodo(0x1064, SFidx, cfg.LOPOS_SCENARIO_TDoA, 13, 0, 0)

def testAccel(dev): 
    print("Schedule testAccel: ")
    global SFrepIdxRef
    SFrepIdxRef=claimRepeatingAndfixedSF(SFrepIdxRef+1)
    cleanupScenario(cfg.LOPOS_SCENARIO_Accel)    
    insertTodo(0xFFF0, SFrepIdxRef, cfg.LOPOS_SCENARIO_Accel, 0, 1, 0)
    insertTodo(dev, SFrepIdxRef, cfg.LOPOS_SCENARIO_Accel, 1, 1, 0)

def testAnchor(addr): 
    print("Schedule testAnchor: ")
    cleanupScenarioActor4dev(cfg.LOPOS_SCENARIO_System, 1, addr)
    for i in range(10):    
        SFcnt = geNextSFidxRef()
        insertTodo(addr, SFcnt, cfg.LOPOS_SCENARIO_System, 1, 0, 0)

def testDiscover(anchor, dev): 
    print("Schedule discover: ")
    SFcnt = geNextSFidxRef()
    cleanupScenario(cfg.LOPOS_SCENARIO_Discover)
    insertTodo(0xFFF0, SFcnt, cfg.LOPOS_SCENARIO_Discover, 0, 0, 0)
    insertTodo(anchor, SFcnt, cfg.LOPOS_SCENARIO_Discover, 1, 0, 0)
    insertTodo(dev, SFcnt, cfg.LOPOS_SCENARIO_Discover, 16, 0, 0)

def testUWB(anchor, dev): 
    print("Schedule UWB: ")
    SFcnt = geNextSFidxRef()
    cleanupScenario(cfg.LOPOS_SCENARIO_Uwb)
    insertTodo(0xFFF0, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 0, 0, 0)
    insertTodo(anchor, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 1, 0, 0)
    insertTodo(dev, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 9, 0, 0)

def scheduleStats():
    print("Schedule dev reports: ")
    cleanupScenario(cfg.LOPOS_SCENARIO_Stat)
    actorCnt = 0
    SFcnt = geNextSFidxRef()
    try:
        mycursor.execute("""
            SELECT p.addr, CASE WHEN s.last_update IS NULL THEN 0 else DATE_ADD(s.last_update, INTERVAL p.interval SECOND) end as schedule
            FROM 
                plan as p
            LEFT JOIN 
                (select addr, max(updated) as last_update from stat group by addr) as s
            ON    
                p.addr = s.addr	
            where 
                scenario = %(scenario)s and ((s.last_update IS NULL) or (TIMESTAMPDIFF(SECOND,s.last_update,now()) > ( p.interval -10) ) )
            order by 2;        
        """,  {'scenario':cfg.LOPOS_SCENARIO_Stat} )
        records = mycursor.fetchall()
        for needStatSchedule in records:
            #print(locals())
            if actorCnt == 0:
                insertTodo(0xFFF0, SFcnt,  cfg.LOPOS_SCENARIO_Stat, actorCnt, 0, needStatSchedule[1])
                actorCnt +=1
            insertTodo(needStatSchedule[0], SFcnt, cfg.LOPOS_SCENARIO_Stat, actorCnt, 0, needStatSchedule[1])
            actorCnt +=1
            if actorCnt > 10:
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
#Actions
#-----------------------------------------------------------



def planActions():
    global SFrepIdxRef
    SFrepIdxRef=0
    initSFidxRef()
    now = datetime.now()
    t1=int(round(time.time() * 1000000))
    current_time = now.strftime("%H:%M:%S %B %d %Y")
    print("Schedule iteration (will clean up old todo): @", current_time)
    dSql="delete from todo using todo,sys where TIMESTAMPDIFF(SECOND,todo.updated,now()) > 2*((sys.SFticks * sys.SFmax)/32768) "
    mycursor.execute(dSql)
    mydb.commit()
    scheduleStats()

    if hasattr(cfg, 'testAnchor'):
        if cfg.testAnchor == 1:
            testAnchor(0xA01E)

    if hasattr(cfg, 'testFwd'):
        if cfg.testFwd == 1:
            testFwd(0x1004, 0xA01E)

    if hasattr(cfg, 'testTDoA'):
        if cfg.testTDoA == 1:
            testTDoA()

    if hasattr(cfg, 'testAccel'):
        if cfg.testAccel == 1:
            testAccel(0x1004)

    if hasattr(cfg, 'testDiscover'):
        if cfg.testDiscover == 1:
            testDiscover(0xA01E, 0x1004)

    if hasattr(cfg, 'testUWB'):
        if cfg.testUWB == 1:
            testUWB(0xA000, 0x1004)


    t2=int(round(time.time() * 1000000))
    print("Scheduler finished in ", t2-t1, "us")

#-----------------------------------------------------------
#Mqtt interface
#-----------------------------------------------------------
def on_connect(client, userdata, message,rc):
    print("Connected to mqtt broker")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("loposcore/plan")
    print("subscribed to loposcore/plan")

def on_message(client, userdata, message):
    payload=str(message.payload.decode("utf-8"))
    print(message.topic)
    if(message.topic == "loposcore/plan"): 
        payloadJson = json.loads(payload)    
        print(payloadJson)
        planActions()

mqtt_broker = '127.0.0.1'
client = mqtt.Client() #create new instance
client.username_pw_set("lopos", "LoPoS")
client.on_connect=on_connect
client.on_message=on_message
print("Connecting to mqtt broker...")
#print(mpl.get_backend())
client.connect(mqtt_broker, 1883, 60)
client.loop_forever()

#-----------------------------------------------------------
#main loop
#-----------------------------------------------------------
while True:
    #delete from stat where TIMESTAMPDIFF(MINUTE,updated, now()) > 60;
    planActions()
    time.sleep(5)
