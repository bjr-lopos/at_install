# LoPoS gateway tools

Scripts that run on a LoPoS gateway instance (e.g. `ilvo-gw`) alongside the
scheduler. The services execute the copies under `/usr/local/bin`
(`loposScheduler.py`, `loposPyLib.py`, `loposTDoA2Pos.py`, `loposcore`),
installed by `bootstrap.sh`; a `git pull` here does **not** update them — you
must `sudo cp` the changed files to `/usr/local/bin` and restart the services
(`loposcore`, `loposmath`/`lms`, `loposplan`).

This README documents the **cell-curation toolchain** added on top of the core
scheduler: it measures the real UWB connectivity between anchors and proposes a
clean set of TDoA *cells* (one core anchor + its well-received edge anchors).

---

## Background

TDoA localization groups anchors into **cells**: a *core* anchor plus *edge*
anchors. A tag is localized from the time-differences of arrival at the cell's
anchors, so a cell needs the core + ≥2 well-connected, non-collinear edges
(≥3 anchors) covering its area. The authoritative state is the `cell` table
(core,edge) plus `anchor.group` (a 4-bit bitmask: grp1=1, grp2=2, grp3=4,
grp4=8; a near-border cell may serve two adjacent groups, e.g. grp2+grp3 = 6).

Over time anchors drift, lose their self-position, or get a poor Beacon-Ratio,
so the hand-made cell table degrades. These tools re-derive it from **measured**
UWB reception instead of guesswork.

Key principle: **link quality is judged by reception COUNT, not RSSI.** Over a
scan we count, per ordered anchor pair, how often the receiver actually heard
the transmitter (`received`) versus how often it *could* have (`expected` =
rounds where the transmitter sent **and** the receiver was listening). A link is
"good" when `received/expected ≥ RECV_GOOD` (default 0.75).

---

## The three tools

### 1. `curateCells.py --scan` — drive a broad UWB scan (GATEWAY only)

Measures connectivity between **all anchors**, not just the currently-configured
cells. For each anchor it forms a *per-core round* — the core is the sole UWB
transmitter, its geometric neighbours within `RADIUS` (default 1900) are the
receivers — and publishes the rounds over MQTT topic `loposcore/scan`. The
scheduler (`uwbScanCells`, see below) holds them in memory and schedules them
every hyperframe in parallel with live localization, so each candidate
`core→edge` link gets one measurement opportunity per HF.

```bash
# on the gateway, as the lopos user, from /home/lopos/install
python3 curateCells.py --scan --scan-hfs 20 --batch 60
```

- `--scan-hfs` hyperframes to hold each batch (~32 s each; 20 ≈ 640 s ≈ ~20
  stats/link).
- `--batch` rounds published at once. With the repeating-SF pool the whole set
  (~59 rounds) fits one HF, so use a big batch (e.g. 60) for a single dense pass
  (~10 min). Smaller batches camp on a subset at a time.
- `--radius` candidate edge max distance from the core (coord units).

Anchors-only: the scan addresses anchors (`0xA000+id`) and the sink (`0xFFF0`)
— **never tags** — so it does not drain tag batteries. It stops by publishing an
empty list and runs in parallel with TDoA (the scan uses the free repeating-SF
slots; localization is unaffected).

### 2. `fetchCurateData.py` — dump the measured data to TSVs (GATEWAY only)

Reads the live DB and writes the TSVs the other two tools consume, filtered to a
time window so a fresh scan's data is not mixed with stale rows.

```bash
python3 fetchCurateData.py --out /tmp/lopos_viz --since "2026-06-03 22:55:00"
```

Outputs in `--out` (default `/tmp/lopos_viz`):

| file | columns | source |
|---|---|---|
| `anchors.tsv` | id, group_bitmask, x, y | `anchor` + `position` (self-fix) |
| `cells.tsv` | core, edge | `cell` |
| `linkcounts.tsv` | txAnchorId, rxAnchorId, received | `uwbstat` count per pair |
| `expected.tsv` | txAnchorId, rxAnchorId, rounds | asns where tx sent AND rx listened |
| `br.tsv` | anchorId, beaconRatio | `stat` (window avg) |
| `map.tsv` | mapcol, x1, y1, x2, y2 | `map` |

`expected` is **per pair** (not per transmitter): rounds where the transmitter
sent and the receiver heard ≥1 anchor that round (so it was awake). This makes
`received/expected` the true `core→edge` quality, undiluted by rounds where the
edge was not part of the receiver set.

### 3. `curateCells.py --mode build|refine` — propose a new cell table

Reads the TSVs (no DB access; can run anywhere) and emits a proposal.

```bash
python3 curateCells.py --mode build      # bottom-up: re-derive from all anchors
python3 curateCells.py --mode refine     # top-down: tweak the current cells
```

Per core it keeps edges with `received/expected ≥ RECV_GOOD`, requires
≥`MIN_EDGES` (2) non-collinear edges (`2Dratio ≥ MIN_2DRATIO`), and a core
Beacon-Ratio ≥ `BR_MIN_CORE` (85 — a weak core loses the whole superframe).
Cores with no self-position are dropped. A greedy set-cover over each cell's
**footprint** (convex hull of its anchors, surface inflated `HULL_AREA_INFLATE`
= +20%) keeps the fewest cells that cover the field; each core's group bitmask
is set from which map bands its footprint spans.

Outputs to `curate_out/`:
- `apply_cells_<ts>.sql` — backup tables + `DELETE/INSERT cell` +
  `UPDATE anchor.group`, transaction-wrapped. **Dry run — nothing is applied.**
- `proposed_cells_<ts>.csv` — the proposal as a table.

Review, confirm `uwbstat` is fresh, and apply on a test DB first. Only an admin
applies the SQL.

### `vizCells.py` — render the current cell state to images

Read-only renderer (reads the same TSVs). Writes to `viz/`:
- `overall.png` — all cells + coverage % over the full `map`
- `group_grp1..4.png`, `group_ungrouped.png`
- `cell_core<NN>.png` — one per cell
- `cells_summary.csv`

All 50 anchors are drawn and labelled; cores are stars (filled by Beacon-Ratio
colour, ringed); `core→edge` lines are coloured by reception
(green ≥ RECV_GOOD, orange weak, red none, grey = core never transmitted) with
`received/expected` labels; each cell's coverage hull (+20%) is shaded. The
caption notes the uwbstat period and any anchors lacking a self-position.

> Note: vizCells renders the **current** `cell` table overlaid with the latest
> measured link quality — not the proposed reorganization.

---

## Typical workflow

```bash
# on the gateway (lopos user, /home/lopos/install):
python3 curateCells.py --scan --scan-hfs 20 --batch 60          # 1. measure (~10 min)
python3 fetchCurateData.py --out /tmp/lopos_viz --since "<scan start>"   # 2. dump TSVs

# anywhere with the TSVs:
python3 vizCells.py                                             # 3. eyeball current state
python3 curateCells.py --mode build                            # 4. propose new cells
# 5. review curate_out/apply_cells_*.sql, then apply on a test DB, then live
```

---

## Scheduler hooks (in `loposScheduler.py` / `loposPyLib.py`)

The scan is driven entirely over MQTT — no extra DB tables.

- **`loposcore/scan`** (MQTT): payload is a JSON list of rounds
  `[{"tx":[ids],"rx":[ids]}]` (anchor ids; the scheduler adds the `0xA000`
  offset). An empty list stops the scan. `curateCells --scan` publishes it
  retained.
- **`uwbScanCells()`**: called from `planActions` each HF while the round list
  is non-empty (survives `cleanupScenario(Uwb)`). Each round = sink `0xFFF0`
  @actor 0, up to `UWB_TAG_OFS-1` (8) receivers @actors 1.., transmitter(s)
  @actors `UWB_TAG_OFS`.. — one superframe measures every tx→rx pair.

### The two superframe pools

`loposPyLib` allocates superframes from two pools (visualise with `pt.py`):

- **fixed / non-repeating** — `getNextSFidxRef` / `keepOutRepeatingAndfixedSF`,
  block offsets **0–1** (~25% of the HF). One-shot schedules re-added each HF.
- **repeating** — `getNextSFrepIdxRef` / `claimRepeatingAndfixedSF`, block
  offsets **2–7** (~75%). TDoA, accel and stat live here.

`uwbScanCells` allocates from the **repeating** pool (it runs after TDoA/accel/
stat, so the shared cursor is past their slots and it takes the free remainder),
with `inter_sf=2` to leave a gap between rounds so the sink is not flooded, and
`rescheduleSF=0` (one-shot — **not** the device repeat flag). That fits all
rounds in one HF for dense, even measurement without touching TDoA's slots. A
budget guard on `SFrepIdxRef` plus a rotating cursor spread the remainder if the
pool ever fills.

---

## Tunables (`curateCells.py`)

| name | default | meaning |
|---|---|---|
| `RECV_GOOD` | 0.75 | min `received/expected` for a good link |
| `MIN_EDGES` | 2 | min edges per cell (→ ≥3 anchors) |
| `MIN_2DRATIO` | 0.20 | reject (near-)collinear edge sets |
| `BR_MIN_CORE` | 85 | min core Beacon-Ratio |
| `RADIUS` | 1900 | candidate edge max distance from core |
| `HULL_AREA_INFLATE` | 1.20 | cell footprint = anchor hull, surface +20% |
| `BORDER_MARGIN` | 500 | core this close to a fence ⇒ serve both groups |
