#!/usr/bin/env python
#import preprocessing
mysql = {
    "host": "localhost",
    "user": "lopos_test",
    "passwd": "lopos_test",
    "db": "lopos_test",
}


LOPOS_SF_BLOCK_SIZE=8
LOPOS_LAST_FIXED_SF = 81
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
