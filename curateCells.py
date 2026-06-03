#!/usr/bin/env python3
"""
curateCells.py - re-derive the TDoA cell table from MEASURED uwb reception + geometry.

Reads the same TSV snapshot vizCells.py uses (see fetch block at bottom of the plan):
  anchors.tsv : id  group_bitmask  x  y        (x/y 'NA' if no self-position)
  cells.tsv   : core  edge                     (current cells)
  linkcounts.tsv : txAnchorId  rxAnchorId  receivedCount
  expected.tsv   : txAnchorId  scanRounds       (distinct asn the tx ran)
  br.tsv      : anchorId  beaconRatio
  map.tsv     : mapcol  x1 y1 x2 y2

Link quality = RECEPTION COUNT, not RSSI:  ratio(core->edge) = received / expected(core).
A link is "good" when ratio >= RECV_GOOD.

Modes:
  refine (default) - start from current cells; keep/prune edges by reception, drop cores
                     that no longer qualify. Minimal change (maintenance, e.g. anchor went silent).
  build            - bottom-up: for each candidate core, take location-neighbours within R,
                     keep the well-received non-collinear ones, then greedily cover the field.
                     NOTE: only links present in uwbstat can be judged; a fresh BROAD scan
                     (candidate links configured + scanned) is required for a true rebuild.

Output (dry-run): proposed cells, a diff vs current, per-cell metrics, and SQL to apply
(+ backup SQL). It does NOT write the DB; you review and apply.

Criteria, in priority order (see plan):
  1. good+tight cell : core has >= MIN_EDGES well-received, non-collinear edges (>=3 anchors)
  2. coverage        : cells cover the used-anchor extent
  3. non-overlapping : avoid cells claiming the same ground
  4. fewer cells     : <= ~2 per group (lowest priority)
Structural: a core is unique (one cell); edges may be reused and may sit in an adjacent group.
Group bitmask (grp1=1,grp2=2,grp3=4,grp4=8) is derived from the map vertical borders.
"""
import os, csv, math, argparse, datetime

DATA_DIR = os.environ.get("CURATE_DATA_DIR", "/tmp/lopos_viz")
OUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "curate_out")

# --- tunables ---
RECV_GOOD   = 0.75     # received/expected to call a core->edge link good (~>= 12 of 16 scan rounds)
MIN_EDGES   = 2        # >=2 edges => >=3 anchors/cell (min for a 2D TDoA fix)
MIN_2DRATIO = 0.20     # reject (near-)collinear edge sets
BR_MIN_CORE = 85       # a core must transmit reliably (Beacon Ratio)
RADIUS      = 1900     # build-mode: candidate edge within this distance of the core (coord units)
BORDER_MARGIN = 500    # core within this of a fence => the cell serves BOTH adjacent groups
COVER_NX, COVER_NY = 40, 25   # coverage sampling grid over the used-anchor extent
HULL_AREA_INFLATE = 1.20            # cell footprint = convex hull of the cell's anchors, surface +20%
HULL_INFLATE = HULL_AREA_INFLATE ** 0.5   # linear scale about the hull centroid giving that area
BALANCE_MAX = 0.40     # (balance criterion currently disabled; kept for later) core off-centre limit

# confirmed vertical map borders (x). grp1|grp2 and grp3|grp4 from inner_fence_*, cluster split = corridor.
BORDER_G1G2 = -2335
CLUSTER_LO  = -280     # central fenced corridor (grp2 | grp3 cluster split)
CLUSTER_HI  =  300
BORDER_G3G4 =  2429
GROUP_BIT = {"grp1": 1, "grp2": 2, "grp3": 4, "grp4": 8}


def load(name):
    rows = []
    with open(os.path.join(DATA_DIR, name)) as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if i == 0 or not line:
                continue                # skip the header row (and blanks)
            rows.append(line.split("\t"))
    return rows


def load_data():
    coords, grp = {}, {}
    for r in load("anchors.tsv"):
        aid = int(r[0]); grp[aid] = int(r[1])
        coords[aid] = None if (r[2] == "NA" or r[3] == "NA") else (float(r[2]), float(r[3]))
    cells = {}
    for r in load("cells.tsv"):
        cells.setdefault(int(r[0]), []).append(int(r[1]))
    recv = {(int(r[0]), int(r[1])): int(r[2]) for r in load("linkcounts.tsv")}
    expected = {(int(r[0]), int(r[1])): int(r[2]) for r in load("expected.tsv")}   # per (tx,rx) pair
    br = {int(r[0]): float(r[1]) for r in load("br.tsv")}
    return coords, grp, cells, recv, expected, br


def group_of_x(x):
    if x < BORDER_G1G2: return "grp1"
    if x < CLUSTER_LO:  return "grp2"
    if x <= CLUSTER_HI: return None          # in the corridor between clusters
    if x < BORDER_G3G4: return "grp3"
    return "grp4"


def convex_hull(pts):
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


def point_in_poly(x, y, poly):
    inside = False; n = len(poly); j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


class Curator:
    def __init__(self, coords, grp, cells, recv, expected, br):
        self.coords, self.grp, self.cells = coords, grp, cells
        self.recv, self.expected, self.br = recv, expected, br
        self.coverage_pct = None

    def ratio(self, core, edge):
        exp = self.expected.get((core, edge), 0)        # rounds where core sent AND edge listened
        return (self.recv.get((core, edge), 0) / exp) if exp else None

    def good(self, core, edge):
        r = self.ratio(core, edge)
        return r is not None and r >= RECV_GOOD

    def two_d_ratio(self, core, edges):
        pts = [self.coords[core]] + [self.coords[e] for e in edges if self.coords.get(e)]
        pts = [p for p in pts if p]
        n = len(pts)
        if n < 3: return 0.0
        mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
        sxx = sum((p[0]-mx)**2 for p in pts)/n; syy = sum((p[1]-my)**2 for p in pts)/n
        sxy = sum((p[0]-mx)*(p[1]-my) for p in pts)/n
        t = sxx+syy; d = sxx*syy-sxy*sxy; disc = max(t*t/4-d, 0)**0.5
        l1 = t/2+disc; l2 = t/2-disc
        return (l2/l1)**0.5 if l1 > 0 else 0.0

    def neighbours(self, core):
        c = self.coords.get(core)
        if not c: return []
        out = []
        for e, ec in self.coords.items():
            if e == core or not ec: continue
            if (ec[0]-c[0])**2 + (ec[1]-c[1])**2 <= RADIUS*RADIUS:
                out.append(e)
        return out

    def balance_offset(self, core, edges):
        """How off-centre the core is within the cell rectangle, as a fraction of half-size
        (0 = core at the rectangle centre of gravity, ->1 = core at the rectangle edge)."""
        pts = [self.coords[a] for a in [core] + edges if self.coords.get(a)]
        if len(pts) < 2:
            return 0.0
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        cx = (min(xs)+max(xs))/2; cy = (min(ys)+max(ys))/2
        hw = max((max(xs)-min(xs))/2, 1.0); hh = max((max(ys)-min(ys))/2, 1.0)
        px, py = self.coords[core]
        return max(abs(px-cx)/hw, abs(py-cy)/hh)

    def rebalance(self, core, edges):
        """Re-centre the core by dropping the most off-centre edge while unbalanced
        (e.g. core-8's anchor 1), keeping >= MIN_EDGES."""
        edges = list(edges)
        while len(edges) > MIN_EDGES and self.balance_offset(core, edges) > BALANCE_MAX:
            cand = min(edges, key=lambda e: self.balance_offset(core, [x for x in edges if x != e]))
            if self.balance_offset(core, [x for x in edges if x != cand]) >= self.balance_offset(core, edges):
                break   # removing nothing improves it
            edges.remove(cand)
        return sorted(edges)

    def qualify(self, core, candidate_edges):
        """Return (kept_edges, reason|None). None reason == cell accepted."""
        if not self.coords.get(core):
            return [], "core has no position"
        if self.br.get(core, 0) < BR_MIN_CORE:
            return [], f"core BR {self.br.get(core,0):.0f} < {BR_MIN_CORE}"
        edges = sorted({e for e in candidate_edges
                        if e != core and self.coords.get(e) and self.good(core, e)})
        if len(edges) < MIN_EDGES:
            return edges, f"only {len(edges)} well-received edge(s) (<{MIN_EDGES})"
        # balance criterion disabled for now (evaluate raw results first)
        r2 = self.two_d_ratio(core, edges)
        if r2 < MIN_2DRATIO:
            return edges, f"edges (near-)collinear 2Dratio={r2:.2f}"
        return edges, None

    def curate(self, mode):
        proposed, dropped = {}, {}
        if mode == "refine":
            candidate_cores = list(self.cells.keys())
            cand_edges = lambda c: self.cells.get(c, [])
        else:  # build
            candidate_cores = sorted(self.coords.keys())
            cand_edges = self.neighbours
        for core in candidate_cores:
            edges, reason = self.qualify(core, cand_edges(core))
            if reason: dropped[core] = (reason, edges)
            else:      proposed[core] = edges
        if mode == "build":
            proposed = self.coverage_select(proposed)
        return proposed, dropped

    def footprint(self, core, edges):
        """Coverage POLYGON = convex hull of the cell's anchors, surface inflated HULL_AREA_INFLATE
        (scaled about the hull centroid). Same model as vizCells, so coverage % is comparable."""
        pts = [self.coords[a] for a in [core] + edges if self.coords.get(a)]
        if len(pts) < 3:
            return None
        hull = convex_hull(pts)
        if len(hull) < 3:
            return None
        cx = sum(p[0] for p in hull)/len(hull); cy = sum(p[1] for p in hull)/len(hull)
        return [(cx + (x-cx)*HULL_INFLATE, cy + (y-cy)*HULL_INFLATE) for x, y in hull]

    def coverage_select(self, cells):
        """Greedy set-cover over cell POLYGONS (convex hull +20% surface, like vizCells): keep the
        FEWEST valid cells whose polygons cover the coverable area (bbox of all hull points).
        Greedily picking max NEW coverage also minimises overlap. Cores stay unique.
        Sets self.coverage_pct = union(polys) / coverable area (matches vizCells.coverage_pct)."""
        polys = {c: self.footprint(c, cells[c]) for c in cells}
        polys = {c: p for c, p in polys.items() if p}
        if not polys:
            self.coverage_pct = 0.0; return cells
        allpts = [pt for p in polys.values() for pt in p]
        minx = min(x for x, _ in allpts); maxx = max(x for x, _ in allpts)
        miny = min(y for _, y in allpts); maxy = max(y for _, y in allpts)
        grid = [(minx + (maxx-minx)*i/(COVER_NX-1), miny + (maxy-miny)*j/(COVER_NY-1))
                for i in range(COVER_NX) for j in range(COVER_NY)]
        covers = {c: set(k for k, (gx, gy) in enumerate(grid) if point_in_poly(gx, gy, polys[c]))
                  for c in polys}
        coverable = set().union(*covers.values()) if covers else set()
        self.coverage_pct = 100.0 * len(coverable) / len(grid) if grid else 0.0
        uncovered = set(coverable); kept = {}
        while uncovered:
            best = max(polys, key=lambda c: len(covers[c] & uncovered) if c not in kept else -1)
            if len(covers[best] & uncovered) == 0:
                break
            kept[best] = cells[best]; uncovered -= covers[best]
        return kept

    def bitmask(self, core, edges):
        """Core-band-centric: serve the core's band, plus an adjacent band only if the CORE sits
        within BORDER_MARGIN of that fence (a genuine border cell)."""
        c = self.coords.get(core)
        if not c:
            return 0
        x = c[0]; g = group_of_x(x)
        bits = GROUP_BIT[g] if g else 0
        if abs(x - BORDER_G1G2) <= BORDER_MARGIN:
            bits |= GROUP_BIT["grp1"] | GROUP_BIT["grp2"]
        if abs(x - BORDER_G3G4) <= BORDER_MARGIN:
            bits |= GROUP_BIT["grp3"] | GROUP_BIT["grp4"]
        if CLUSTER_LO - BORDER_MARGIN <= x <= CLUSTER_HI + BORDER_MARGIN:
            bits |= GROUP_BIT["grp2"] | GROUP_BIT["grp3"]     # near the central corridor
        if bits == 0:                                         # core inside corridor, no band
            bits = GROUP_BIT["grp2"] if x < 0 else GROUP_BIT["grp3"]
        return bits


def grp_label(bm):
    return "+".join(g for g, b in GROUP_BIT.items() if bm & b) or "none"


def build_scan_rounds(coords, radius, max_rx, max_tx=1):
    """ONE round per core (like uwbInfoAllCells): the core is the sole transmitter, its candidate
    edges (geometric neighbours within `radius`, nearest first, up to max_rx per round) are the
    receivers. So every candidate core->edge link gets EXACTLY ONE equal measurement opportunity
    per scan cycle -- unlike a multi-tx grid sweep, which co-occurs pairs an uneven 0/1/2 times
    per cycle and asymmetrically. A core with more than max_rx neighbours is split across several
    rounds (still its own transmitter). Only core->edge is measured (the direction that matters)."""
    rounds = []
    ids = [a for a in coords if coords.get(a)]
    r2 = radius * radius
    for core in sorted(ids):
        c = coords[core]
        edges = sorted((e for e in ids if e != core
                        and (coords[e][0]-c[0])**2 + (coords[e][1]-c[1])**2 <= r2),
                       key=lambda e: (coords[e][0]-c[0])**2 + (coords[e][1]-c[1])**2)
        for i in range(0, len(edges), max_rx):
            chunk = edges[i:i+max_rx]
            if chunk:
                rounds.append({"tx": [core], "rx": chunk})
    return rounds


def run_scan(scan_hfs, radius, batch):
    """GATEWAY ONLY. Drive a broad UWB scan over MQTT (topic 'loposcore/scan', a list of {tx,rx});
    the scheduler holds them in memory and planActions schedules them each hyperframe (HF-synced,
    free SFs), in parallel with localization. ONE round per core (core transmits, its candidate
    edges listen).

    We scan in BATCHES of `batch` rounds -- small enough that ALL of a batch fits one HF, so the
    scheduler runs the whole batch EVERY HF (no rotation), giving each (core,edge) pair ~one stat
    per HF == the dense coverage the legacy uwbInfoAllCells produced. Each batch is held for
    `scan_hfs` HFs (~640 s at scan_hfs=20) so every pair reaches ~scan_hfs stats, then the next
    batch. Re-fetch TSVs and run `--mode build`. Requires loposPyLib + localConfig + paho-mqtt."""
    import time, json
    import paho.mqtt.client as mqtt
    import mysql.connector
    import loposPyLib as loposPy
    import localConfig as cfg
    loposPy.initDB()
    rec = loposPy.wrappedSql(
        "SELECT a.id, ROUND(AVG(p.x)), ROUND(AVG(p.y)) FROM anchor a "
        "JOIN position p ON p.addr=a.addr AND IFNULL(p.numHyperbola,0)=0 GROUP BY a.id", {})
    coords = {int(r[0]): (float(r[1]), float(r[2])) for r in (rec or []) if r[1] is not None}
    max_rx = cfg.LOPOS_SCENARIO_UWB_TAG_OFS - 1         # up to 8 edge receivers per round
    rounds = build_scan_rounds(coords, radius, max_rx)
    batches = [rounds[i:i+batch] for i in range(0, len(rounds), batch)]
    cli = mqtt.Client(); cli.username_pw_set("lopos", "LoPoS")
    cli.connect("127.0.0.1", 1883, 60); cli.loop_start()
    # Dedicated autocommit connection for progress polling: loposPy's connection sits in InnoDB
    # REPEATABLE-READ and would keep seeing its first snapshot (always 0 new rows). autocommit
    # makes each COUNT its own transaction, so it sees rows the C core commits during the scan.
    mcon = mysql.connector.connect(host=cfg.mysql["host"], user=cfg.mysql["user"],
                                   passwd=cfg.mysql["passwd"], db=cfg.mysql["db"], autocommit=True)
    mcur = mcon.cursor()
    HF = 32
    print(f"{len(coords)} anchors -> {len(rounds)} per-core rounds, {len(batches)} batches of <= {batch} "
          f"(each fits one HF -> scheduled EVERY HF, like legacy), {scan_hfs} HF/batch (~{scan_hfs*HF//60} "
          f"min) -> ~{scan_hfs} stats/pair. Total ~{len(batches)*scan_hfs*HF//60} min. R={radius}.")
    try:
        for bi, br in enumerate(batches, 1):
            cli.publish("loposcore/scan", json.dumps(br), qos=1, retain=True)
            cores = [r["tx"][0] for r in br]
            print(f"=== batch {bi}/{len(batches)}: cores {cores} ===", flush=True)
            mcur.execute("SELECT NOW()"); t0 = mcur.fetchone()[0]
            last = 0
            for hf in range(1, scan_hfs + 1):
                time.sleep(HF)
                mcur.execute("SELECT COUNT(*) FROM uwbstat WHERE updated >= %s", (t0,))
                n = mcur.fetchone()[0]
                print(f"  HF {hf:>2}/{scan_hfs}: rows this batch = {n} (+{n-last})", flush=True)
                last = n
    finally:
        cli.publish("loposcore/scan", "[]", qos=1, retain=True)   # stop the scan
        time.sleep(1); cli.loop_stop(); cli.disconnect()
        mcur.close(); mcon.close()
    print("scan stopped (published empty list). Fresh broad uwbstat is in the DB.")
    print("Next: re-fetch TSVs, then run:  curateCells.py --mode build")


def main():
    global RECV_GOOD, DATA_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["refine", "build"], default="refine")
    ap.add_argument("--recv-good", type=float, default=RECV_GOOD)
    ap.add_argument("--data-dir", default=DATA_DIR)
    ap.add_argument("--scan", action="store_true",
                    help="GATEWAY: drive a broad UWB scan (batched per-core rounds over MQTT), then exit")
    ap.add_argument("--scan-hfs", type=int, default=20, help="hyperframes per batch (~32s each; 20 ~= 640s)")
    ap.add_argument("--batch", type=int, default=10, help="rounds per batch (must fit one HF so it runs every HF)")
    ap.add_argument("--radius", type=int, default=RADIUS, help="candidate edge max distance from core")
    args = ap.parse_args()
    if args.scan:
        run_scan(args.scan_hfs, args.radius, args.batch)
        return
    RECV_GOOD = args.recv_good; DATA_DIR = args.data_dir
    os.makedirs(OUT_DIR, exist_ok=True)

    coords, grp, cells, recv, expected, br = load_data()
    cur = Curator(coords, grp, cells, recv, expected, br)
    proposed, dropped = cur.curate(args.mode)

    # --- report ---
    print(f"== curateCells mode={args.mode} RECV_GOOD={RECV_GOOD} ==")
    print(f"current: {len(cells)} cores / {sum(len(v) for v in cells.values())} memberships")
    print(f"proposed: {len(proposed)} cores / {sum(len(v) for v in proposed.values())} memberships\n")

    print("PROPOSED CELLS:")
    rows = []
    for core in sorted(proposed):
        e = proposed[core]; bm = cur.bitmask(core, e)
        r2 = cur.two_d_ratio(core, e)
        ratios = " ".join(f"{x}:{cur.ratio(core,x):.0%}" for x in e)
        print(f"  core {core:>3}  groups={grp_label(bm):<11}(bm {bm:>2})  2Dratio={r2:.2f}  "
              f"edges[{len(e)}]: {ratios}")
        rows.append((core, bm, grp_label(bm), len(e), round(r2, 2), " ".join(map(str, e))))

    print("\nDROPPED / DEMOTED CORES (were cells, no longer qualify):")
    for core in sorted(dropped):
        reason, edges = dropped[core]
        print(f"  core {core:>3}  -> {reason}  (good edges: {edges})")

    # --- diff vs current ---
    cur_cores, new_cores = set(cells), set(proposed)
    print("\nDIFF vs current cell table:")
    print(f"  cores removed : {sorted(cur_cores - new_cores)}")
    print(f"  cores added   : {sorted(new_cores - cur_cores)}")
    changed = []
    for c in sorted(cur_cores & new_cores):
        if sorted(cells[c]) != sorted(proposed[c]):
            changed.append((c, sorted(set(cells[c]) - set(proposed[c])), sorted(set(proposed[c]) - set(cells[c]))))
    for c, rem, add in changed:
        print(f"  core {c}: edges -{rem} +{add}")

    # --- emit SQL (apply + backup) ---
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sqlpath = os.path.join(OUT_DIR, f"apply_cells_{ts}.sql")
    with open(sqlpath, "w") as f:
        f.write("-- curateCells proposed cell table; review before running.\n")
        f.write(f"CREATE TABLE IF NOT EXISTS cell_bak_{ts} AS SELECT * FROM cell;\n")
        f.write(f"CREATE TABLE IF NOT EXISTS anchor_bak_{ts} AS SELECT id,`group` FROM anchor;\n")
        f.write("START TRANSACTION;\n")
        f.write("DELETE FROM cell;\n")
        for core in sorted(proposed):
            for e in sorted(proposed[core]):
                f.write(f"INSERT INTO cell (core,edge) VALUES ({core},{e});\n")
        # reset all anchor.group bits we manage to 0, then set core bitmasks
        f.write("UPDATE anchor SET `group`=0;\n")
        for core in sorted(proposed):
            bm = cur.bitmask(core, proposed[core])
            f.write(f"UPDATE anchor SET `group`={bm} WHERE id={core};\n")
        f.write("COMMIT;\n")
    with open(os.path.join(OUT_DIR, f"proposed_cells_{ts}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["core", "bitmask", "groups", "n_edges", "2Dratio", "edges"]); w.writerows(rows)

    # group balance
    per_group = {g: 0 for g in GROUP_BIT}
    for core in proposed:
        for g, b in GROUP_BIT.items():
            if cur.bitmask(core, proposed[core]) & b: per_group[g] += 1
    print(f"\ncells per group (target ~2): {per_group}")
    if cur.coverage_pct is not None:
        print(f"field coverage by selected cells: {cur.coverage_pct:.0f}% of the used-anchor grid")
    print(f"\nwrote SQL  -> {sqlpath}")
    print(f"wrote CSV  -> {OUT_DIR}/proposed_cells_{ts}.csv")
    print("DRY-RUN: nothing applied. Review the SQL, ensure uwbstat is FRESH, apply on a test DB first.")


if __name__ == "__main__":
    main()
