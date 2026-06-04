#!/usr/bin/env python3
"""Dump the TSVs that vizCells.py / curateCells.py read, straight from the live DB.

Run ON THE GATEWAY (needs loposPyLib + localConfig). Writes to --out (default /tmp/lopos_viz):
  anchors.tsv    : id  group_bitmask  x  y          (x/y 'NA' if no self-position)
  cells.tsv      : core  edge                        (current cell table)
  linkcounts.tsv : txAnchorId  rxAnchorId  received  (anchor->anchor uwbstat rows)
  expected.tsv   : txAnchorId  rxAnchorId  rounds     (asns where tx sent AND rx was listening)
  br.tsv         : anchorId  beaconRatio             (avg over the window)
  map.tsv        : mapcol  x1 y1 x2 y2

The uwbstat-derived TSVs (linkcounts/expected/br) are filtered to `updated >= --since`, so a
fresh broad scan's data is not mixed with stale pre-scan rows. Default --since = 60 min ago.
"""
import os, sys, argparse
import mysql.connector
import localConfig as cfg

A_BASE = 0xA000     # anchor dev address base (dev = 0xA000 + anchorId)
A_MASK = 0xF000


def dump(cur, path, header, sql, params=()):
    cur.execute(sql, params)
    rows = cur.fetchall()
    with open(path, "w") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join("NA" if v is None else str(v) for v in r) + "\n")
    print(f"  {os.path.basename(path):16s} {len(rows):5d} rows")
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/lopos_viz")
    ap.add_argument("--since", default=None,
                    help="uwbstat cutoff 'YYYY-MM-DD HH:MM:SS' (default: 60 min ago)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    m = cfg.mysql
    con = mysql.connector.connect(host=m["host"], user=m["user"], passwd=m["passwd"],
                                  db=m["db"], autocommit=True)
    cur = con.cursor()
    if args.since:
        since = args.since
    else:
        cur.execute("SELECT NOW() - INTERVAL 60 MINUTE"); since = cur.fetchone()[0]
    print(f"fetching to {args.out} (uwbstat since {since})")

    dump(cur, os.path.join(args.out, "anchors.tsv"),
         ["id", "group_bitmask", "x", "y"],
         "SELECT a.id, a.`group`, ROUND(AVG(p.x)), ROUND(AVG(p.y)) FROM anchor a "
         "LEFT JOIN position p ON p.addr=a.addr AND IFNULL(p.numHyperbola,0)=0 "
         "GROUP BY a.id, a.`group` ORDER BY a.id")

    dump(cur, os.path.join(args.out, "cells.tsv"), ["core", "edge"],
         "SELECT core, edge FROM cell ORDER BY core, edge")

    dump(cur, os.path.join(args.out, "linkcounts.tsv"),
         ["txAnchorId", "rxAnchorId", "received"],
         "SELECT devTx-%s, devRx-%s, COUNT(*) FROM uwbstat "
         "WHERE (devTx & %s)=%s AND (devRx & %s)=%s AND updated >= %s "
         "GROUP BY devTx, devRx", (A_BASE, A_BASE, A_MASK, A_BASE, A_MASK, A_BASE, since))

    # per-PAIR expected: asns where tx transmitted AND rx was listening (rx heard >=1 anchor that
    # asn => it was awake). ratio received/expected is then the true core->edge link quality,
    # not diluted by rounds where the edge was not part of the receiver set.
    dump(cur, os.path.join(args.out, "expected.tsv"), ["txAnchorId", "rxAnchorId", "rounds"],
         "SELECT t.devTx-%s, r.devRx-%s, COUNT(*) FROM "
         "(SELECT DISTINCT asn, devTx FROM uwbstat WHERE (devTx & %s)=%s AND updated >= %s) t "
         "JOIN (SELECT DISTINCT asn, devRx FROM uwbstat WHERE (devRx & %s)=%s AND updated >= %s) r "
         "ON t.asn=r.asn AND t.devTx<>r.devRx GROUP BY t.devTx, r.devRx",
         (A_BASE, A_BASE, A_MASK, A_BASE, since, A_MASK, A_BASE, since))

    dump(cur, os.path.join(args.out, "br.tsv"), ["anchorId", "beaconRatio"],
         "SELECT addr-%s, ROUND(AVG(beaconRatio)) FROM stat "
         "WHERE (addr & %s)=%s AND updated >= %s GROUP BY addr",
         (A_BASE, A_MASK, A_BASE, since))

    dump(cur, os.path.join(args.out, "map.tsv"), ["mapcol", "x1", "y1", "x2", "y2"],
         "SELECT mapcol, x1, y1, x2, y2 FROM map")

    # meta.tsv: one row describing the uwbstat dataset actually fetched (anchor->anchor rows that
    # passed the --since filter) -- start/end time, row count, distinct tx/rx anchors, ordered pairs.
    # vizCells.py renders this in the figure caption so the image states which dataset it shows.
    dump(cur, os.path.join(args.out, "meta.tsv"),
         ["since", "min_updated", "max_updated", "rows", "tx_anchors", "rx_anchors", "pairs"],
         "SELECT %s, MIN(updated), MAX(updated), COUNT(*), "
         "COUNT(DISTINCT devTx), COUNT(DISTINCT devRx), COUNT(DISTINCT devTx, devRx) "
         "FROM uwbstat WHERE (devTx & %s)=%s AND (devRx & %s)=%s AND updated >= %s",
         (str(since), A_MASK, A_BASE, A_MASK, A_BASE, since))

    cur.close(); con.close()
    print("done.")


if __name__ == "__main__":
    main()
