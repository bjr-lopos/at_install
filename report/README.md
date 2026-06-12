# Measurement-campaign w2w report — generation flow

Reusable procedure to (re)generate the LoPoS localization **week-over-week report**
(`../lopos_w2w_report.pdf`) for a new **baseline-vs-current** comparison.

- **Audience: biologists** (not IT). Lead with the environment (vegetated, RF-hostile), keep TDoA light.
- **Brand: apply the `lopos-brand` skill** (`~/.claude/skills/lopos-brand.skill`) — yellow=current,
  slate=baseline, black `▲` deltas (never red/green), no gradients, alternating table rows, dot-motif header.
- **ONE output file**: `lopos_w2w_report.pdf`. Retire stale PDFs. Announce any file/window/regime change **in CAPITALS**.

## Files (this dir + repo root)
| file | role |
|---|---|
| `../make_w2w_report.py` | the report generator (reportlab, lopos-brand). Edit **data + narrative** here. |
| `gen_report.sh` | build: runs the generator + renders `/tmp/rep-*.png` previews. |
| `report_data.py` | pull per-group ptag/min for the two windows (piped to ilvo). |
| `make_viz2.sh` | render before/after cell maps via `vizCells` (runs on ilvo). |
| `../cellmap_data.tsv`, `../cells_before.png`, `../cells_after.png` | cell-map inputs/renders. |

## Step 1 — choose the two windows
Baseline window vs current ("since last deploy") window — **matched length, same clock & weekday** if possible.

**CRITICAL — record the SCHEDULING REGIME of each window; it sets the ptag ceiling:**
- **un-gated** (≤ 2026-06-08 12:24, commit `5ffaa6b`): no hit-pacing → ptag up to ~1.875/min.
- **gated** (≥ 2026-06-08 12:24): hits paced to `plan.interval` (~96 s) → ptag ≤ ~0.625/min.

A baseline and current in **different** regimes are **not** comparable on absolute ptag — say so in the report.
Also note the cell config + selection mode each window ran (cells: 20→13 on 2026-06-10; roaming since ~Jun 4).
Data: live `position` table + weekly archives `position_YY_MM_DD*` (rotated by `table_hist.sh`, Sat 23:59).

## Step 2 — pull the data (ilvo)
Edit the window datetimes in `report_data.py` (`CUR_START`, `BASE_START`), then:
```
cat report/report_data.py | ssh ilvo "cd /home/lopos/install && sudo -u lopos python3 -"
```
Prints per-group base/now fixes, tags, ptag/min. Metric = `COUNT(*) FROM position WHERE numHyperbola>=3`,
per group, ÷ window-min ÷ distinct tags. **This is HITS (positions), not transmissions.**
(Battery/over-transmission is a *separate* metric — schedule count, from `processTagPerCoreCell` in the journal.)

## Step 3 — cell maps (only if the cell table changed)
Edit the before/after tables in `make_viz2.sh` (`group_src`, `cell_t`), then:
```
ssh ilvo 'bash -s' < report/make_viz2.sh
scp ilvo:/tmp/vb/out/overall-used.png cells_before.png
scp ilvo:/tmp/va/out/overall-used.png cells_after.png
```
Coverage %: the render shows `vizCells`' hull-union metric; the curateCells/drive analysis may differ
(e.g. **65% render vs 68% drive** for the 20-cell; both agree 82% for 13-cell). **State the source** in the report.

## Step 4 — update the report
In `make_w2w_report.py` set `base`, `now`, `fixes_b`, `fixes_a`, `delta`, totals; update the **periods table**,
the **narrative**, and the **"Project work delivered"** bullets. Keep the lopos-brand styling.

## Step 5 — generate + verify
```
bash report/gen_report.sh        # -> ../lopos_w2w_report.pdf + /tmp/rep-*.png
```
Verify: wording, numbers match the data, **regime/source stated**, exactly one PDF in the tree.

## Lessons baked in (read before editing)
- **State the date/regime/source of every number.** The grp2 "1.30 vs 0.46" confusion came from comparing
  across the Jun-8 gate without flagging it (un-gated 1.30 → gated 0.46). Never quote a number without its regime.
- **ptag/min = HITS** (positions); **battery = COUNT** (schedules/transmissions). Don't conflate.
- One report filename; announce file/window/approach changes in CAPITALS — a silent filename switch
  (`proactive_w2w_report.pdf` → `lopos_w2w_report.pdf`) burned hours once.
