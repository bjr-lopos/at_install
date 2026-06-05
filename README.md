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
`rescheduleSF=0` (one-shot — **not** the device repeat flag). Its per-HF budget
is `repPoolRemaining()` (see *moving TDoA window* below): when the pool is
nearly consumed this cycle the rotating cursor spreads the remaining rounds
over the next HFs, so a scan campaign runs slower while the window moves but
still completes full coverage.

---

## Scheduling approaches

> **⚠ REVERTED 2026-06-05 evening (commit `0671e38`).** Everything in this section
> below the *Proactive cell selection* subsection — the moving TDoA window, scan
> wrap, capture-COM discovery, COM-based cell pick, held blind trials, symmetric
> activeTag drop — was deployed on 2026-06-05 and **backed out the same evening**:
>**Root cause isolated same evening:** the capture-COM commit's
> `localizeDiscoverTags` ran a non-sargable full scan of the `tdoa` firehose
> table every planning cycle — scheduler time 0.35 s → ~5 s, so planning
> completed ~SF 38: after the early fixed-pool SFs where **stat** frames live,
> before the TDoA region (SF 90+) — killing stat reporting fleet-wide at exactly
> 15:21 while TDoA kept running (masked by activeTag's persist-forever
> semantics). Wrong-plot localizations came from capture-COM steering; the total
> stop 17:31–17:50 was the activeTag drop meeting the dead stat table.
> Production runs `abbbab6`: system-wide proactive + WINDOW=60 + cold-start fix
> only. **Exonerated by log forensics:** moving window, COM selection, activeTag
> drop — safe to re-introduce one at a time. Capture-COM needs a fast query
> first (index on `tdoa(updated)` or a sargable asn-range predicate) plus a
> measured runtime. Health gates for any redeploy: **stat freshness** (distinct
> addrs in `stat`, last 10 min ≈ fleet size), `Len dict activeTag` (journal),
> and **"Scheduler finished in" > ~2 s = alarm** (planning must beat the early
> fixed-pool SFs).

### Proactive, group-aware TDoA cell selection — system-wide

Toggle = presence of `cfg.tdoaProactiveCell`; scope = `LOPOS_TDOA_PROACTIVE_GROUPS`
(now `[1,2,3,4]`, i.e. all groups; remove the line for the same effect). Comment
`tdoaProactiveCell` out to revert to plain round-robin. Code:
`scheduleTdoaGroupsProactiveCB` (`loposScheduler.py`) + `findCloseCoreInGroup`,
`getPositionTagsMedian`, `tagGoodFixAge`, cell footprints/COMs (`loposPyLib.py`).

Per tag, each re-decide round (`overdue` is **percent past the plan interval**,
not seconds; gate is `overdue > 32`):

1. **Fresh good fix** (≥`MINHYPER` hyperbolas within `QUALITY_MAXAGE` s): pick the
   cell whose **footprint hull contains** the median position (median of `SAMPLES`
   fixes within `WINDOW` s), else the cell with the nearest **center of mass**
   (mean of ALL the cell's anchors, core + edges — `cellCOM`, not the core anchor
   alone). Hysteresis: switch only if the candidate is closer by > `MARGIN` and
   only after wanting to switch `MINDWELL` consecutive rounds. Cold start
   (`core == -1`) bypasses the dwell (else the tag is scheduled to nonexistent
   core −1 / dev `0x9fff` after a service restart).
2. **No good fix, but audible**: a location hint picks the cell directly each
   round — a stale fix up to `LOST_MAXAGE` (600 s) or the **capture COM**
   (`discoveredTag`, below) — no incumbent, no margin.
3. **Fully silent**: blind round-robin, first move after `FALLBACK_ROUNDS` (2) bad
   rounds, then each trial cell is **held `TRIAL_ROUNDS` (5) re-decide rounds**: a
   low-BR tag must *hear the plan while the trial cell is also the covering one* —
   P(heard in d rounds) = 1−(1−BR)^d, so holding trials beats fast rotation.
   `badRounds` counts continuously; only a good fix resets it.

Round-robin (`nextRoundRobinCore`) is unchanged and remains the cold-start +
safety-net path; per-group scoping means a staged rollout is one config line.

### Capture-COM discovery (`localizeDiscoverTags`)

`discoveredTag[addr]` = plain **center of mass of the distinct anchors that
captured the tag's TDoA blinks** in the last 100 s, from the `tdoa` capture
table (`dbAddTdoaInfo` stores *every* capture, including rounds
`storeTdoaResult` rejects on sync mismatch — a stale round still contributes
discovery data). Every capturing anchor counts equally (no RSSI weighting).
`uwbstat` is **not** used: it never carries tag transmissions here
(anchor-to-anchor only — the old uwbstat-based centroid was permanently empty).
Encoding: `tdoa.tag` = dev−0x1000 (negatives = stripped-address reports,
skipped), `tdoa.edge` = anchor id, anchor position addr = id+0xA000.

### Moving TDoA window (repeating-pool slide)

The repeating-pool cursor is **not reset to 90 each HF** (`initSFrepIdxRef`):
each cycle continues after the last slot the previous HF used, so the
TDoA/accel/stat/scan block slides through SF 90..240 (~32 SFs per HF) and
**rotates** back to `LOPOS_FIRST_REPEAT_SF+1` past `LOPOS_LAST_USABLE_SF`
(`claimRepeatingAndfixedSF`). Block offsets 0–1 stay reserved. After a rotate
every slot is checked free against pending todos (`isSFslotFree`); consecutive
HFs are kept **slot-disjoint** (`repPoolRemaining()` budgets to the *previous*
cycle's start), and lapping the own cycle start still exits as overstressed.

Why: a device that misses the new plan replays last HF's provisioning at the
same absolute SF. With a static window that landed inside live frames →
`storeTdoaResult failed … used sync X, now sync seems Y` (the gateway bundles
captures per (asn, tag) and requires **all reporting anchors to agree on the
sync ref, first-report-wins** — one stale or foreign-cell report arriving first
poisons the whole bundle). With the moving window stale replays land in
**silent SFs**: measured stale-sync rate went from ~0.13–0.15 per fix (bursts
to 20/min) to ~0 at deploy. Hard requirement: one-shot scheduling
(`tdoa_rescheduleSF=0`) — the device `.repeat` flag is incompatible with a
moving window.

### Evaluation + known issues

- `proactiveEval.py N` (gateway, lopos user) appends per-group fix rates over an
  N-minute window to `/home/lopos/proactive_eval.csv`. Compare each group to its
  own trend over time — grp1/2 are **different physical zones**, not a control
  for grp3/4, and the gain is activity/diurnal-dependent (evening ≠ morning).
- `Missing frames between A-B` (loposcore, serial schedule-fetch sequence):
  ref A+1..B−1 never fetched its schedule that round (anchor id or 4-tag chunk)
  → those devices run the HF unprovisioned. Chronic ~40–70/h, device/radio-side,
  unaffected by the changes above; the dominant remaining provisioning-loss path.
- A tag is TDoA-scheduled only while it keeps proving presence: a `stat` report
  within the last 900 s (`updateActiveTags`). Quiet tags are **dropped** (stat
  scheduling itself is not gated, so they keep getting stat offers and re-enter
  — cold start — on their next stat success). **Intentional** liveness gate:
  presence is proven by a device response, never presumed from history. Do not
  seed/fake it at startup.
- Cross-group moves (tag carried to another group's area) are still unhandled:
  the Discover wide-net scenario needs `cell` rows for core 0 (admin SQL), which
  are not configured.
- A tag's `dev` in some loposcore log lines appears with the `0x1000` bit
  stripped (`dev:0x0049` = tag `0x1049`) — log formatting in the C binary, the
  addresses on air and in `todo` are correct.

### Proactive tunables (`localConfig.py`)

| name | default | meaning |
|---|---|---|
| `LOPOS_TDOA_PROACTIVE_SAMPLES` | 5 | median over the last N fixes |
| `LOPOS_TDOA_PROACTIVE_WINDOW` | 60 | … within this many seconds |
| `LOPOS_TDOA_PROACTIVE_MAXAGE` | 60 | ignore positions older than this (s) |
| `LOPOS_TDOA_PROACTIVE_MARGIN` | 300 | switch only if closer by > this |
| `LOPOS_TDOA_PROACTIVE_MINDWELL` | 2 | … and only after this many rounds |
| `LOPOS_TDOA_PROACTIVE_MINHYPER` | 3 | a good fix needs ≥ this many hyperbolas |
| `LOPOS_TDOA_PROACTIVE_QUALITY_MAXAGE` | 45 | no good fix within this (s) = bad round |
| `LOPOS_TDOA_PROACTIVE_FALLBACK_ROUNDS` | 2 | bad rounds before the first blind move |
| `LOPOS_TDOA_PROACTIVE_LOST_MAXAGE` | 600 | stale fix age accepted as a location hint |
| `LOPOS_TDOA_PROACTIVE_TRIAL_ROUNDS` | 5 | rounds each blind trial cell is held |

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
