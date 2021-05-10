            SELECT 
                case 
                    when (devTx & 0xFF00)=0xA000 then 900 + (devTx & 0x0FFF)
                    else 0 + (devTx & 0x0FFF) 
                end 
                as id_begin, 
                case 
                    when (devRx & 0xFF00)=0xA000 then 900 + (devRx & 0x0FFF)
                    else 0 + (devRx & 0x0FFF)
                end 
                as id_end, 
                count(*) as info, 
                case 
                    when count(*) >= 18 then '0x00FF10'
                    when count(*) >= 16 then '0xffb810'
                    when count(*) >= 14 then '0xff8810'
                    when count(*) >= 12 then '0xff5810'
                    when count(*) >= 10 then '0xff2815'
                    else '0xFF0020'
                end
                as color 
            from 
                uwbstat left join anchor as txa on uwbstat.devTx = txa.addr left join  anchor as rxa on uwbstat.devRx = rxa.addr
            where 
                TIMESTAMPDIFF(SECOND,updated,now()) <640
            group by 
                devTx, devRx

