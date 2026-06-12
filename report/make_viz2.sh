#!/bin/bash
# Render overall-used.png for BEFORE (20-core layout live through May 30; cell_bak_20260604_131225 +
# anchor groups from anchor_bak_20260604_131225) and AFTER (current live 13-core layout).
set -e
cd /home/lopos/install

sudo -u lopos python3 - <<'PYEOF'
import os, mysql.connector, localConfig
cn = mysql.connector.connect(**localConfig.mysql); c = cn.cursor()
A = "0xA000"
def dump(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join("NA" if v is None else str(v) for v in r) + "\n")
def q(sql):
    c.execute(sql); return c.fetchall()

# group_src = table with (id, `group`); cell_t = cell definition table. Positions always current.
for state, group_src, cell_t in (
        ("/tmp/vb", "anchor_bak_20260604_131225", "cell_bak_20260604_131225"),
        ("/tmp/va", "anchor",                     "cell")):
    dump(f"{state}/anchors.tsv", ["id", "group_bitmask", "x", "y"],
         q(f"SELECT a.id, g.`group`, ROUND(AVG(p.x)), ROUND(AVG(p.y)) "
           f"FROM anchor a JOIN {group_src} g ON g.id=a.id "
           f"LEFT JOIN position p ON p.addr=a.addr AND IFNULL(p.numHyperbola,0)=0 "
           f"GROUP BY a.id, g.`group` ORDER BY a.id"))
    dump(f"{state}/cells.tsv", ["core", "edge"], q(f"SELECT core, edge FROM {cell_t} ORDER BY core, edge"))
    dump(f"{state}/map.tsv", ["mapcol", "x1", "y1", "x2", "y2"], q("SELECT mapcol, x1, y1, x2, y2 FROM map"))
    dump(f"{state}/br.tsv", ["anchorId", "beaconRatio"],
         q(f"SELECT addr-{A}, ROUND(AVG(beaconRatio)) FROM stat WHERE (addr & 0xF000)={A} AND updated>=CURDATE() GROUP BY addr"))
    dump(f"{state}/linkcounts.tsv", ["txAnchorId", "rxAnchorId", "received"], [])
    dump(f"{state}/expected.tsv", ["txAnchorId", "rxAnchorId", "rounds"], [])
print("TSVs written")
PYEOF

sudo -u lopos env VIZ_DATA_DIR=/tmp/vb VIZ_OUT_DIR=/tmp/vb/out VIZ_LABEL="Cell layout to 30 May" python3 vizCells.py >/dev/null
sudo -u lopos env VIZ_DATA_DIR=/tmp/va VIZ_OUT_DIR=/tmp/va/out VIZ_LABEL="Cell layout now" python3 vizCells.py >/dev/null
ls -la /tmp/vb/out/overall-used.png /tmp/va/out/overall-used.png
