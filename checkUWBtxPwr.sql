





SELECT
            d.addr,
	    s.uwbTxPwr as isTx,
            d.uwbTxPower as setTx
        FROM
            device as d,
	    stat as s,
            (select addr, max(updated) as last_update from stat group by addr) as ref
        where
            s.addr = d.addr and
            s.addr = ref.addr and
	    s.updated = ref.last_update and
            d.uwbTxPower > 0 and
            d.uwbTxPower <> s.uwbTxPwr
