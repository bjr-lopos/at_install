import sys
import blessed
import loposPyLib as loposPy
import localConfig as cfg

term = None
ref_pos = None

def plot(scheduleAT, marker= "*", rep = 32):
    y = ref_pos[0] - ( 8 - scheduleAT%8)
    x = scheduleAT//8
    xofs = x
    while True:
        with term.location(1 + xofs, y):
                print(marker, end='')
        xofs = (xofs + rep) % 32
        if xofs == x:
            break
        

def grabSchedules():
    sql = """
select 
    hex(addr), 
    case 
        when addr&0xF000 = 0xA000 then "anchor"
        when addr&0xFFF0 = 0xFFF0 then "sink"
    else 
        "tag"
    end
    as type,
    case 
        when addr&0xFFF0 = 0xFFF0 then addr&0x000F
    else 
        addr&0x0FFF
    end
    as id,
    scheduleAT,
    scenario,
    actor,
    rescheduleSF,
    TIMESTAMPDIFF(SECOND,updated,now()) as secSinceLastUpdate
from 
    todo
order by 
    4,6;
    """

    records = loposPy.wrappedSql(sql, {} )
    for schedule in records:
        marker = "?"
        scheduleAT = schedule[3]
        rescheduleSF = schedule[6]
        if rescheduleSF > 0:
            interval = 2 ** ( schedule[6] - 1)
        else: 
            interval = 32
        if schedule[4] == 0:
            marker = "s"
        if schedule[4] == 8:
            marker = "T"
        if schedule[4] == 11:
            marker = "A"
        if schedule[4] == 12:
            marker = "S"
        plot(scheduleAT, marker, interval)


def print_cursor_location():
    val = term.get_location()
    print(val)


def prep_table(): 
    print(" ", end='')
    for i in range(32):
        print(str(i%10), end='')
    print()
    for i in range(8):
        print(str(i) + "\n", end='')

def add_provision_slots():
    prov_slot = 0
    adjust2allowedOffsets = {0:0, 1:0, 2:6, 3:5, 4:4, 5:3, 6:2, 7:1}  
    while prov_slot <= cfg.LOPOS_LAST_FIXED_SF:
        plot(prov_slot, "p")
        prov_slot =  prov_slot + 1
        blockOfs = prov_slot % cfg.LOPOS_SF_BLOCK_SIZE
        prov_slot += adjust2allowedOffsets[blockOfs]


term = blessed.Terminal()
prep_table()
ref_pos = term.get_location()
add_provision_slots()

loposPy.initDB()
grabSchedules()
print("------------------------------")


if False: 
    plot(0, "A")
    plot(1, "B")
    plot(2, "C")
    plot(69, "a")
    plot(70, "b")
    plot(71, "c")

