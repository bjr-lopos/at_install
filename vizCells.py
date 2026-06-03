#!/usr/bin/env python3
"""
vizCells.py - render the CURRENT TDoA cell state to image files (read-only).

Reads TSVs produced from the live DB (see fetch block in the project plan):
  anchors.tsv : id  group_bitmask  x  y      (x/y = 'NA' if no self-position)
  cells.tsv   : core  edge
  uwb.tsv     : txAnchorId  rxAnchorId  rxPow  n
  br.tsv      : anchorId  beaconRatio
  map.tsv     : mapcol  x1 y1 x2 y2

Outputs (PNG) into OUT_DIR:
  cell_core<ID>.png   - one per cell: full map + all anchors, this cell highlighted
  group<g>.png        - one per group: full map + all anchors, all cells of that group
  overall.png         - all cells
Plus cells_summary.csv.

Every image draws the COMPLETE map table and ALL anchors, each labelled with its id;
the core anchor of a cell is marked distinctly.
"""
import os, csv, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch, Polygon

DATA_DIR = "/tmp/lopos_viz"
OUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "viz")
os.makedirs(OUT_DIR, exist_ok=True)

# group bit -> label
GROUP_BITS = [(1, "grp1"), (2, "grp2"), (4, "grp3"), (8, "grp4")]
# confirmed vertical borders from the map table
BORDERS = [(-2335, "grp1|grp2"), (2429, "grp3|grp4"), (-280, "cluster"), (300, "cluster")]
RECV_GOOD = 0.80   # a link must deliver >= this fraction of its expected stats to count as "good"

def load(name):
    p = os.path.join(DATA_DIR, name)
    rows = []
    with open(p) as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if i == 0 or not line:
                continue                # skip the header row (and blanks)
            rows.append(line.split("\t"))
    return rows

# ---- load data ----
anchors = {}            # id -> dict(grp, x, y)
no_coord = []
for r in load("anchors.tsv"):
    aid = int(r[0]); grp = int(r[1])
    if r[2] == "NA" or r[3] == "NA":
        anchors[aid] = dict(grp=grp, x=None, y=None); no_coord.append(aid)
    else:
        anchors[aid] = dict(grp=grp, x=float(r[2]), y=float(r[3]))

cells = {}              # core -> [edges]
for r in load("cells.tsv"):
    core, edge = int(r[0]), int(r[1])
    cells.setdefault(core, []).append(edge)

recv = {}               # (tx,rx) -> count of UWB stats received (tx transmits, rx listens)
for r in load("linkcounts.tsv"):
    recv[(int(r[0]), int(r[1]))] = int(r[2])
expected = {}           # (tx,rx) -> asns where tx transmitted AND rx was listening
for r in load("expected.tsv"):
    expected[(int(r[0]), int(r[1]))] = int(r[2])

br = {}
for r in load("br.tsv"):
    br[int(r[0])] = float(r[1])

mapsegs = []
for r in load("map.tsv"):
    try:
        mapsegs.append((r[0], float(r[1]), float(r[2]), float(r[3]), float(r[4])))
    except ValueError:
        pass

# uwbstat freshness (from meta.tsv: min, max, total, last10min)
mr = load("meta.tsv")
uwb_min = uwb_max = "?"; uwb_total = uwb_recent = 0
if mr:
    uwb_min, uwb_max, uwb_total, uwb_recent = mr[0][0], mr[0][1], int(mr[0][2]), int(mr[0][3] or 0)
STALE = "  [STALE: no live UWB scan running]" if uwb_recent == 0 else ""
_used_anchors = set(cells.keys()) | {e for es in cells.values() for e in es}
nc_used = sorted(a for a in no_coord if a in _used_anchors)
nc_unused = sorted(a for a in no_coord if a not in _used_anchors)
# coverage extent = bounding box over USED anchors (cores+edges) that have coords
_uw = [(anchors[a]["x"], anchors[a]["y"]) for a in _used_anchors
       if anchors.get(a) and anchors[a]["x"] is not None]
COVER_BBOX = (min(x for x, _ in _uw), max(x for x, _ in _uw),
              min(y for _, y in _uw), max(y for _, y in _uw)) if _uw else None
CAPTION = (f"Link quality = UWB stats RECEIVED / EXPECTED rounds (count, NOT rssi) from uwbstat over "
           f"{uwb_min} .. {uwb_max} ({uwb_total} pairs, {uwb_recent} in last 10 min){STALE}.   "
           f"Line colour = core->edge reception (the only direction that matters); label = recv/expected + symmetry (= both dirs good, -> fwd-only, <- rev-only).\n"
           f"Anchors without a self-position (not plotted): USED in cells (relevant): {nc_used or 'none'}  |  unused: {nc_unused or 'none'}.")

LEGEND_HANDLES = [
    Line2D([], [], marker="*", color="w", markerfacecolor="0.6", markeredgecolor="black", markersize=15, label="cell core (star; fill=BR colour; ring outlines the cell)"),
    Line2D([], [], marker="s", color="w", markerfacecolor="0.6", markeredgecolor="black", markersize=9, label="core anchor (square; fill=BR colour)"),
    Line2D([], [], marker="o", color="w", markerfacecolor="0.6", markeredgecolor="black", markersize=7, label="edge / other anchor (circle; fill=BR colour)"),
    Line2D([], [], color="purple", lw=1.3, ls="--", label="coverage extent (used-anchor bbox)"),
    Patch(facecolor="0.6", alpha=0.25, edgecolor="0.5", linestyle="--", label="cell coverage (convex hull +20% surface)"),
    Line2D([], [], color="#1f77b4", lw=1, ls="--", label="group border (map)"),
    Line2D([], [], color="#2ca02c", lw=2, ls="-",  label=f"core->edge good (>= {int(RECV_GOOD*100)}% received)"),
    Line2D([], [], color="#ff7f0e", lw=2, ls="--", label=f"core->edge weak (< {int(RECV_GOOD*100)}%)"),
    Line2D([], [], color="#d62728", lw=2, ls=":",  label="core->edge no stats received"),
    Line2D([], [], color="0.5",     lw=2, ls=":",  label="core did not transmit (cannot judge)"),
    Line2D([], [], marker="o", color="w", markerfacecolor="#2ca02c", markersize=9, label="anchor BR >= 95 (good)"),
    Line2D([], [], marker="o", color="w", markerfacecolor="#ff7f0e", markersize=9, label="anchor BR 85-94"),
    Line2D([], [], marker="o", color="w", markerfacecolor="#d62728", markersize=9, label="anchor BR < 85 (low; misses provisioning)"),
    Line2D([], [], marker="o", color="w", markerfacecolor="0.6", markersize=9, label="anchor BR unknown"),
]

def link_recv(core, edge):
    """Reception quality core->edge: (received_count, expected_rounds, ratio).
    ratio is None when the core never transmitted in the period (cannot judge)."""
    r = recv.get((core, edge), 0)
    exp = expected.get((core, edge), 0)      # rounds where core sent AND edge listened
    return r, exp, (r / exp if exp else None)

def coords(aid):
    a = anchors.get(aid)
    if a and a["x"] is not None:
        return (a["x"], a["y"])
    return None

def two_d_ratio(core, edges):
    pts = [coords(core)] + [coords(e) for e in edges]
    pts = [p for p in pts if p]
    n = len(pts)
    if n < 3:
        return 0.0
    mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    sxx = sum((p[0]-mx)**2 for p in pts) / n
    syy = sum((p[1]-my)**2 for p in pts) / n
    sxy = sum((p[0]-mx)*(p[1]-my) for p in pts) / n
    t = sxx + syy; d = sxx*syy - sxy*sxy
    disc = max(t*t/4 - d, 0) ** 0.5
    l1 = t/2 + disc; l2 = t/2 - disc
    return (l2/l1) ** 0.5 if l1 > 0 else 0.0

CORE_SET = set(cells.keys())

HULL_AREA_INFLATE = 1.20            # cell coverage region = convex hull of anchors, surface +20%
HULL_INFLATE = HULL_AREA_INFLATE ** 0.5   # linear scale about the hull centroid giving that area

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

def cell_hull(core, edges):
    """Coverage polygon of a cell = convex hull of its anchors, surface inflated HULL_AREA_INFLATE
    (scaled about the hull centroid)."""
    pts = [coords(a) for a in [core] + edges if coords(a)]
    pts = [p for p in pts if p]
    if len(pts) < 3:
        return None
    hull = convex_hull(pts)
    if len(hull) < 3:
        return None
    cx = sum(p[0] for p in hull)/len(hull); cy = sum(p[1] for p in hull)/len(hull)
    return [(cx + (x-cx)*HULL_INFLATE, cy + (y-cy)*HULL_INFLATE) for x, y in hull]

def coverage_pct(cell_map):
    """Total coverage = union of cell hulls, as % of the coverable area
    (the bounding box of all those hull points). Sampled on a fine grid."""
    polys = [p for p in (cell_hull(c, cell_map[c]) for c in cell_map) if p]
    if not polys:
        return 0.0
    allpts = [pt for p in polys for pt in p]
    minx = min(x for x, _ in allpts); maxx = max(x for x, _ in allpts)
    miny = min(y for _, y in allpts); maxy = max(y for _, y in allpts)
    NX, NY = 140, 90; inside = 0
    for i in range(NX):
        gx = minx + (maxx-minx)*i/(NX-1)
        for j in range(NY):
            gy = miny + (maxy-miny)*j/(NY-1)
            if any(point_in_poly(gx, gy, p) for p in polys):
                inside += 1
    return 100.0 * inside / (NX*NY)

def br_color(aid):
    v = br.get(aid)
    if v is None:
        return "0.6"
    if v >= 95: return "#2ca02c"
    if v >= 85: return "#ff7f0e"
    return "#d62728"

def draw_field(ax, title):
    # complete map table
    for label, x1, y1, x2, y2 in mapsegs:
        ax.plot([x1, x2], [y1, y2], color="0.80", lw=1.0, zorder=1)
    # group-border verticals
    for bx, lbl in BORDERS:
        ax.axvline(bx, color="#1f77b4", ls="--", lw=0.8, alpha=0.5, zorder=1)
    # coverage extent = bbox over USED anchors (not hardcoded corners)
    if COVER_BBOX:
        x0, x1, y0, y1 = COVER_BBOX
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                     edgecolor="purple", ls="--", lw=1.3, alpha=0.6, zorder=2))
    # all anchors, labelled
    for aid, a in anchors.items():
        if a["x"] is None:
            continue
        is_core = aid in CORE_SET
        ax.scatter(a["x"], a["y"], s=(70 if is_core else 28),
                   marker=("s" if is_core else "o"),
                   facecolor=br_color(aid), edgecolor="black",
                   linewidths=(1.2 if is_core else 0.5), zorder=4)
        ax.annotate(str(aid), (a["x"], a["y"]), textcoords="offset points",
                    xytext=(4, 4), fontsize=7, zorder=6)
    ax.set_aspect("equal"); ax.set_title(title, fontsize=11)
    ax.grid(True, ls=":", alpha=0.3)
    ax.legend(handles=LEGEND_HANDLES, loc="upper left", bbox_to_anchor=(1.01, 1.0),
              fontsize=7, framealpha=0.95, title="legend", title_fontsize=8)
    ax.figure.text(0.5, 0.005, CAPTION, ha="center", va="bottom", fontsize=7, color="0.25")

def draw_cell(ax, core, color, focal=False):
    cc = coords(core)
    if not cc:
        return
    hull = cell_hull(core, cells.get(core, []))    # coverage polygon (convex hull +20% surface)
    if hull:
        ax.add_patch(Polygon(hull, closed=True, facecolor=color,
                     alpha=0.08, edgecolor=color, ls="--", lw=1.0, zorder=2))
    for e in cells.get(core, []):
        ec = coords(e)
        if not ec:
            ax.annotate(f"{e}?nocoord", cc, fontsize=6, color="red")
            continue
        # decision/colour use ONLY core->edge (the direction that matters)
        rf, ef, ratf = link_recv(core, e)     # forward: core transmits -> edge receives
        rr, er, ratr = link_recv(e, core)     # reverse: edge -> core (symmetry only)
        fwd_ok = ratf is not None and ratf >= RECV_GOOD
        rev_ok = ratr is not None and ratr >= RECV_GOOD
        if ratf is None:
            lc, ls = "0.5", ":"          # core never transmitted -> cannot judge
        elif rf == 0:
            lc, ls = "#d62728", ":"      # no stats received core->edge
        elif fwd_ok:
            lc, ls = "#2ca02c", "-"      # good (quality, NOT cell colour)
        else:
            lc, ls = "#ff7f0e", "--"     # weak
        sym = "=" if (fwd_ok and rev_ok) else ("→" if fwd_ok else ("←" if rev_ok else "·"))
        ax.plot([cc[0], ec[0]], [cc[1], ec[1]], color=lc, ls=ls,
                lw=(2.0 if focal else 1.3), alpha=0.9, zorder=3)
        mx, my = (cc[0]+ec[0])/2, (cc[1]+ec[1])/2
        ax.annotate(f"{rf}/{ef}{sym}", (mx, my), fontsize=6, color=lc, zorder=7)
    # mark the core: star filled by Beacon-Ratio colour (like every anchor);
    # the ring highlights which cell -- black for the focus cell, cell colour in group views.
    ax.scatter(*cc, s=320, marker="*", facecolor=br_color(core), edgecolor="black",
               linewidths=1.2, zorder=8)
    ax.scatter(*cc, s=620, marker="o", facecolor="none",
               edgecolor=("black" if focal else color), linewidths=2.0, zorder=8)

GROUP_COLORS = ["#1f77b4", "#2ca02c", "#9467bd", "#8c564b", "#e377c2", "#17becf",
                "#bcbd22", "#ff7f0e", "#7f7f7f", "#aec7e8", "#98df8a"]

def fig_ax():
    fig, ax = plt.subplots(figsize=(15, 10))
    return fig, ax

def grp_label(bitmask):
    return "+".join(lbl for bit, lbl in GROUP_BITS if bitmask & bit) or "none"

# ---- one image per cell ----
summary = []
for ci, core in enumerate(sorted(cells)):
    fig, ax = fig_ax()
    bm = anchors.get(core, {}).get("grp", 0)
    r2 = two_d_ratio(core, cells[core])
    draw_field(ax, f"CURRENT cell core={core}  groups={grp_label(bm)} (bitmask {bm})  "
                   f"edges={cells[core]}")
    draw_cell(ax, core, "#d62728", focal=True)
    fig.savefig(os.path.join(OUT_DIR, f"cell_core{core:02d}.png"), dpi=110, bbox_inches="tight")
    plt.close(fig)
    summary.append((core, bm, grp_label(bm), len(cells[core]), round(r2, 2),
                    " ".join(str(e) for e in cells[core])))

# ---- one image per group (incl. ungrouped=0) ----
for bit, gl in GROUP_BITS + [(0, "ungrouped")]:
    members = [c for c in cells if (anchors.get(c, {}).get("grp", 0) & bit)
               or (bit == 0 and anchors.get(c, {}).get("grp", 0) == 0)]
    if not members:
        continue
    fig, ax = fig_ax()
    draw_field(ax, f"CURRENT {gl}: {len(members)} cells, cores={sorted(members)}")
    for i, core in enumerate(sorted(members)):
        draw_cell(ax, core, GROUP_COLORS[i % len(GROUP_COLORS)])
    fig.savefig(os.path.join(OUT_DIR, f"group_{gl}.png"), dpi=110, bbox_inches="tight")
    plt.close(fig)

# ---- overall ----
fig, ax = fig_ax()
draw_field(ax, f"CURRENT all cells: {len(cells)} cores / {len(anchors)} anchors  |  "
               f"coverage {coverage_pct(cells):.0f}% (union of cell hulls / coverable area)")
for i, core in enumerate(sorted(cells)):
    draw_cell(ax, core, GROUP_COLORS[i % len(GROUP_COLORS)])
fig.savefig(os.path.join(OUT_DIR, "overall.png"), dpi=120, bbox_inches="tight")
plt.close(fig)

with open(os.path.join(OUT_DIR, "cells_summary.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["core", "group_bitmask", "groups", "n_edges", "2Dratio", "edges"])
    w.writerows(summary)

print(f"wrote {len(cells)} cell images + {len(GROUP_BITS)+1} group images + overall to {OUT_DIR}")
if no_coord:
    print(f"NOTE: {len(no_coord)} anchors have no self-position (not plotted): {sorted(no_coord)}")
