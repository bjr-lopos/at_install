#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector

import json
import time
import mysql.connector
import functools
print = functools.partial(print, flush=True)
import argparse

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

def insertTodo(addr, SFcnt, scenario, actor, repeat, last):
    iSql="insert into todo (addr, scheduleAT, scenario, actor, rescheduleSF) values (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE updated=now()"
    try:
        print("Will schedule @", SFcnt, ":", actor, "4dev:", addr, " last was @ ", last)
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


#-----------------------------------------------------------
#Actions
#-----------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("type", help="sink/anchor/tag")
parser.add_argument("id", type=int, help="id of the device.")
parser.add_argument("action", help="reset/dfu")
args=parser.parse_args()
addr = 0
if args.type=='sink':
    if args.action=='reset':
        updateSysBeaconId(0xFA)
        time.sleep(60)
        updateSysBeaconId(0xA5)
    if args.action=='dfu':
        updateSysBeaconId(0xFC)
        time.sleep(60)
        updateSysBeaconId(0xA5)
if args.type=='anchor':
    addr = 0xA000 + args.id
if args.type=='tag':
    addr = 0x1000 + args.id
print(f"Addr is 0x{addr:X}")
if args.action=='reset':
    insertTodo(addr, 1, 0, 17, 0, 0)
if args.action=='dfu':
    insertTodo(addr, 1, 0, 16, 0, 0)

