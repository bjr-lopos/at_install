#!/usr/bin/env python
#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector

import time
from datetime import datetime
import paho.mqtt.client as mqtt
import mysql.connector
import functools
import loposPyLib as loposPy
import localConfig as cfg

print = functools.partial(print, flush=True)

stats_ActorCnt=0
stats_SFcnt=0
tdoa_ActorCnt=0
tdoa_SFcnt=0
disc_ActorCnt=0
disc_SFcnt=0


def testFwd(dev,anchor): 
    print("Schedule testFwd: ")
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Fwd)    
    SF2fwd = loposPy.geNextSFidxRef()
    SF2sink = loposPy.geNextSFidxRef()
    loposPy.insertTodo(anchor, SF2fwd, cfg.LOPOS_SCENARIO_Stat, 11, 0, 0)
    loposPy.insertTodo(dev, SF2fwd, cfg.LOPOS_SCENARIO_Stat, 1, 0, 0)
    loposPy.insertTodo(0xFFF0, SF2sink, cfg.LOPOS_SCENARIO_Fwd, 0, 0, 0)
    loposPy.insertTodo(anchor, SF2sink, cfg.LOPOS_SCENARIO_Fwd, 1, 0, 0)
    #geNextSFidxRef()

def testTDoA(): 
    print("Schedule testTDoA: ")
    SFidx = loposPy.geNextSFidxRef()
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_TDoA)    
    loposPy.insertTodo(0xFFF0, SFidx, cfg.LOPOS_SCENARIO_TDoA, 0, 0, 0)
    loposPy.insertTodo(0xA000, SFidx, cfg.LOPOS_SCENARIO_TDoA, 1, 0, 0)
    loposPy.insertTodo(0xA01E, SFidx, cfg.LOPOS_SCENARIO_TDoA, 2, 0, 0)
    loposPy.insertTodo(0xA009, SFidx, cfg.LOPOS_SCENARIO_TDoA, 3, 0, 0)
    loposPy.insertTodo(0x1001, SFidx, cfg.LOPOS_SCENARIO_TDoA, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS + 0, 0, 0)
    loposPy.insertTodo(0x1002, SFidx, cfg.LOPOS_SCENARIO_TDoA, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS + 1, 0, 0)
    loposPy.insertTodo(0x1004, SFidx, cfg.LOPOS_SCENARIO_TDoA, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS + 2, 0, 0)
    loposPy.insertTodo(0x1064, SFidx, cfg.LOPOS_SCENARIO_TDoA, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS + 2, 0, 0)

def testAccel(dev): 
    print("Schedule testAccel: ")
    SFrepIdxRef=loposPy.geNextSFrepIdxRef()
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Accel)    
    loposPy.insertTodo(0xFFF0, SFrepIdxRef, cfg.LOPOS_SCENARIO_Accel, 0, 1, 0)
    loposPy.insertTodo(dev, SFrepIdxRef, cfg.LOPOS_SCENARIO_Accel, 1, 1, 0)

def testAnchor(addr): 
    print("Schedule testAnchor: ")
    loposPy.cleanupScenarioActor4dev(cfg.LOPOS_SCENARIO_System, 2, addr)
    for i in range(10):    
        SFcnt = loposPy.geNextSFidxRef()
        loposPy.insertTodo(addr, SFcnt, cfg.LOPOS_SCENARIO_System, 2, 0, 0)

def testDiscover(anchor, dev): 
    print("Schedule discover: ")
    SFcnt = loposPy.geNextSFidxRef()
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Discover)
    loposPy.insertTodo(0xFFF0, SFcnt, cfg.LOPOS_SCENARIO_Discover, 0, 0, 0)
    loposPy.insertTodo(anchor, SFcnt, cfg.LOPOS_SCENARIO_Discover, 1, 0, 0)
    loposPy.insertTodo(dev, SFcnt, cfg.LOPOS_SCENARIO_Discover, cfg.LOPOS_SCENARIO_Discover_TAG_OFS + 0, 0, 0)

def testUWB(anchor, dev): 
    print("Schedule UWB: ")
    SFcnt = loposPy.geNextSFidxRef()
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Uwb)
    loposPy.insertTodo(0xFFF0, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 0, 0, 0)
    loposPy.insertTodo(anchor, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 1, 0, 0)
    loposPy.insertTodo(dev, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 9, 0, 0)

def scheduleStatsCB(addr, last, overdue):
    global stats_ActorCnt
    global stats_SFcnt
    #print("scheduleStatsCB: " + hex(addr) + " "+ last + " "+ str(overdue)+ "s"  )
    if stats_ActorCnt == 0:
        loposPy.insertTodo(0xFFF0, stats_SFcnt,  cfg.LOPOS_SCENARIO_Stat, stats_ActorCnt, 0, last)
        stats_ActorCnt +=1
    loposPy.insertTodo(addr, stats_SFcnt, cfg.LOPOS_SCENARIO_Stat, stats_ActorCnt, 0, last)
    stats_ActorCnt +=1
    if stats_ActorCnt > 10:
        stats_ActorCnt = 0
        stats_SFcnt = loposPy.geNextSFidxRef()

def scheduleStats():
    print("Schedule dev reports: ")
    global stats_ActorCnt
    global stats_SFcnt
    stats_ActorCnt = 0
    stats_SFcnt = loposPy.geNextSFidxRef()
    loposPy.checkForSchedules("stat", cfg.LOPOS_SCENARIO_Stat, scheduleStatsCB)


def discReqAnchorCellCB(core, edge):
    global disc_ActorCnt
    global disc_SFcnt
    loposPy.insertTodo(edge, disc_SFcnt,  cfg.LOPOS_SCENARIO_Discover, disc_ActorCnt, 0, 0)
    disc_ActorCnt +=1


def tdoaReqAnchorCellCB(core, edge):
    global tdoa_ActorCnt
    global tdoa_SFcnt
    loposPy.insertTodo(edge, tdoa_SFcnt,  cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, 0)
    tdoa_ActorCnt +=1

def scheduleTdoaCB(addr, last, overdue):
    #print("scheduleTdoaCB: " + hex(addr) + " "+ last + " "+ str(overdue) )
    if (overdue > 64) and (loposPy.findCloseCore(addr,64) is None): 
        global disc_ActorCnt
        global disc_SFcnt
        #print("discover") 
        if disc_ActorCnt == 0:
            loposPy.insertTodo(0xFFF0, disc_SFcnt,  cfg.LOPOS_SCENARIO_Discover, disc_ActorCnt, 0, last)
            disc_ActorCnt +=1
            loposPy.requestAnchorPerCell(40, cfg.LOPOS_SCENARIO_Discover_TAG_OFS - 1, discReqAnchorCellCB)
            if (disc_ActorCnt < cfg.LOPOS_SCENARIO_Discover_TAG_OFS):
                disc_ActorCnt = cfg.LOPOS_SCENARIO_Discover_TAG_OFS
        loposPy.insertTodo(addr, disc_SFcnt, cfg.LOPOS_SCENARIO_Discover, disc_ActorCnt, 0, last)
        disc_ActorCnt +=1
        if disc_ActorCnt > cfg.LOPOS_SCENARIO_Discover_TAG_MAX:
            disc_ActorCnt = 0
            disc_SFcnt = loposPy.geNextSFidxRef()
    else :
        global tdoa_ActorCnt
        global tdoa_SFcnt
        #print("tdoa") 
        if tdoa_ActorCnt == 0:
            loposPy.insertTodo(0xFFF0, tdoa_SFcnt,  cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, last)
            tdoa_ActorCnt +=1
            core = loposPy.findCloseCore(addr,1000)
            loposPy.insertTodo(0xA000+core, tdoa_SFcnt,  cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, last)
            tdoa_ActorCnt +=1
            loposPy.requestAnchorPerCell(core, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS - 2, tdoaReqAnchorCellCB)
            if (tdoa_ActorCnt < cfg.LOPOS_SCENARIO_TDoA_TAG_OFS):
                tdoa_ActorCnt = cfg.LOPOS_SCENARIO_TDoA_TAG_OFS
        loposPy.insertTodo(addr, tdoa_SFcnt, cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, last)
        tdoa_ActorCnt +=1
        if tdoa_ActorCnt > cfg.LOPOS_SCENARIO_TDoA_TAG_MAX:
            tdoa_ActorCnt = 0
            tdoa_SFcnt = loposPy.geNextSFidxRef()

def scheduleTDoA():
    print("Schedule TDoA reports: ")
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_TDoA)    
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Discover)    
    global tdoa_ActorCnt
    global tdoa_SFcnt
    global disc_ActorCnt
    global disc_SFcnt
    tdoa_ActorCnt = 0
    tdoa_SFcnt = loposPy.geNextSFidxRef() #maybe not used?
    disc_ActorCnt = 0
    disc_SFcnt = loposPy.geNextSFidxRef() #maybe not used?
    loposPy.getPositionTags()
    loposPy.localizeDiscoverTags(50)
    loposPy.checkForSchedules("position", cfg.LOPOS_SCENARIO_TDoA, scheduleTdoaCB)

#-----------------------------------------------------------
#Actions
#-----------------------------------------------------------

def planActions():
    loposPy.initSFidxRef()
    loposPy.initSFrepIdxRef()
    now = datetime.now()
    t1=int(round(time.time() * 1000000))
    current_time = now.strftime("%H:%M:%S %B %d %Y")
    print("Schedule iteration (will clean up old todo): @", current_time)
    loposPy.deleteOldSchedules(2)
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Stat)
    scheduleStats()
    scheduleTDoA()

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
    #print(message.topic)
    if(message.topic == "loposcore/plan"): 
        #payloadJson = json.loads(payload)    
        #print(payloadJson)
        planActions()

loposPy.initDB()
loposPy.getPositionCoreAnchors()
mqtt_broker = '127.0.0.1'
client = mqtt.Client() #create new instance
client.username_pw_set("lopos", "LoPoS")
client.on_connect=on_connect
client.on_message=on_message
print("Connecting to mqtt broker...")
#print(mpl.get_backend())
client.connect(mqtt_broker, 1883, 60)
planActions()
client.loop_forever()

#-----------------------------------------------------------
#main loop
#-----------------------------------------------------------
while True:
    #delete from stat where TIMESTAMPDIFF(MINUTE,updated, now()) > 60;
    planActions()
    time.sleep(5)
