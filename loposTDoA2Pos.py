#sudo apt-get install python-scipy
#pip3 install scipy
#pip3 install paho-mqtt python-etcd
#pip3 install mysql-connector-python-rf
#python3 -m pip install mysql-connector

import numpy as np
import csv
import json
import numpy
import scipy.optimize as optimization
import time
import paho.mqtt.client as mqtt
import mysql.connector
import functools
print = functools.partial(print, flush=True)

mydb = mysql.connector.connect(
  host="localhost",
  user="lopos_test",
  passwd="lopos_test",
  database="lopos_test"  
)
#print(mydb)
mycursor = mydb.cursor()

mycursor.execute("""
SELECT max(id)+1 as maxAnchor
FROM anchor as a
""" )
records = mycursor.fetchall()
for row in records:
    numAnchors = row[0]

print("Overdimension the number of anchors to: ", numAnchors)


mycursor.execute("""
SELECT a.id as id, a.addr as addr, hex(a.addr) as addrX, p.x as x, p.y as y, p.z as z
FROM position as p, anchor as a, (select addr, max(updated) as updated from position group by addr) as recent 
where p.addr=recent.addr and recent.updated=p.updated and p.addr=a.addr 
order by 1 
""" )
records = mycursor.fetchall()
#numAnchors = mycursor.rowcount
interDistAnchor = np.zeros( (numAnchors, numAnchors) )
anchorPosition = np.zeros( (numAnchors, 3) )
for rowA in records:
    Aid=rowA[0]
    Ax=rowA[3]
    Ay=rowA[4]
    Az=rowA[5]
    anchorPosition[Aid] = [Ax, Ay, Az]
    for rowB in records:
        Bid=rowB[0]
        Bx=rowB[3]
        By=rowB[4]
        Bz=rowB[5]
        interDistAnchor[Aid,Bid]=((Ax-Bx)**2+(Ay-By)**2+(Az-Bz)**2)**(.5)

print("Selected the most recent anchor positions from database:")
print(anchorPosition)

print("Calculated the anchor interdistances based on most recent positions from database:")
print(interDistAnchor)

mqtt_broker = '127.0.0.1'
client = mqtt.Client() #create new instance
client.username_pw_set("lopos", "LoPoS")


tagz = 30 #2.5D, we predefine the tags height.

def calculateAndPlotPosition(jsondata):
    #HFid=jsondata['hf']
    #SFid=jsondata['sf']
    ASNid=jsondata['asn']
    DEVid=jsondata['dev']
    anchorSync=jsondata['sync']

    AnchorsAx=[]
    AnchorsAy=[]
    AnchorsAz=[]

    AnchorsBx=[]
    AnchorsBy=[]
    AnchorsBz=[]

    DDoAValues=[]
    
    #for ddoaEntry in jsondata['ddoa']:
    #    print("row", ddoaEntry)
    
    for ddoaEntry in jsondata['ddoa']:
        anchorA = ddoaEntry['a']
        anchorB = ddoaEntry['b']
        ddoa = ddoaEntry['v']
        #print("will look up ", anchorA, anchorB, anchorSync)
        ddoaAdj= ddoa + (interDistAnchor[anchorA,anchorSync] - interDistAnchor[anchorB,anchorSync])
        #ddoaAdj= ddoaAdj/2.0
        print("adjusted  A:", anchorA, " B: ", anchorB, " S: ", anchorSync, " DDoA: ", ddoaAdj, " DAS: ", interDistAnchor[anchorA,anchorSync], " DBS: ", interDistAnchor[anchorB,anchorSync])
        AnchorsAx.append(anchorPosition[anchorA,0])
        AnchorsAy.append(anchorPosition[anchorA,1])
        AnchorsAz.append(anchorPosition[anchorA,2])
        AnchorsBx.append(anchorPosition[anchorB,0])
        AnchorsBy.append(anchorPosition[anchorB,1])
        AnchorsBz.append(anchorPosition[anchorB,2])
        DDoAValues.append(ddoaAdj)
    startGuess = (anchorPosition[anchorSync,0], anchorPosition[anchorSync,1])
    Xmin = min(min(AnchorsAx),min(AnchorsBx))
    Ymin = min(min(AnchorsAy),min(AnchorsBy))
    Xmax = max(max(AnchorsAx),max(AnchorsBx))
    Ymax = max(max(AnchorsAy),max(AnchorsBy))
    Xrange=Xmax-Xmin
    Yrange=Ymax-Ymin
    Xmin=Xmin-Xrange*0.5
    Ymin=Ymin-Yrange*0.5
    Xmax=Xmax+Xrange*0.5
    Ymax=Ymax+Yrange*0.5
    print (Xmin, Ymin, Xmax, Ymax)
    #to be defined
    bnds=((Xmin, Ymin), (Xmax, Ymax))
    t1=int(round(time.time() * 1000))
    result = optimization.curve_fit(
        func_curvefit,
        (AnchorsAx,AnchorsAy,AnchorsAz,AnchorsBx,AnchorsBy,AnchorsBz), 
        DDoAValues, 
        p0=startGuess,
        method='trf',
        bounds=bnds)[0]
    t2=int(round(time.time() * 1000))
    jsonObj = {
        "asn":ASNid,
        "dev":DEVid,
        "x":result[0],
        "y":result[1],
        "z":tagz,
        "t":t2-t1
    }
    print(jsonObj)
    sql="insert into position (addr, asn, x, y, z) values (%s,%s,%s,%s,%s)"
    val=( DEVid, ASNid, int(round(result[0])), int(round(result[1])), int(round(tagz)) )
    print(sql, val)
    try:
        mycursor.execute(sql, val)
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
    print(mycursor.rowcount, "record inserted.")    

def on_connect(client, userdata, message,rc):
    print("Connected to mqtt broker")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("loposcore/ddoa")
    print("subscribed to loposcore/ddoa")

def on_message(client, userdata, message):
    payload=str(message.payload.decode("utf-8"))
    #print(message.topic)
    if(message.topic == "loposcore/ddoa"): 
        #payloadJson = json.loads(message.payload.decode(r.info().get_param('charset') or 'utf-8'))    
        payloadJson = json.loads(payload)    
        print(payloadJson)
        calculateAndPlotPosition(payloadJson)


# The function whose square is to be minimised.
# params ... list of parameters tuned to minimise function.
# Further arguments:
# xdata ... design matrix for a linear model.
# ydata ... observed data.
def func_curvefit(anchorPositions,tagx,tagy):
    edgex, edgey,edgez,corex,corey,corez = anchorPositions 
    # print(str(tagx) + " "+str(tagy))
    return (((edgex-tagx)**2+(edgey-tagy)**2+(edgez-tagz)**2)**(.5)-(((corex-tagx)**2+(corey-tagy)**2+(corez-tagz)**2))**(.5))

def func_leastsquares(tagposition,edgex, edgey,edgez,corex,corey,corez,ddoa):
    # print(edgex)
    tagx = tagposition[0]
    tagy = tagposition[1]
    print(tagx)
    # edgex, edgey,edgez,corex,corey,corez,ddoa = anchorPositions 
    toBeMinimized = (((edgex-tagx)**2+(edgey-tagy)**2+(edgez-tagz)**2)**(.5)-(((corex-tagx)**2+(corey-tagy)**2+(corez-tagz)**2))**(.5))-ddoa
    print(toBeMinimized)
    return toBeMinimized

client.on_connect=on_connect
client.on_message=on_message
print("Connecting to mqtt broker...")
#print(mpl.get_backend())
client.connect(mqtt_broker, 1883, 60)

client.loop_forever()
