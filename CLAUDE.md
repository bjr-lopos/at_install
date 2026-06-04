# Project guidance for Claude

## Commit policy
- **Never** add a `Co-Authored-By: Claude ...` trailer (or any Claude/AI co-author line) to commit messages. Commit messages must contain no AI attribution.

## Deployment note
- The running services execute copies under `/usr/local/bin` (`loposScheduler.py`, `loposPyLib.py`, `loposTDoA2Pos.py`, `loposcore`), installed by `bootstrap.sh` via `sudo cp`. A `git pull` into the working dir does **not** update them — you must `sudo cp` the changed files to `/usr/local/bin` and restart the services (`loposcore`, `loposmath`/`lms`, `loposplan`). The scheduler also imports `localConfig` from `/usr/local/bin` when launched from there.
- The gateway is reached over SSH as host alias `ilvo` (user has root via `sudo`; the app DB user is `ilvo`/`ilv0`, driver `mysql.connector`, dict `localConfig.mysql`). The app DB user lacks `CREATE`/`DROP`/`DELETE` on most tables. SSH note: backgrounding a process inside an ssh command (`& sleep …`) often yields no output / kills the child — launch long jobs via a backgrounded Bash tool call running `nohup … & echo pid`, and verify in a separate call.

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
- Evaluation data is being logged on ilvo by a **cron** (lopos crontab) running `proactiveEval.py 30`
  every 30 min → appends `/home/lopos/proactive_eval.csv` (stdout/errs in `/home/lopos/proactive_eval.log`).
  Read the CSV to see the grp3/4-vs-grp1/2(control) trend over time. Run a one-off any time:
  `ssh ilvo 'cd /home/lopos/install && sudo -u lopos python3 proactiveEval.py 30'`.
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
