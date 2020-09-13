        SELECT
            p.addr,
            CASE
                WHEN ref.last_update IS NULL THEN 0
                else DATE_ADD(ref.last_update, INTERVAL p.interval SECOND)
            end as schedule,
            CASE
                WHEN ref.last_update IS NULL THEN p.interval/2
                else TIMESTAMPDIFF(SECOND,ref.last_update,now()) - p.interval
            end as diff
        FROM
            sys,
            plan as p
        LEFT JOIN
            (select addr, max(updated) as last_update from position group by addr) as ref
        ON
            p.addr = ref.addr
        where
            scenario = 8
            and (
                    (ref.last_update IS NULL)
                    or
                    (TIMESTAMPDIFF(SECOND,ref.last_update,now()) > ( p.interval - (sys.SFmax*sys.SFticks/32768)) )
            )
        order by 3 desc;


