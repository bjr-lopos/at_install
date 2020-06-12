#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector

import json
import time
import paho.mqtt.client as mqtt
import mysql.connector
import functools
print = functools.partial(print, flush=True)


#-----------------------------------------------------------
#Database
#-----------------------------------------------------------
mydb = mysql.connector.connect(
  host="localhost",
  user="lopos_test",
  passwd="lopos_test",
  database="lopos_test"  
)
#print(mydb)
mycursor = mydb.cursor()


def insertTodo(addr, SFcnt, scenario, actor, repeat, last):
    iSql="insert into todo (addr, scheduleAT, scenario, actor, rescheduleSF) values (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE updated=now()"
    try:
        print("Will schedule @", SFcnt, ":", actor, "4dev:", hex(addr), " last was @ ", last)
        mycursor.execute(iSql, (addr, SFcnt, scenario, actor, repeat))
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

def testAnchor(addr): 
    LOPOS_SF_BLOCK_SIZE=8
    scenarioJustSink=0
    actorCnt=1
    dSql="delete from todo where addr=%(anchor_test_id)s and scenario=%(scenario)s and actor=1"
    mycursor.execute(dSql, {'anchor_test_id':addr, 'scenario':scenarioJustSink} )
    mydb.commit()
    SFcnt = 80
    for i in range(10):    
        if SFcnt % LOPOS_SF_BLOCK_SIZE < 3:
            SFcnt +=3 - (SFcnt % LOPOS_SF_BLOCK_SIZE)
        if SFcnt % LOPOS_SF_BLOCK_SIZE > 4:
            SFcnt += (LOPOS_SF_BLOCK_SIZE +3) - (SFcnt % LOPOS_SF_BLOCK_SIZE)
        insertTodo(addr, SFcnt, scenarioJustSink, actorCnt, 0, 0)
        SFcnt +=1

def scheduleStats():
    print("Schedule dev reports: ")
    scenarioStat=7
    LOPOS_SF_BLOCK_SIZE=8
    actorCnt = 0
    SFcnt = 80
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
                scenario = 7 and ((s.last_update IS NULL) or (TIMESTAMPDIFF(SECOND,s.last_update,now()) > ( p.interval -10) ) )
            order by 2;        
        """ )
        records = mycursor.fetchall()
        for needStatSchedule in records:
            #print(locals())
            if SFcnt % LOPOS_SF_BLOCK_SIZE == 0:
                SFcnt +=5
            if actorCnt == 0:
                insertTodo(0xFFF0, SFcnt, scenarioStat, actorCnt, 0, needStatSchedule[1])
                actorCnt +=1
            insertTodo(needStatSchedule[0], SFcnt, scenarioStat, actorCnt, 0, needStatSchedule[1])
            actorCnt +=1
            if actorCnt > 10:
                actorCnt = 0
                SFcnt +=1
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
    dSql="delete from todo using todo,sys where TIMESTAMPDIFF(SECOND,todo.updated,now()) > ((sys.SFticks * sys.SFmax)/32768) "
    print("Schedule iteration (will clean up old todo): ")
    mycursor.execute(dSql)
    mydb.commit()
    testAnchor(0xA001)
    scheduleStats()

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
    planActions()
    time.sleep(5)
