import mysql.connector, localConfig, json
cn = mysql.connector.connect(**localConfig.mysql); c = cn.cursor()
c.execute("SELECT NOW()"); now = c.fetchone()[0]

CUR_START = "2026-06-10 11:00:00"   # just after the 13-cell deploy (~10:39) settled
c.execute("SELECT TIMESTAMPDIFF(MINUTE, %s, NOW())", (CUR_START,))
dur = c.fetchone()[0]
BASE_START = "2026-05-30 11:00:00"
c.execute("SELECT DATE_ADD(%s, INTERVAL %s MINUTE)", (BASE_START, dur))
base_end = c.fetchone()[0]

def stats(tbl, start, end):
    c.execute("SELECT t.`group` g, COUNT(*) f, COUNT(DISTINCT p.addr) n "
              "FROM " + tbl + " p JOIN tag t ON t.addr=p.addr "
              "WHERE (p.addr&0xF000)=0x1000 AND IFNULL(p.numHyperbola,0)>=3 "
              "AND p.updated>=%s AND p.updated<%s GROUP BY t.`group` ORDER BY t.`group`",
              (start, end))
    return {g: (f, n) for g, f, n in c.fetchall()}

cur = stats("position", CUR_START, now)
base = stats("position_26_06_02", BASE_START, base_end)
out = {"now": str(now), "dur_min": dur, "cur_window": [CUR_START, str(now)],
       "base_window": [BASE_START, str(base_end)], "groups": {}}
for g in sorted(set(cur) | set(base)):
    fb, nb = base.get(g, (0, 1)); fa, na = cur.get(g, (0, 1))
    out["groups"][g] = dict(base_fixes=fb, base_tags=nb, base_ptag=round(fb/dur*60/max(nb,1)/60*60, 3) if dur else 0,
                            cur_fixes=fa, cur_tags=na)
    # ptag/min = fixes / minutes / tags
    out["groups"][g]["base_ptag"] = round(fb/dur/max(nb,1), 3)
    out["groups"][g]["cur_ptag"] = round(fa/dur/max(na,1), 3)
print(json.dumps(out, indent=2))
