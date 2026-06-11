# Project guidance for Claude

## System architecture
LoPoS tracks free-ranging animals in an **RF-hostile, vegetated environment** (plants/trees/canopy attenuate and scatter the radio links and break line-of-sight). Two radio layers: a **sub-GHz long-range** link (provisioning + reporting) and **UWB** (ranging). Three device roles:
- **Sink** — base station. **Provisions all devices** over the **sub-GHz** link — i.e. assigns each device *when it acts*: which **SF (superframe) slot** within which **HF (hyperframe)** slot, per scenario (TDoA=8, Stat=12, Accel=11, …) — and captures their reports.
- **Anchors** — fixed reference stations (mains/large-cell powered). **In every cell the core anchor syncs the edge anchors via UWB**; the anchors capture the UWB pulses from tags and report those captures to the sink. A **cell** = one core anchor + its edge anchors (the `cell` table: core,edge).
- **Tags** — carried by animals; **battery-critical**. A tag just emits a UWB pulse in its assigned **TDoA slot within the repeating hyperframe**.
- **Stats (scenario 12)** are sent by **both anchors and tags** in their sink-provisioned scenario-12 frames (device health/liveness; `activeTag` keys off tag stat freshness, loposPyLib).
- A tag's position = **time-difference-of-arrival** of its single pulse across the surrounding (synced) anchors of a cell. The TDoA report's `sync` is that cell's **core anchor**; mismatched syncs in one (asn,tag) bundle are rejected (`storeTdoaResult`). Because provisioning over sub-GHz can't be guaranteed through vegetation, a tag may act on **stale slot/hyperframe info** and pulse where anchors aren't listening / against a stale sync → no fix; the **moving TDoA window** (scenario 8 sliding through the hyperframe) makes such stale pulses land in idle slots instead of corrupting a live measurement.

## Commit policy
- **Never** add a `Co-Authored-By: Claude ...` trailer (or any Claude/AI co-author line) to commit messages. Commit messages must contain no AI attribution.

## Tag battery constraint (read before touching scheduling)
- **Tags run on tiny batteries; every UWB transmission costs battery.** Anything that makes a tag transmit/report **more often** — TDoA cadence, stat/accel intervals, discovery, re-scheduling, retries — has a **large** cumulative impact on tag lifetime. Treat fix-rate as a cost, not just a benefit: a higher ptag/min means more blinks = faster drain.
- The intended per-device TDoA period comes from **`plan.interval` per device** (honored via the `checkForSchedules` gate `age > interval - HF`, loposPyLib.py), **not** a fixed value — the `interval=32` defaults in the CB / `processTagPerCoreCell` are vestigial (only the disabled `rescheduleSF` auto-repeat used them). Anchors are mains/large-cell powered; **tags are the battery-critical actors** — be especially careful with anything in the TDoA/stat/accel/discover scenarios that addresses tag addresses (`0x1000+`).
- Before changing any scenario cadence/interval/retry behavior: estimate the change in **tags-transmissions-per-tag-per-hour** and call it out. If you "improve" fix rate, you are likely spending battery; say so.
- **Root-caused + FIXED (2026-06-08, commit `5ffaa6b`):** tags were fixing ~every 37 s despite a 95 s `plan.interval` (~3× over-scheduled = pure battery drain). Cause: the TDoA groups path (`scheduleTDoAgroups`, `fixedSF=1` via `LOPOS_SCENARIO_TDoA_FIXED_SUPERFRAMES`) routed through **`checkForSchedulesFixed`, which had no interval gate** (returned every active tag every planning cycle) — unlike `checkForSchedules` (stat/accel) which gates on `age > interval - HF`. Fix = added the same gate to `checkForSchedulesFixed` (keeps its `ORDER BY 1`). TDoA now honors `plan.interval`; verified ~2.7× fewer transmissions, scheduler unaffected. Two functions exist: gated `checkForSchedules` (ORDER BY overdue) and `checkForSchedulesFixed` (ORDER BY addr) — both now gated.

## Deployment note
- The running services execute copies under `/usr/local/bin` (`loposScheduler.py`, `loposPyLib.py`, `loposTDoA2Pos.py`, `loposcore`), installed by `bootstrap.sh` via `sudo cp`. A `git pull` into the working dir does **not** update them — you must `sudo cp` the changed files to `/usr/local/bin` and restart the services (`loposcore`, `loposmath`/`lms`, `loposplan`). The scheduler also imports `localConfig` from `/usr/local/bin` when launched from there.
- The gateway is reached over SSH as host alias `ilvo` (user has root via `sudo`; the app DB user is `ilvo`/`ilv0`, driver `mysql.connector`, dict `localConfig.mysql`). The app DB user lacks `CREATE`/`DROP`/`DELETE` on most tables. SSH note: backgrounding a process inside an ssh command (`& sleep …`) often yields no output / kills the child — launch long jobs via a backgrounded Bash tool call running `nohup … & echo pid`, and verify in a separate call.

## DB access & applying cell/anchor changes (admin)
- The app user `ilvo` has only **SELECT/INSERT** on most tables, **DELETE only on `todo`**, no `CREATE`/`UPDATE` on `cell`/`anchor`. So `apply_cells_*.sql` (which does `CREATE TABLE cell_bak…`, `DELETE FROM cell`, re-`INSERT`, `UPDATE anchor.group`) **silently rolls back** if run as `ilvo` — this is why an "applied" curation can leave the live `cell` table unchanged. **Verify a cell change actually committed** (binlog has no rolled-back txns: `sudo mysqlbinlog --base64-output=DECODE-ROWS -v /var/lib/mysql/binlog.* | grep '`cell`'`, or just re-query).
- To **apply for real**, run as MySQL admin: `sudo mysql --defaults-file=/etc/mysql/debian.cnf ilvo < apply_cells_*.sql` (the `debian-sys-maint` account; root@localhost needs a password we don't have). Then **restart `loposplan`+`loposmath`** (they cache cells: `cellFootprint`, `positionCoreAnchor`, `cellsPerGroup` load once per process). Backups: SQL dumps in `/home/lopos/install/bu/cell_*.sql`; the apply SQL also makes `cell_bak_<ts>`/`anchor_bak_<ts>` tables.
- **Cell history:** old layout = 11 cores `{0,11,12,20,26,…}` (in `bu_cell.sql`, ~Jan 2024). The 20-core `{1,4,8,10,15,…}` config was already live by the May-2026 baseline. The **13-core curated config** `{4,7,8,11,16,18,25,26,27,29,34,39,48}` (97 edges, coverage 65→82%, no unused cells) was applied **2026-06-10** (`cell_bak_20260604_131225`); early result: per-tag fix-rate up in ALL groups (g4 +69%) at the same throttled schedule.

## Deploy canaries (run after ANY scheduler/DB change + restart)
- **Scheduler speed:** `Scheduler finished in` must stay **< ~2 s** (an unindexed full-scan of the `tdoa` firehose once pushed planning 0.35→5 s; planning then completed past the early fixed-pool SFs and **silently killed the fleet-wide stat pipeline** — 2026-06-05 incident).
- **Stat freshness:** distinct tags reporting `stat` in the last 10 min ≈ fleet size (`SELECT COUNT(DISTINCT addr) FROM stat WHERE updated>NOW()-INTERVAL 10 MINUTE AND addr>=0x1000`). `Len dict activeTag` in the loposplan journal is the live canary.
- **No `processTagPerCoreCell {-1…` rounds** (cold-start scheduling to nonexistent core −1 / dev `0x9fff`), **no tracebacks**, and after a cell change confirm **no group is starved** (per-group fix counts all > 0).

## Cell-curation toolchain (new — see README.md)
- `curateCells.py` (build/refine + `--scan`), `vizCells.py`, `fetchCurateData.py` re-derive the TDoA `cell` table from **measured** UWB reception. README.md has the full description. Metric = reception **count** (`received/expected` per ordered pair ≥ `RECV_GOOD`), **not** RSSI. The broad scan runs anchors-only (never tags) over MQTT topic `loposcore/scan`, scheduled by `uwbScanCells` from the **repeating** SF pool (`getNextSFrepIdxRef`, block offsets 2–7, interleaved `inter_sf=2`, one-shot — runs after TDoA/accel/stat so it uses their leftover slots without collision).

## Resume / proactive cell selection (state as of 2026-06-04 evening) — ACTIVE EXPERIMENT
**What is live now:** Proactive, group-aware TDoA cell selection is DEPLOYED and ENABLED for **grp3/4
only** on ilvo (round-robin unchanged for grp1/2). Toggle = `cfg.tdoaProactiveCell` (presence) +
`cfg.LOPOS_TDOA_PROACTIVE_GROUPS=[3,4]` in `localConfig.py`. Code: `loposScheduler.py`
(`scheduleTdoaGroupsProactiveCB`, `nextRoundRobinCore`) + `loposPyLib.py` (`findCloseCoreInGroup`,
`getPositionTagsMedian`, `tagGoodFixAge`, cell footprints; fixed `dz-cz` typo). Round-robin is reused
as the cold-start + quality fallback (a tag uses round-robin until it has a fresh good fix). Design
plan: `~/.claude/plans/two-options-now-we-tingly-emerson.md` (local to that PC; summary here).
Deployed: `loposScheduler.py`+`loposPyLib.py` `sudo cp`'d to `/usr/local/bin`; `localConfig.py` is a
symlink so the repo copy is live. Restart `loposplan`+`loposmath` after any change (not loposcore).
All committed+pushed to `ab-install/master`.

**Early result (1 window, ~20 min settle, 2026-06-04 ~17:11):** per-tag fix-rate Δ vs baseline —
grp3 **+20%**, grp4 +8%; control grp1 +9%, grp2 +0.7% (so ~5–9% global drift → net grp3 ≈ +12–15%,
grp4 marginal). No errors, services healthy. Only ~40% of grp3/4 tags were on the proactive path
(rest fell back to round-robin: no fresh position within the 30 s window).

**How to continue next session (read this first):**
- Evaluation is **manual** (no standing cron — auto-mode blocked installing a recurring job on the
  production gateway). Take a sample any time:
  `ssh ilvo 'cd /home/lopos/install && sudo -u lopos python3 proactiveEval.py 30'` — it appends
  `/home/lopos/proactive_eval.csv` (seeded 2026-06-04 17:17). Read that CSV for the
  grp3/4-vs-grp1/2(control) trend. To auto-collect while idle, the user can authorize this cron
  (lopos crontab): `*/30 * * * * /usr/bin/python3 /home/lopos/install/proactiveEval.py 30 >> /home/lopos/proactive_eval.log 2>&1`.
- **Decide system-wide** when grp3/4 stay consistently above the grp1/2 control: set
  `LOPOS_TDOA_PROACTIVE_GROUPS=[1,2,3,4]` (or remove the line), commit/push, `git pull` on ilvo,
  `sudo cp` the changed file(s), restart `loposplan`+`loposmath`.
- **Revert** = comment `tdoaProactiveCell=1`, pull on ilvo, restart `loposplan`+`loposmath`.
- **Tuning lever**: widen `LOPOS_TDOA_PROACTIVE_WINDOW` (30→60 s) to pull more grp3/4 tags onto the
  proactive path (likely larger effect); other tunables: SAMPLES/MAXAGE/MARGIN/MINDWELL/MINHYPER/
  QUALITY_MAXAGE/FALLBACK_ROUNDS in `localConfig.py`.
- **Remove the cron** when done evaluating: `sudo -u lopos crontab -e` and delete the proactiveEval line.

## Resume / TODO (state as of 2026-06-03 evening)
Done today: merged wish+ilvo onto master & deployed; fixed grp3/4 collapse (reverted `rescheduleSF`/repeat to one-shot, `tdoa_rescheduleSF=0`, commented re-enable line); built the curation toolchain; broad rep-pool scan working (dense: median ~12, max 14 opportunities/link, ~10 min, TDoA unaffected, no tag drain); `--mode build` on fresh dense data → **13 cells, 79% coverage**, low-BR (13/14/99) / no-position (2/6/33/37/41/52) / collinear cores dropped; example links 8→3 (13/13) and 8→10 (12/12) now candidates. Proposal written to `curate_out/apply_cells_*.sql` (**dry-run, NOT applied**). All committed+pushed to `ab-install/master`; README.md added.

Open items to pick up:
1. **Cells per group still high** (4/7/7/4 vs ~2 target). `coverage_select` keeps every cell that adds hull area; the lowest-priority "fewest cells / ~2 per group" thinning pass is not enforced yet — add it (overlap-merge or per-group cap) when ready.
2. **Balance criterion is disabled** ("evaluate results first"). `balance_offset`/`rebalance` still in `curateCells.py` but not called in `qualify`. Decide metric (rectangle-centre vs centre-of-mass) + threshold before re-enabling.
3. Optionally run the scan ~25 HF for ≥16 opportunities/link (currently 12–14).
4. `vizCells.py` renders the **current** cell table, not the proposal — could add a `viz_proposed/` render to compare current vs proposed.
5. The proposed cells are **not applied** — review SQL + `viz/`, dry-run on a test DB, then apply live (admin only); then verify grp3/4 fix-rate and `storeTdoaResult` error rate.
6. Optional later lever: re-enable `tdoa_rescheduleSF = int(math.log2(interval))+1` in `loposScheduler.py` **only** with stable, constant planning.
