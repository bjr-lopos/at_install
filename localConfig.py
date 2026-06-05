#!/usr/bin/env python
#import preprocessing
mysql = {
    "host": "localhost",
    "user": "ilvo",
    "passwd": "ilv0",
    "db": "ilvo",
}


#testFwd=1
#testAnchor=1
#testSinkStress=1
#testTDoA=1
#testAccel=1
#testDiscover=1
#testUWB=1
# uwbInfoAllCells=1   # disabled: UWB-all-cells is driven by the plan table (scenario 13) via scheduleCellSyncTest; enabling this too double-schedules and overflows the hyperframe
#altIUwbInfolvoScan=1
scheduleTDoAwGroups=1

# Proactive, group-aware TDoA cell selection (presence-toggle, like scheduleTDoAwGroups above).
# Uncomment tdoaProactiveCell to pick each tag's cell from its smoothed location instead of blind
# round-robin; comment it out to revert to round-robin. The tunables below always apply when on.
tdoaProactiveCell=1
LOPOS_TDOA_PROACTIVE_GROUPS=[1,2,3,4]   # all groups proactive (system-wide). grp1/2 are not a valid
                                       # control for grp3/4 (different physical zones), so the staged
                                       # grp3/4-only A/B was dropped; evaluate absolute fix-rate trend.
LOPOS_TDOA_PROACTIVE_SAMPLES=5          # median over the last N position fixes (outlier rejection)
LOPOS_TDOA_PROACTIVE_WINDOW=60          # ... within this many seconds
LOPOS_TDOA_PROACTIVE_MAXAGE=60          # ignore a tag position older than this (s) -> fallback
LOPOS_TDOA_PROACTIVE_MARGIN=300         # switch cell only if a candidate is closer by > this (coord units)
LOPOS_TDOA_PROACTIVE_MINDWELL=2         # ... and only after wanting to switch this many rounds (min-dwell)
LOPOS_TDOA_PROACTIVE_MINHYPER=3         # a "good" fix needs >= this many hyperbolas
LOPOS_TDOA_PROACTIVE_QUALITY_MAXAGE=45  # no good fix within this (s) counts as a bad round
LOPOS_TDOA_PROACTIVE_FALLBACK_ROUNDS=2  # after this many bad rounds, fall back to round-robin advance

LOPOS_SF_BLOCK_SIZE=8
LOPOS_LAST_FIXED_SF = 89
LOPOS_FIRST_REPEAT_SF = 89
LOPOS_LAST_USABLE_SF = 240

LOPOS_SCENARIO_System =  0
LOPOS_SCENARIO_ReqSinkSchedule =  1
LOPOS_SCENARIO_ReqAnchorSchedule =  2
LOPOS_SCENARIO_AnchorProvisioning =  3
LOPOS_SCENARIO_ReqTagSchedule =  4
LOPOS_SCENARIO_TagProvisioning =  5
LOPOS_SCENARIO_Fwd =  6
LOPOS_SCENARIO_Discover =  7
LOPOS_SCENARIO_TDoA =  8
LOPOS_SCENARIO_TWR =  9
LOPOS_SCENARIO_CIR = 10
LOPOS_SCENARIO_Accel = 11
LOPOS_SCENARIO_Stat = 12
LOPOS_SCENARIO_Uwb = 13

LOPOS_SCENARIO_TDoA_TAG_OFS=10
LOPOS_SCENARIO_TDoA_TAG_MAX=21
LOPOS_SCENARIO_Discover_TAG_OFS=16
LOPOS_SCENARIO_Discover_TAG_MAX=21
LOPOS_SCENARIO_UWB_TAG_OFS=9
LOPOS_SCENARIO_UWB_TAG_MAX=14

# --- backfilled from wish localConfig.py so the newest loposScheduler/loposPyLib code runs ---
# (the ILVO config originally lacked these; values copied from wish defaults)
LOPOS_ITERATE_TAG_PER_CELL=0

LOPOS_SCENARIO_TDoA_MAX_SF=24
LOPOS_SCENARIO_TDoA_INTER_SF=1
LOPOS_SCENARIO_TDoA_INTER_ACTOR=2
LOPOS_SCENARIO_TDoA_FIXED_SUPERFRAMES=1
LOPOS_SCENARIO_TDoA_SUPERFRAMES_MOD=[2,3,4,5]

LOPOS_SCENARIO_STAT_MAX_SF=6
LOPOS_SCENARIO_STAT_INTER_SF=1
LOPOS_SCENARIO_STAT_FIXED_SUPERFRAMES=0

LOPOS_SCENARIO_ACCEL_MAX_SF=30
LOPOS_SCENARIO_ACCEL_INTER_ACTOR=2
LOPOS_SCENARIO_ACCEL_INTER_SF=1
LOPOS_SCENARIO_ACCEL_DEV_MAX=10
LOPOS_SCENARIO_ACCEL_SUPERFRAMES_MOD=[6,7]


#tagPerCoreCellFixed={
#2:[5,14,22,30,33,45,46,48,49,55,57,58,59,61,62,64,67,73,83,104,107,109,110,111,120],
#5:[13,27,39,43,56,75,78,87,91,92,95,96,97,100],
#6:[4,34,36,65,68,74,80,81,86,88,93,94,98,105,116,119],
#1:[7,17,37,44,54,66,69,72,85,90,99,102,103,106,113,114],
#4:[2,3,8,9,11,12,15,16,18,21,26,28,29,31,32,40,42,47,51,52,53,60,70,76,77,82,84,101]
#}

#tagPerCoreCellFixed={
#1:[21,95,129,143]
#}


#TDOA2POS_OFFSET_X=100
#TDOA2POS_OFFSET_Y=100
TDOA2POS_FACTOR_X=2.0
TDOA2POS_FACTOR_Y=2.0
