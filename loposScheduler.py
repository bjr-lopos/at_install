#!/usr/bin/env python
#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector-python

import time
from datetime import datetime
from collections import deque
import paho.mqtt.client as mqtt
import mysql.connector
import functools
import loposPyLib as loposPy
import localConfig as cfg
import numpy as np


print = functools.partial(print, flush=True)

stats_ActorCnt=0
stats_SFidx=0
stats_SFcnt = 0
disc_ActorCnt=0
disc_SFidx=0
tdoa_ActorCnt=0
tdoa_SFidx=0
uwb_ActorCnt = 0
uwb_SFidx = 0

alt_tdoa_iter = 0

tagPerCoreCell = {} 


def testFwd(dev,anchor): 
    print("Schedule testFwd: ")
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Fwd)    
    SF2fwd = loposPy.getNextSFidxRef()
    SF2sink = loposPy.getNextSFidxRef()
    loposPy.insertTodo(anchor, SF2fwd, cfg.LOPOS_SCENARIO_Stat, 11, 0, 0)
    loposPy.insertTodo(dev, SF2fwd, cfg.LOPOS_SCENARIO_Stat, 1, 0, 0)
    loposPy.insertTodo(0xFFF0, SF2sink, cfg.LOPOS_SCENARIO_Fwd, 0, 0, 0)
    loposPy.insertTodo(anchor, SF2sink, cfg.LOPOS_SCENARIO_Fwd, 1, 0, 0)
    #getNextSFidxRef()

def testTDoA(): 
    print("Schedule testTDoA: ")
    SFidx = loposPy.getNextSFidxRef()
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_TDoA)    
    loposPy.insertTodo(0xFFF0, SFidx, cfg.LOPOS_SCENARIO_TDoA, 0, 0, 0)
    loposPy.insertTodo(0xA009, SFidx, cfg.LOPOS_SCENARIO_TDoA, 1, 0, 0)
    loposPy.insertTodo(0xA014, SFidx, cfg.LOPOS_SCENARIO_TDoA, 2, 0, 0)
    loposPy.insertTodo(0xA01F, SFidx, cfg.LOPOS_SCENARIO_TDoA, 3, 0, 0)
    loposPy.insertTodo(0x1029, SFidx, cfg.LOPOS_SCENARIO_TDoA, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS + 0, 0, 0)
    loposPy.insertTodo(0x1032, SFidx, cfg.LOPOS_SCENARIO_TDoA, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS + 1, 0, 0)
    loposPy.insertTodo(0x1080, SFidx, cfg.LOPOS_SCENARIO_TDoA, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS + 2, 0, 0)

def testAccel(dev): 
    print("Schedule testAccel: ")
    SFrepIdxRef=loposPy.getNextSFrepIdxRef()
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Accel)    
    loposPy.insertTodo(0xFFF0, SFrepIdxRef, cfg.LOPOS_SCENARIO_Accel, 0, 1, 0)
    loposPy.insertTodo(dev, SFrepIdxRef, cfg.LOPOS_SCENARIO_Accel, 1, 1, 0)

def testAnchor(addr): 
    print("Schedule testAnchor: ")
    loposPy.cleanupScenarioActor4dev(cfg.LOPOS_SCENARIO_System, 2, addr)
    numSlots = 3
    for i in range(numSlots):    
        #SFcnt = loposPy.getNextSFidxRef()
        #loposPy.insertTodo(addr, i*(256/numSlots)+6, cfg.LOPOS_SCENARIO_System, 2, 0, 0)
        loposPy.insertTodo(addr, i*80+6, cfg.LOPOS_SCENARIO_System, 2, 0, 0)

def testSinkStress(addr): 
    print("Schedule sinkStress: ")
    numSlots = 120
    for i in range(numSlots):    
        stats_SFidx = loposPy.getNextSFrepIdxRef()
        loposPy.insertTodo(0xFFF0, stats_SFidx, cfg.LOPOS_SCENARIO_Stat, 0, 0, 0)
        #loposPy.insertTodo(addr,   stats_SFidx + 0, cfg.LOPOS_SCENARIO_Stat, 12, 0, 0)


def testDiscover(devRx, devTx): 
    print("Schedule discover: ")
    SFcnt = loposPy.getNextSFidxRef()
    loposPy.insertTodo(0xFFF0, SFcnt, cfg.LOPOS_SCENARIO_Discover, 0, 0, 0)
    loposPy.insertTodo(devRx, SFcnt, cfg.LOPOS_SCENARIO_Discover, 1, 0, 0)
    loposPy.insertTodo(devTx, SFcnt, cfg.LOPOS_SCENARIO_Discover, cfg.LOPOS_SCENARIO_Discover_TAG_OFS + 0, 0, 0)

def testUWB(devRx, devTx): 
    print("Schedule UWB: ")
    SFcnt = loposPy.getNextSFidxRef()
    loposPy.insertTodo(0xFFF0, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 0, 0, 0)
    loposPy.insertTodo(devRx, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 1, 0, 0)
    loposPy.insertTodo(devTx, SFcnt, cfg.LOPOS_SCENARIO_Uwb, 9, 0, 0)

def scheduleStatsCB(addr, last, overdue):
    global stats_ActorCnt
    global stats_SFidx
    global stats_SFcnt
    if (stats_SFcnt > 3):
        return

    #print("scheduleStatsCB: " + hex(addr) + " "+ last + " "+ str(overdue)+ "s"  )
    if stats_ActorCnt == 0:
        loposPy.insertTodo(0xFFF0, stats_SFidx,  cfg.LOPOS_SCENARIO_Stat, stats_ActorCnt, 0, last)
        stats_ActorCnt +=1
    loposPy.insertTodo(addr, stats_SFidx, cfg.LOPOS_SCENARIO_Stat, stats_ActorCnt, 0, last)
    stats_ActorCnt +=1
    if stats_ActorCnt > 10:
        stats_ActorCnt = 0
        stats_SFidx = loposPy.getNextSFidxRef()
        stats_SFcnt += 1

def scheduleStats():
    print("Schedule dev reports: ")
    global stats_ActorCnt
    global stats_SFidx
    global stats_SFcnt
    stats_SFcnt = 0
    stats_ActorCnt = 0
    stats_SFidx = loposPy.getNextSFidxRef()
    loposPy.checkForSchedules("stat", cfg.LOPOS_SCENARIO_Stat, scheduleStatsCB)

def scheduleAccelCB(addr, last, overdue):
    global accel_ActorCnt
    global accel_SFidx
    global accel_SFcnt
    if (accel_SFcnt > 3):
        return
    #print("scheduleAccelCB: " + hex(addr) + " "+ last + " "+ str(overdue)+ "s"  )
    if accel_ActorCnt == 0:
        loposPy.insertTodo(0xFFF0, accel_SFidx,  cfg.LOPOS_SCENARIO_Accel, accel_ActorCnt, 0, last)
        accel_ActorCnt +=1
    loposPy.insertTodo(addr, accel_SFidx, cfg.LOPOS_SCENARIO_Accel, accel_ActorCnt, 0, last)
    accel_ActorCnt +=1
    if accel_ActorCnt > 10:
        accel_ActorCnt = 0
        accel_SFidx = loposPy.getNextSFidxRef()
        accel_SFcnt += 1

def scheduleAccel():
    print("Schedule accel reports: ")
    global accel_ActorCnt
    global accel_SFidx
    global accel_SFcnt
    accel_SFcnt = 0
    accel_ActorCnt = 0
    accel_SFidx = loposPy.getNextSFidxRef()
    loposPy.checkForSchedules("motion", cfg.LOPOS_SCENARIO_Accel, scheduleAccelCB)

def discReqAnchorCellCB(core, edge):
    global disc_ActorCnt
    global disc_SFidx
    loposPy.insertTodo(edge, disc_SFidx,  cfg.LOPOS_SCENARIO_Discover, disc_ActorCnt, 0, 0)
    disc_ActorCnt +=1

def uwbinfoReqAnchorCellCB(core, edge):
    global uwb_ActorCnt
    global uwb_SFidx
    loposPy.insertTodo(edge, uwb_SFidx,  cfg.LOPOS_SCENARIO_Uwb, uwb_ActorCnt, 0, 0)
    uwb_ActorCnt +=1

def tdoaReqAnchorCellCB(core, edge):
    global tdoa_ActorCnt
    global tdoa_SFidx
    loposPy.insertTodo(edge, tdoa_SFidx,  cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, 0)
    tdoa_ActorCnt +=1

def scheduleTdoaCB(addr, last, overdue):
    #print("scheduleTdoaCB: " + hex(addr) + " "+ last + " "+ str(overdue) )
    if (overdue > 64) and (loposPy.findCloseCore(addr,64) is None): 
        global disc_ActorCnt
        global disc_SFidx
        #print("discover") 
        if disc_ActorCnt == 0:
            loposPy.insertTodo(0xFFF0, disc_SFidx,  cfg.LOPOS_SCENARIO_Discover, disc_ActorCnt, 0, last)
            disc_ActorCnt +=1
            loposPy.requestAnchorPerCell(0, cfg.LOPOS_SCENARIO_Discover_TAG_OFS - 1, discReqAnchorCellCB)
            if (disc_ActorCnt < cfg.LOPOS_SCENARIO_Discover_TAG_OFS):
                disc_ActorCnt = cfg.LOPOS_SCENARIO_Discover_TAG_OFS
        loposPy.insertTodo(addr, disc_SFidx, cfg.LOPOS_SCENARIO_Discover, disc_ActorCnt, 0, last)
        disc_ActorCnt +=1
        if disc_ActorCnt > cfg.LOPOS_SCENARIO_Discover_TAG_MAX:
            disc_ActorCnt = 0
            disc_SFidx = loposPy.getNextSFidxRef()
    else :
        global tagPerCoreCell
        core = loposPy.findCloseCore(addr,1000)
        try:
                tagPerCoreCell[core].append(addr)
        except KeyError:
                tagPerCoreCell[core] = [addr]   


def scheduleTdoaGroupsCB(addr, last, overdue):
    #print("scheduleTdoaCB: " + hex(addr) + " "+ last + " "+ str(overdue) )
    tagInfo = loposPy.isTagActive(addr)
    if (tagInfo is None): 
        return
    grp =  tagInfo[1]
    core = tagInfo[2]
    if (last == 0) or (overdue > 96) or (core == -1) : 
        cellsPerGroup = loposPy.getCellsPerGroupActive(grp)
        coreIdx = 0
        if (core != -1): 
            coreIdx = cellsPerGroup.index(core)
            coreIdx = coreIdx + 1
            if (coreIdx >= len(cellsPerGroup)):
                coreIdx = 0
            loposPy.updateTag(addr, core)
        core = cellsPerGroup[coreIdx]
    global tagPerCoreCell
    try:
        tagPerCoreCell[core].append(addr)
    except KeyError:
        tagPerCoreCell[core] = [addr]   


def processTagPerCoreCell() :
    global tagPerCoreCell
    global tdoa_ActorCnt
    global tdoa_SFidx
    tdoa_SFcnt = 0
    print(tagPerCoreCell)
    for core in tagPerCoreCell.keys():
        tdoa_ActorCnt = 0
        tdoa_SFidx = loposPy.getNextSFidxRef() #maybe not used?
        addrList = deque(tagPerCoreCell[core])
        addrList.rotate(alt_tdoa_iter)
        print(core, ":", addrList, " ", len(addrList), " ", tdoa_SFcnt)
        for addr in addrList:
            if tdoa_ActorCnt == 0:
                loposPy.insertTodo(0xFFF0, tdoa_SFidx,  cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, 0)
                tdoa_ActorCnt +=1
                loposPy.insertTodo(0xA000+core, tdoa_SFidx,  cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, 0)
                tdoa_ActorCnt +=1
                loposPy.requestAnchorPerCell(core, cfg.LOPOS_SCENARIO_TDoA_TAG_OFS - 2, tdoaReqAnchorCellCB)
                if (tdoa_ActorCnt < cfg.LOPOS_SCENARIO_TDoA_TAG_OFS):
                    tdoa_ActorCnt = cfg.LOPOS_SCENARIO_TDoA_TAG_OFS
            loposPy.insertTodo(addr, tdoa_SFidx, cfg.LOPOS_SCENARIO_TDoA, tdoa_ActorCnt, 0, 0)
            tdoa_ActorCnt +=1
            if tdoa_ActorCnt > cfg.LOPOS_SCENARIO_TDoA_TAG_MAX:
                tdoa_SFcnt += 1
                if tdoa_SFcnt>=6: 
                    return
                tdoa_ActorCnt = 0
                tdoa_SFidx = loposPy.getNextSFidxRef()
        if tdoa_ActorCnt != 0:
            tdoa_SFcnt += 1
            if tdoa_SFcnt>=6: 
                return


def scheduleTDoA():
    print("Schedule TDoA reports based on location or discovery: ")
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_TDoA)    
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Discover)    
    global disc_ActorCnt
    global disc_SFidx
    disc_ActorCnt = 0
    disc_SFidx = loposPy.getNextSFidxRef() #maybe not used?
    loposPy.getPositionTags()
    loposPy.localizeDiscoverTags(100,-87.0)

    global tagPerCoreCell
    tagPerCoreCell.clear()
    loposPy.checkForSchedules("position", cfg.LOPOS_SCENARIO_TDoA, scheduleTdoaCB)
    processTagPerCoreCell()


def scheduleTDoAAlt():
    global alt_tdoa_iter
    print("Schedule TDoA alt reports: ")
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_TDoA)    
    global tagPerCoreCell
    tagPerCoreCell.clear()
    coreList = deque(cfg.tagPerCoreCellFixed.keys())
    coreList.rotate(alt_tdoa_iter)
    for core in coreList:
        for tagIdx in cfg.tagPerCoreCellFixed[core]:
            try:
                    tagPerCoreCell[core].append(0x1000+tagIdx)
            except KeyError:
                    tagPerCoreCell[core] = [0x1000+tagIdx]   
    processTagPerCoreCell()
    alt_tdoa_iter += 1
    if alt_tdoa_iter >= (17*len(cfg.tagPerCoreCellFixed)):
        alt_tdoa_iter = 0


def scheduleTDoAgroups():
    print("Schedule TDoA reports based on group info: ")
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_TDoA)    
    loposPy.updateActiveTags(500) 

    global tagPerCoreCell
    tagPerCoreCell.clear()
    loposPy.checkForSchedules("position", cfg.LOPOS_SCENARIO_TDoA, scheduleTdoaGroupsCB)
    processTagPerCoreCell()


def uwbInfoAllCells():
    global uwb_ActorCnt        
    global uwb_SFidx
    for core in loposPy.getCoreAnchors():
        print ("core is :", core)
        uwb_SFidx = loposPy.getNextSFidxRef()
        uwb_ActorCnt = 0
        loposPy.insertTodo(0xFFF0, uwb_SFidx,  cfg.LOPOS_SCENARIO_Uwb, uwb_ActorCnt, 0, 0)
        uwb_ActorCnt +=1
        loposPy.requestAnchorPerCell(core, cfg.LOPOS_SCENARIO_UWB_TAG_OFS - 1, uwbinfoReqAnchorCellCB)
        if (uwb_ActorCnt < cfg.LOPOS_SCENARIO_UWB_TAG_OFS):
            uwb_ActorCnt = cfg.LOPOS_SCENARIO_UWB_TAG_OFS
        loposPy.insertTodo(core, uwb_SFidx, cfg.LOPOS_SCENARIO_Uwb, uwb_ActorCnt, 0, 0)


def analyzeOpportunities(x,y,dx,dy,txA, rxA):
    global uwb_ActorCnt
    global uwb_SFidx
    if len(rxA)==0 or len(txA)==0:
        print("Abort analyzeOpportunities len(rxA) vs len(txA)", len(rxA), len(txA) )
        return
    uwb_ActorCnt = 0
    uwb_SFidx = loposPy.getNextSFidxRef() #maybe not used?
    loposPy.insertTodo(0xFFF0, uwb_SFidx,  cfg.LOPOS_SCENARIO_Uwb, uwb_ActorCnt, 0, 0)
    uwb_ActorCnt +=1
    for rxAe in rxA:
        if (int(rxAe) & 0xF000) == 0xA000:
            loposPy.insertTodo(int(rxAe), uwb_SFidx,  cfg.LOPOS_SCENARIO_Uwb, uwb_ActorCnt, 0, 0)
            uwb_ActorCnt +=1
    if (uwb_ActorCnt < cfg.LOPOS_SCENARIO_UWB_TAG_OFS):
        uwb_ActorCnt = cfg.LOPOS_SCENARIO_UWB_TAG_OFS
    for txAe in txA:
        loposPy.insertTodo(int(txAe), uwb_SFidx,  cfg.LOPOS_SCENARIO_Uwb, uwb_ActorCnt, 0, 0)
        uwb_ActorCnt +=1

def altIUwbInfolvoScan():
	maxx=6
	maxy=5
	anchors = np.array([ 
			[ 0xA00A,		-1,		-1,	0xA00E,	0xA00F,	0xA010],
			[ 0xA00B,	0xA009,	0x1002,	0xA00D,	0xA014,	0xA011],
			[ 0xA003,	0xA004,	0xA005,	0xA00C,	0xA013,	0xA012],
			[ 0xA002,	0xA000,	0xA006,		-1,		-1,		-1],
			[ 0xA001,	0xA008,	0xA007,		-1,		-1,		-1]
	])
	for x in range (0, maxx):
		for dx in (-1,1):
			rxA = []
			txA = []
			if x+dx < 0:
				continue
			if x+dx >= maxx:
				continue
			for y in range (0, maxy):
				if anchors[y,x] != -1:
					txA.append(anchors[y,x])
				if anchors[y,x+dx] != -1:
					rxA.append(anchors[y,x+dx])
			analyzeOpportunities(x,0,dx,0,txA, rxA)
	for y in range (0, maxy):
		rxA = []
		txA = []
		for dy in (-1,1):
			if y+dy < 0:
				continue
			if y+dy >= maxy:
				continue
			for x in range (0, maxx):
				if x % 2 != 0: 
					continue
				if anchors[y,x] not in txA and  anchors[y,x] != -1:
					txA.append(anchors[y,x])
				if anchors[y+dy,x] != -1:
					rxA.append(anchors[y+dy,x])
		analyzeOpportunities(x,y,dx,dy,txA, rxA)
		rxA = []
		txA = []
		for dy in (-1,1):
			if y+dy < 0:
				continue
			if y+dy >= maxy:
				continue
			for x in range (0, maxx):
				if x % 2 == 0: 
					continue
				if anchors[y,x] not in txA and  anchors[y,x] != -1:
					txA.append(anchors[y,x])
				if anchors[y+dy,x] != -1:
					rxA.append(anchors[y+dy,x])
		analyzeOpportunities(x,y,dx,dy,txA, rxA)

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
    loposPy.wrappedESqlDoCommitAndSetInstant(1)
    loposPy.deleteOldSchedules(2)
    loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Stat)
    loposPy.wrappedESqlDoCommitAndSetInstant(0)

    if hasattr(cfg, 'uwbInfoAllCells'):
        uwbInfoAllCells()
    if hasattr(cfg, 'altIUwbInfolvoScan'):
        altIUwbInfolvoScan()

    if hasattr(cfg, 'scheduleTDoAwGroups'):
        scheduleTDoAgroups()
    else: 
        if hasattr(cfg, 'tagPerCoreCellFixed'):
            scheduleTDoAAlt()
        else:
            scheduleTDoA()

    scheduleAccel()
    scheduleStats()

    if hasattr(cfg, 'testAnchor'):
        if cfg.testAnchor == 1:
            testAnchor(0xA01E)

    if hasattr(cfg, 'testSinkStress'):
        if cfg.testSinkStress == 1:
            testSinkStress(0xA001)

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
            loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Discover)
            testDiscover(0xA014, 0xA009)
            testDiscover(0xA009, 0xA014)

    if hasattr(cfg, 'testUWB'):
        if cfg.testUWB == 1:
            loposPy.cleanupScenario(cfg.LOPOS_SCENARIO_Uwb)
            #loposPy.insertTodo(0xA009, 0x38, cfg.LOPOS_SCENARIO_System, 24, 0, 0)
            #testUWB(0xA009, 0xA014)
            #testUWB(0xA014, 0xA009)
            #loposPy.insertTodo(0xA001, 0xC0, cfg.LOPOS_SCENARIO_System, 24, 0, 0)
            #loposPy.insertTodo(0xA002, 0xC0, cfg.LOPOS_SCENARIO_System, 24, 0, 0)
            #loposPy.insertTodo(0xA002, 0x38, cfg.LOPOS_SCENARIO_System, 24, 0, 0)
            #testUWB(0xA002, 0xA001)
            #testUWB(0xA001, 0xA002)

    loposPy.wrappedESqlDoCommitAndSetInstant(0)
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
loposPy.updateCellsPerGroup()
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
