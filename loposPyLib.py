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
activeTag = {}
cellsPerGroup = {}
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
            IFNULL(numHyperbola,0) = 0;
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
                1 as weight -- plain center-of-mass: every anchor that picked the tag up
                            -- counts equally (was RSSI-bucket weighted 10/7/1/0)
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
    print("Discovered:", discoveredTag)

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

def updateActiveTags(maxAge):
    global activeTag
    sql="""
        select 
            s.addr as addr, 
            timestampdiff(second, max(updated), now()) as age, 
            t.group as grp 
        from 
            stat as s,
            tag as t 
        where 
            t.addr=s.addr and 
            timestampdiff(second, updated, now()) < %(maxAge)s
        group by 
            s.addr
        order by 1
    """

    # Liveness gate, symmetric: a tag is schedulable only while it keeps PROVING presence
    # (a stat report within maxAge). Tags whose stat goes quiet are DROPPED -- no reason to
    # spend TDoA slots on a device that is not responding; they re-enter (cold start, the
    # proactive CB handles core=-1) on their next stat success. Entries used to persist for
    # the process lifetime with age=-1, which kept scheduling long-gone tags until a restart.
    records = wrappedSql(sql, {'maxAge':maxAge})
    if records is None:
        return                      # transient DB error: keep the current set unchanged
    fresh = {}
    for tag in records:
        addr=tag[0]
        age=tag[1]
        grp=tag[2]
        lastCell = -1
        tagInfo =  activeTag.get(addr)
        if (tagInfo is not None):
            lastCell = tagInfo[2]
        fresh[addr] = [age, grp, lastCell]
    dropped = sorted(set(activeTag) - set(fresh))
    if dropped:
        print("activeTag: dropped (no stat in", maxAge, "s):", dropped)
    activeTag.clear()
    activeTag.update(fresh)
    print("Len dict activeTag: ", len(activeTag))


def isTagActive(addr):
    return activeTag.get(addr)    

def updateTag(addr, lastCell):
    tagInfo =  activeTag.get(addr)
    diff=tagInfo[0]
    grp=tagInfo[1]
    activeTag[addr] = [diff, grp, lastCell]


def updateCellsPerGroup():
    global cellsPerGroup
    cellsPerGroup.clear()
    sql="""
        select 
            1, id 
        from 
            anchor 
        where 
            anchor.group & 1 = 1
    UNION
        select 
            2, id 
        from 
            anchor 
        where 
            anchor.group & 2 = 2
    UNION
        select 
            3, id 
        from 
            anchor 
        where 
            anchor.group & 4 = 4
    UNION
        select 
            4, id 
        from 
            anchor 
        where 
            anchor.group & 8 = 8
    UNION
        select 
            5, id 
        from 
            anchor 
        where 
            anchor.group & 0x10 = 0x10
    UNION
        select 
            6, id 
        from 
            anchor 
        where 
            anchor.group & 0x20 = 0x20
    UNION
        select 
            7, id 
        from 
            anchor 
        where 
            anchor.group & 0x40 = 0x40
    UNION
        select 
            8, id 
        from 
            anchor 
        where 
            anchor.group & 0x80 = 0x80
    order by 1;
    """
    records = wrappedSql(sql, {})
    if records is None:
        return
    for cell in records:
        grp=cell[0]
        core=cell[1]
        try:
            cellsPerGroup[grp].append(core)
        except KeyError:
            cellsPerGroup[grp] = [core]

def getCellsPerGroupActive(grp):
    return cellsPerGroup.get(grp)    


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
        cDist = ((dx-cx)**2+(dy-cy)**2+(dz-cz)**2)**(.5)
        if cDist < lDist: 
            coreIdx = core
            lDist = cDist
    #print("Dist is: ", str(lDist))
    return coreIdx


# -----------------------------------------------------------
# Proactive, group-aware cell selection (toggle: cfg.tdoaProactiveCell).
# Picks the cell whose coverage polygon contains the tag, else the nearest core, restricted to the
# tag's group. Uses a SMOOTHED tag position (median over recent fixes) so a single faulty fix does
# not move the choice. Hysteresis (switch margin) is folded in here; min-dwell + the round-robin
# quality fallback live in the scheduler callback. Reception/geometry data, positions and group
# membership all already exist; no C-core change.
# -----------------------------------------------------------
cellFootprint = {}      # core -> [(x,y), ...] convex hull of the cell's anchors (cores + edges)
cellCOM = {}            # core -> (x,y) center of mass of ALL the cell's anchors (core + edges)


def _convexHull(pts):
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _pointInPoly(x, y, poly):
    inside = False; n = len(poly); j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def updateCellFootprints():
    """Load each cell's coverage polygon (convex hull of its anchors) for in-cell selection,
    plus the cell's center of mass (mean of ALL member anchors: core + edges) used as the
    cell's reference point for nearest-cell distances.
    Cached; needs positionAnchor (all anchors) + the cell table. Same hull model as curateCells."""
    global cellFootprint, cellCOM
    if len(cellFootprint) > 0:
        return
    getPositionAnchors()
    records = wrappedSql("SELECT core, edge FROM cell ORDER BY core", {})
    if records is None:
        return
    edges = {}
    for core, edge in records:
        edges.setdefault(int(core), []).append(int(edge))
    for core, es in edges.items():
        pts = []
        for a in [core] + es:
            p = positionAnchor.get(a)
            if p and p[0] is not None:
                pts.append((float(p[0]), float(p[1])))
        if pts:
            cellCOM[core] = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
        if len(pts) >= 3:
            hull = _convexHull(pts)
            if len(hull) >= 3:
                cellFootprint[core] = hull


def _median(vals):
    s = sorted(vals); n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def getPositionTagsMedian(samples, window):
    """Like getPositionTags but stores the per-tag MEDIAN of the last <=`samples` fixes within
    `window` seconds, instead of the single latest row -> robust to one faulty position.
    age = freshest sample's age."""
    global positionTag
    positionTag.clear()
    sql = """
        select p.addr, p.x, p.y, p.z, TIMESTAMPDIFF(SECOND, p.updated, now()) as age
        from position as p
        where p.addr & 0xF000 = 0x1000
          and TIMESTAMPDIFF(SECOND, p.updated, now()) < %(window)s
        order by p.addr, p.updated desc
    """
    records = wrappedSql(sql, {'window': window})
    if records is None:
        return
    bucket = {}
    for addr, x, y, z, age in records:
        bucket.setdefault(addr, []).append((x, y, z, age))
    for addr, rows in bucket.items():
        rows = rows[:samples]
        mx = _median([float(r[0]) for r in rows])
        my = _median([float(r[1]) for r in rows])
        mz = _median([float(r[2]) for r in rows])
        age = min(r[3] for r in rows)
        positionTag[addr] = [mx, my, mz, age]


def tagGoodFixAge(addr, minHyper):
    """Seconds since the tag's last GOOD position fix (numHyperbola >= minHyper); None if never.
    The closed-loop quality signal for the proactive scheduler -- no C-core change needed."""
    rec = wrappedSql(
        "select TIMESTAMPDIFF(SECOND, max(updated), now()) from position "
        "where addr=%(addr)s and IFNULL(numHyperbola,0) >= %(minHyper)s",
        {'addr': addr, 'minHyper': minHyper})
    if rec and rec[0] and rec[0][0] is not None:
        return rec[0][0]
    return None


def findCloseCoreInGroup(dev, grp, maxage, current=-1, margin=0.0):
    """Proactive group-aware cell pick. Among the cores serving group `grp`, prefer the cell whose
    coverage polygon contains the tag, else the cell whose center of mass (mean of ALL its
    anchors, not just the core) is nearest -- pairs naturally with the discoveredTag fallback,
    itself a center of mass of the anchors that picked the tag up. With hysteresis: if `current`
    is one of the group's cores, keep it unless the new best is closer by more than `margin`.
    Returns a core id, or None when no usable (fresh) tag position is known -> caller falls back to
    round-robin (cold start / quality fallback)."""
    cores = cellsPerGroup.get(grp)
    if not cores:
        return None
    pos = positionTag.get(dev)
    if (pos is None) or (pos[3] >= maxage):
        pos = discoveredTag.get(dev)
        if pos is None:
            return None
    dx = float(pos[0]); dy = float(pos[1])
    updateCellFootprints()
    def _ref(c):                            # cell reference point: COM, core anchor as fallback
        return cellCOM.get(c) or positionCoreAnchor.get(c)
    contains = [c for c in cores
                if c in cellFootprint and _pointInPoly(dx, dy, cellFootprint[c])]
    pool = contains if contains else [c for c in cores if _ref(c)]
    best = None; lDist2 = None
    for core in pool:
        cp = _ref(core)
        if not cp:
            continue
        d2 = (dx - float(cp[0]))**2 + (dy - float(cp[1]))**2
        if lDist2 is None or d2 < lDist2:
            lDist2 = d2; best = core
    if best is None:
        return None
    # hysteresis: keep the current cell unless the new best beats it by more than `margin`
    if current != -1 and current in cores and _ref(current) and best != current:
        cp = _ref(current)
        curD = ((dx - float(cp[0]))**2 + (dy - float(cp[1]))**2) ** 0.5
        bestD = lDist2 ** 0.5
        if (curD - bestD) <= margin:
            return current
    return best


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



def checkUwbTxPwr(_reqUpdateUwbTxPwrCB = None):
    print("checkUwbTxPwr adjusting the UWB tx Power if needed")
    sql = """
        SELECT
            d.addr,
            ((6 - (s.uwbTxPwr div 32)) * 3) + round((s.uwbTxPwr & 0x01F)/2) as isUwbTxPwr,
            d.uwbTxPower as setUwbTxPwr
        FROM
            device as d,
            stat as s,
            (select addr, max(updated) as last_update from stat group by addr) as ref
        WHERE
            s.addr = d.addr and
            s.addr = ref.addr and
            s.updated = ref.last_update and
            d.uwbTxPower > 0 and
            d.uwbTxPower <> ((6 - (s.uwbTxPwr div 32)) * 3) + round((s.uwbTxPwr & 0x01F)/2);
    """
    records = wrappedSql(sql, {} )
    for needUwbTxPwrSchedule in records:
        addr = needUwbTxPwrSchedule[0]
        newUwbTxPwr = needUwbTxPwrSchedule[2]
        if _reqUpdateUwbTxPwrCB:
            #print ("will call cb")
            _reqUpdateUwbTxPwrCB(addr, newUwbTxPwr)




#every planned scenario has a result table, we will search for devices which have an overdue scenario
#WHEN ref.last_update IS NULL THEN p.interval/2 

def checkForSchedules(table, scenario, _reqScheduleCB = None):
    sql = """
        SELECT
            p.addr, 
            CASE 
                WHEN ref.last_update IS NULL THEN 0 
                else DATE_ADD(ref.last_update, INTERVAL p.interval SECOND) 
            end as schedule,
            CASE 
                WHEN ref.last_update IS NULL THEN (round(100 * 0.5 * (1 - rand())))
                else round( 100* (TIMESTAMPDIFF(SECOND,ref.last_update,now()) - p.interval) / p.interval)
            end as diff,
            p.interval as p_interval
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
        interval = needSchedule[3]
        if _reqScheduleCB:
            #print ("will call cb")
            _reqScheduleCB(addr, last, overdue, interval)

def checkForSchedulesFixed(table, scenario, _reqScheduleCB = None):
    sql = """
        SELECT
            p.addr, 
            CASE 
                WHEN ref.last_update IS NULL THEN 0 
                else DATE_ADD(ref.last_update, INTERVAL p.interval SECOND) 
            end as schedule,
            CASE 
                WHEN ref.last_update IS NULL THEN (round(100 * 0.5 * (1 - rand())))
                else round( 100* (TIMESTAMPDIFF(SECOND,ref.last_update,now()) - p.interval) / p.interval)
            end as diff,
            p.interval as p_interval
        FROM 
            sys,
            plan as p
        LEFT JOIN 
            (select addr, max(updated) as last_update from """ + table + """ group by addr) as ref
        ON    
            p.addr = ref.addr	
        where 
            scenario = %(scenario)s 
        order by 1;        
    """
    records = wrappedSql(sql, {'scenario':scenario} )
    for needSchedule in records:
        addr = needSchedule[0]
        last = needSchedule[1]
        overdue = needSchedule[2]
        interval = needSchedule[3]
        if _reqScheduleCB:
            #print ("will call cb")
            _reqScheduleCB(addr, last, overdue, interval)


#-----------------------------------------------------------
#SFidxRef and SFrepIdxRef
#-----------------------------------------------------------

SFidxRef=0
SFrepIdxRef=0
SFrepWrapped=False      # claimRepeatingAndfixedSF rotated past LOPOS_LAST_USABLE_SF this cycle
SFrepCycleStart=None    # first slot claimed this planning cycle (overstress guard after a rotate)
SFrepPrevCycleStart=None # first slot of the PREVIOUS cycle: this cycle must stop before it so
                         # one-HF-late devices replaying last HF's slots always hit silent SFs

def keepOutRepeatingAndfixedSF(SFid):
    adjust2allowedOffsets = {0:0, 1:0, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1}  
    if SFid <= cfg.LOPOS_LAST_FIXED_SF:
        SFid = cfg.LOPOS_LAST_FIXED_SF + 1
    if SFid >cfg.LOPOS_LAST_USABLE_SF:
        deleteOldSchedules(0)
        print("ERROR: Hyperframe !")
        sys.exit()
    blockOfs = SFid % cfg.LOPOS_SF_BLOCK_SIZE
    SFid += adjust2allowedOffsets[blockOfs]
    return SFid        

def isSFslotFree(SFid):
    """Post-rotate safety: a wrapped-to slot is only reusable when no pending todo still
    references it (e.g. one-shot tasks of the previous HF not yet consumed/aged out)."""
    records = wrappedSql("select count(*) from todo where scheduleAT = %(SFid)s", {'SFid': SFid})
    if records is None:
        return True
    return records[0][0] == 0

def claimRepeatingAndfixedSF(SFid):
    """Moving TDoA window: instead of failing past LOPOS_LAST_USABLE_SF, rotate back to
    LOPOS_FIRST_REPEAT_SF+1 (right after the last provisioning/fixed slot). Block offsets
    0-1 stay reserved (adjust2allowedOffsets). After a rotate every slot is checked to be
    free (isSFslotFree) and a full lap back to this cycle's start = real overstress."""
    global SFrepWrapped
    adjust2allowedOffsets = {0:2, 1:1, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0}
    if SFid <= cfg.LOPOS_FIRST_REPEAT_SF:
        SFid = cfg.LOPOS_FIRST_REPEAT_SF+ 1
    while True:
        if SFid > cfg.LOPOS_LAST_USABLE_SF:
            SFrepWrapped = True
            SFid = cfg.LOPOS_FIRST_REPEAT_SF + 1
        SFid += adjust2allowedOffsets[SFid % cfg.LOPOS_SF_BLOCK_SIZE]
        if SFid > cfg.LOPOS_LAST_USABLE_SF:
            continue                            # offset adjust crossed the end -> rotate
        if SFrepWrapped:
            if (SFrepCycleStart is not None) and (SFid >= SFrepCycleStart):
                deleteOldSchedules(0)
                print("ERROR: Hyperframe overstressed!")
                sys.exit()
            if not isSFslotFree(SFid):
                SFid += 1
                continue
        return SFid

def initSFidxRef():
    global SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(0)
    return SFidxRef

def getNextSFidxRef(inter_sf = 1):
    global SFidxRef
    SFidxCurr = SFidxRef
    SFidxRef = keepOutRepeatingAndfixedSF(SFidxCurr+inter_sf)
    return SFidxCurr


def _repPoolFwdDist(frm, to):
    """Forward distance frm -> to inside the repeating pool, wrapping at LOPOS_LAST_USABLE_SF."""
    if to == frm:
        return 0
    if to > frm:
        return to - frm
    return (cfg.LOPOS_LAST_USABLE_SF - frm) + (to - (cfg.LOPOS_FIRST_REPEAT_SF + 1))

def repPoolRemaining():
    """Slots left in the repeating pool this planning cycle before reaching the PREVIOUS
    cycle's start. Stopping there keeps consecutive HFs slot-disjoint (the moving-window
    goal: a one-HF-late replay lands in a silent SF). Callers like uwbScanCells use this
    as the budget and defer the rest to the next HF; first cycle (no previous) is capped
    to half the pool so the second cycle has room too."""
    boundary = SFrepPrevCycleStart
    if boundary is None:
        if SFrepCycleStart is None:
            return cfg.LOPOS_LAST_USABLE_SF - SFrepIdxRef
        return max(0, (cfg.LOPOS_LAST_USABLE_SF - cfg.LOPOS_FIRST_REPEAT_SF) // 2
                      - _repPoolFwdDist(SFrepCycleStart, SFrepIdxRef))
    return _repPoolFwdDist(SFrepIdxRef, boundary)

def initSFrepIdxRef():
    """Moving TDoA window: do NOT reset to the pool start each HF -- continue from the
    last slot the previous HF used, so the scenario blocks slide through the repeating
    pool over time. A device acting on the previous HF's provisioning then hits silent
    SFs instead of a live frame (kills the one-HF-late stale-sync race). Rotation back
    to LOPOS_FIRST_REPEAT_SF+1 happens in claimRepeatingAndfixedSF."""
    global SFrepIdxRef, SFrepWrapped, SFrepCycleStart, SFrepPrevCycleStart
    SFrepPrevCycleStart = SFrepCycleStart
    SFrepWrapped = False
    SFrepCycleStart = None
    SFrepIdxRef = claimRepeatingAndfixedSF(SFrepIdxRef)   # first run: 0 -> pool start (90)
    SFrepCycleStart = SFrepIdxRef
    return SFrepIdxRef

def getNextSFrepIdxRef(inter_sf = 1, allowed_ofs=None):
    global SFrepIdxRef 
    if allowed_ofs is None:
        allowed_ofs = [0,1,2,3,4,5,6,7]
    while True:
        SFrepIdxCurr = SFrepIdxRef
        SFrepIdxRef = claimRepeatingAndfixedSF(SFrepIdxCurr+inter_sf)
        blockOfs = SFrepIdxCurr % cfg.LOPOS_SF_BLOCK_SIZE
        if blockOfs in allowed_ofs: 
            break
    return SFrepIdxCurr

