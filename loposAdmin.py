#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector

import time
import sys
import mysql.connector
import functools
print = functools.partial(print, flush=True)
import argparse
import loposPyLib as loposPy
import localConfig as cfg

#-----------------------------------------------------------
#Actions
#-----------------------------------------------------------
loposPy.initDB()
parser = argparse.ArgumentParser()
parser.add_argument("type", help="sink/anchor/tag/all")
parser.add_argument("id", type=int, help="id of the device.")
parser.add_argument("action", help="reset/dfu")
parser.add_argument("version", type=int, help="dfu ref version")
args=parser.parse_args()



addr = 0
addr = args.id
if args.type=='anchor':
    addr += 0xA000
if args.type=='tag':
    addr += 0x1000
if args.type=='sink':
    addr += 0xFFF0

if args.action=='clearDFU':
    loposPy.cleanupScenarioActor(cfg.LOPOS_SCENARIO_System,16)
    loposPy.updateSysBeaconId(0xA5)
    sys.exit()


if args.type=='all':
    if args.action=='reset':
        loposPy.updateSysBeaconId(0xFB)
        time.sleep(16)
        loposPy.updateSysBeaconId(0xA5)
    if args.action=='dfu':
        loposPy.updateSysBeaconId(0xFD)
        time.sleep(32)
        loposPy.updateSysBeaconId(0xA5)
    sys.exit()

if args.type=='sink':
    if args.action=='reset':
        loposPy.updateSysBeaconId(0xFA)
        time.sleep(16)
        loposPy.updateSysBeaconId(0xA5)
        #loposPy.insertTodo(0xFFF0, 1, cfg.LOPOS_SCENARIO_System, 17, 0, 0)
        sys.exit()
    if args.action=='dfu':
        #loposPy.updateSysBeaconId(0xFC)
        #time.sleep(32)
        #loposPy.updateSysBeaconId(0xA5)
        #loposPy.insertTodo(addr, 1, cfg.LOPOS_SCENARIO_System, 16, 0, 0)
        print("Handle as default")


SFid=1
if hasattr(args, 'version'):
    SFid= (args.version & 0x03FF)

print("Default for addr is 0x", hex(addr), "and ref version (10bit) 0x",hex(SFid),"/",SFid)
if args.action=='reset':
    loposPy.cleanupScenarioActor4dev(cfg.LOPOS_SCENARIO_System, 17, addr)
    loposPy.insertTodo(addr, 1, cfg.LOPOS_SCENARIO_System, 17, 0, 0)
if args.action=='dfu':
    loposPy.cleanupScenarioActor4dev(cfg.LOPOS_SCENARIO_System, 16, addr)
    loposPy.insertTodo(addr, SFid, cfg.LOPOS_SCENARIO_System, 16, 0, 0)
sys.exit()

