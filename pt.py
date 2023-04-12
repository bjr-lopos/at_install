import sys
import blessed
import loposPyLib as loposPy

term = None
ref_pos = None

def plot(scheduleAT, marker= "*"):
    with term.location(1 + scheduleAT//8, ref_pos[0] - ( 8 - scheduleAT%8)):
            print(marker, end='')



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
        if schedule[4] == 0:
            marker = "s"
        if schedule[4] == 8:
            marker = "T"
        if schedule[4] == 11:
            marker = "A"
        if schedule[4] == 12:
            marker = "S"
        plot(scheduleAT, marker)


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

term = blessed.Terminal()
prep_table()
ref_pos = term.get_location()
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

