SELECT
            d.addr,
	    ((6 - (s.uwbTxPwr div 32)) * 3) + round((s.uwbTxPwr & 0x01F)/2) as isUwbTxPwr,
            d.uwbTxPower as setUwbTxPwr
FROM
            device as d,
	    stat as s,
            (select addr, max(updated) as last_update from stat group by addr) as ref
WHERE
            s.addr = d.addr and
            s.addr = ref.addr and
	    s.updated = ref.last_update and
            d.uwbTxPower > 0 and
            d.uwbTxPower <> ((6 - (s.uwbTxPwr div 32)) * 3) + round((s.uwbTxPwr & 0x01F)/2)
