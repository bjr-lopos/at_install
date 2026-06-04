#!/usr/bin/env python3
"""proactiveEval.py - snapshot TDoA fix rate per group, to evaluate proactive cell selection.

A "fix" = a position row with numHyperbola >= 3 (a successful TDoA localization). For each tag
group we report fixes, distinct tags, fixes/min and per-tag/min over the last N minutes, and tag
the group as 'proactive' or 'round-robin' from localConfig (cfg.tdoaProactiveCell +
cfg.LOPOS_TDOA_PROACTIVE_GROUPS). grp1/2 (round-robin) act as a control to cancel global drift.

Usage:  python3 proactiveEval.py [minutes=30] [csv=/home/lopos/proactive_eval.csv]
Prints a table and appends one CSV row per group (header written once). Meant to be run manually
or from cron (see CLAUDE.md 'Resume / proactive cell selection') so evaluation data accumulates
even when the dev PC is off. Read-only on the DB; only writes the CSV log.
"""
import sys, os, datetime, mysql.connector
sys.path.insert(0, "/usr/local/bin")          # the live localConfig (symlinked to the repo copy)
import localConfig as cfg

win = int(sys.argv[1]) if len(sys.argv) > 1 else 30
csv_path = sys.argv[2] if len(sys.argv) > 2 else "/home/lopos/proactive_eval.csv"

proactive_on = hasattr(cfg, "tdoaProactiveCell")
pg = getattr(cfg, "LOPOS_TDOA_PROACTIVE_GROUPS", None)   # None => all groups when proactive_on
def mode_of(grp):
    if not proactive_on:
        return "round-robin"
    return "proactive" if (pg is None or grp in pg) else "round-robin"

m = cfg.mysql
con = mysql.connector.connect(host=m["host"], user=m["user"], passwd=m["passwd"], db=m["db"])
cur = con.cursor()
cur.execute("SELECT NOW()")
now = cur.fetchone()[0]
cur.execute("""SELECT t.`group` grp, COUNT(*) fixes, COUNT(DISTINCT p.addr) tags
               FROM position p JOIN tag t ON t.addr=p.addr
               WHERE (p.addr & 0xF000)=0x1000 AND IFNULL(p.numHyperbola,0)>=3
                 AND p.updated >= NOW() - INTERVAL %s MINUTE
               GROUP BY t.`group` ORDER BY t.`group`""", (win,))
rows = cur.fetchall()
cur.close(); con.close()

print(f"# proactiveEval @ {now}  window={win}min  proactive_on={proactive_on}  groups={pg}")
print("  grp  mode         fixes  tags  fix/min  pertag/min")
new_file = not os.path.exists(csv_path)
with open(csv_path, "a") as f:
    if new_file:
        f.write("ts,window_min,grp,mode,fixes,tags,fixes_per_min,pertag_per_min\n")
    for grp, fixes, tags in rows:
        fpm = fixes / win
        ptm = fpm / tags if tags else 0.0
        md = mode_of(grp)
        print(f"   {grp:>2}  {md:<11} {fixes:>6} {tags:>5}   {fpm:>6.1f}    {ptm:>6.2f}")
        f.write(f"{now},{win},{grp},{md},{fixes},{tags},{fpm:.3f},{ptm:.4f}\n")
