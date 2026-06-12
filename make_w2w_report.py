"""Lopos-branded week-over-week localization report for a BIOLOGIST audience.
Palette: Yellow #F5C800 (current) / Slate #9B9BB4 (baseline) / Black #1A1A1A / light grey.
Black deltas with up-arrow (never red/green), minimal charts, geometric sans (Helvetica)."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                ListFlowable, ListItem, Flowable, KeepTogether, Image)
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, String, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart

YELLOW = colors.HexColor('#F5C800'); BLACK = colors.HexColor('#1A1A1A')
GREY = colors.HexColor('#F0F0F0'); ROW = colors.HexColor('#F7F7F7')
SLATE = colors.HexColor('#9B9BB4'); LINE = colors.HexColor('#E0E0E0')
HERE = os.path.dirname(__file__)

# ---- data: baseline (30 May window) vs current (since 10 Jun cell deploy) ----
groups  = ['grp1', 'grp2', 'grp3', 'grp4']
base    = [0.180, 0.183, 0.145, 0.305]
now     = [0.283, 0.456, 0.425, 0.328]
fixes_b = [4617, 4707, 3516, 7833]
fixes_a = [7262, 10345, 10283, 8422]
delta   = ['+57%', '+149%', '+193%', '+8%']
TOT_B, TOT_A, TOT_D = sum(fixes_b), sum(fixes_a), '+76%'

S = getSampleStyleSheet()['Normal']
H = lambda **k: ParagraphStyle('h', parent=S, **k)
disp = H(fontName='Helvetica-Bold', fontSize=21, textColor=BLACK, leading=24, spaceAfter=2)
sub  = H(fontName='Helvetica', fontSize=10, textColor=SLATE, spaceAfter=12)
h2   = H(fontName='Helvetica-Bold', fontSize=13, textColor=BLACK, spaceBefore=13, spaceAfter=5)
body = H(fontName='Helvetica', fontSize=9.5, textColor=BLACK, leading=14)
small= H(fontName='Helvetica', fontSize=8, textColor=SLATE, leading=11)
hdr  = H(fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.white, leading=12)

class Header(Flowable):
    def __init__(self, w): self.w, self.height = w, 26
    def wrap(self, *a): return (self.w, self.height)
    def draw(self):
        c = self.canv
        for i, (rad, op) in enumerate(((2.2, 0.30), (3.2, 0.55), (4.2, 1.0))):
            c.setFillColor(YELLOW); c.setFillAlpha(op)
            c.circle(5, 20 - i*7, rad, stroke=0, fill=1)
        c.setFillAlpha(1); c.setFillColor(BLACK); c.setFont('Helvetica-Bold', 20)
        c.drawString(18, 4, 'Lopos')

def kpi_row():
    cells = []
    for g, d in zip(groups, delta):
        dd = Drawing(95, 46)
        dd.add(String(2, 26, d, fontName='Helvetica-Bold', fontSize=19, fillColor=BLACK))
        dd.add(String(2, 8, g.upper() + ' positions / tag', fontName='Helvetica', fontSize=7, fillColor=SLATE))
        cells.append(dd)
    dt = Drawing(120, 46)
    dt.add(Rect(0, 0, 120, 46, fillColor=YELLOW, strokeColor=None))
    dt.add(String(8, 26, TOT_D, fontName='Helvetica-Bold', fontSize=22, fillColor=BLACK))
    dt.add(String(8, 8, 'TOTAL positions vs baseline', fontName='Helvetica', fontSize=7, fillColor=BLACK))
    t = Table([[*cells, dt]], colWidths=[33*mm, 33*mm, 33*mm, 33*mm, 0])
    t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('LEFTPADDING',(0,0),(-1,-1),0),
                           ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    return t

def fitted(png, w):
    iw, ih = ImageReader(png).getSize()
    return Image(png, width=w, height=w*ih/iw)

doc = SimpleDocTemplate(os.path.join(HERE, 'lopos_w2w_report.pdf'), pagesize=A4,
                        leftMargin=18*mm, rightMargin=18*mm, topMargin=15*mm, bottomMargin=15*mm)
E = [Header(170*mm), Spacer(1, 6)]
E.append(Paragraph('More animal positions through dense vegetation', disp))
E.append(Paragraph('LoPoS tracking system &nbsp;&middot;&nbsp; week-over-week field result &nbsp;&middot;&nbsp; 2026-06-11', sub))

# ---- the setting ----
E.append(Paragraph('The setting', h2))
E.append(Paragraph(
    'This system locates free-ranging animals in a natural, <b>vegetated environment</b>. Dense '
    'vegetation &mdash; plants, trees and canopy &mdash; is the main obstacle for the radio links: '
    'foliage absorbs and scatters the signals and repeatedly breaks the line-of-sight between the '
    'animal-borne tags and the receivers, and it keeps changing as plants grow and move. Everything '
    'below is about getting more reliable positions through that vegetation.', body))

# ---- how it works ----
E.append(Paragraph('How the system works', h2))
E.append(ListFlowable([ListItem(Paragraph(x, body), leftIndent=8, value='▪') for x in [
    'A <b>base station (the &ldquo;sink&rdquo;)</b> coordinates everything over a long-range, low-frequency '
    'radio link: it tells each device when to act and collects all their reports.',
    '<b>Anchors</b> are fixed reference stations. Within each cell the central anchor keeps the others '
    'time-synchronised over ultra-wideband (UWB) radio; together they listen for the brief pulses sent by tags.',
    '<b>Tags</b> are carried by the animals and run on small batteries. A tag simply emits one UWB pulse '
    'in its assigned time slot. Its position is found from the tiny differences in <i>when</i> that single '
    'pulse reaches the surrounding anchors. A group of anchors that hears a tag together is a <b>cell</b>.']],
    bulletType='bullet'))

E.append(Paragraph('Headline', h2))
E.append(kpi_row())
E.append(Paragraph('&ldquo;Positions per tag&rdquo; = successful localizations per animal per minute. '
                   'Higher is better; every group improved.', small))

# ---- periods ----
E.append(Paragraph('What we compared', h2))
per = [[Paragraph('Window', hdr), Paragraph('Dates (local)', hdr), Paragraph('System state', hdr)],
       [Paragraph('Baseline', body), Paragraph('Sat 30 May 11:00 &rarr; Sun 31 May ~12:00', body),
        Paragraph('Earlier system &mdash; original cell layout, simpler scheduling', body)],
       [Paragraph('Current', body), Paragraph('Wed 10 Jun 11:00 &rarr; Thu 11 Jun ~12:00', body),
        Paragraph('After the rebuilt cell network + improved scheduling went live', body)]]
t = Table(per, colWidths=[24*mm, 64*mm, 86*mm])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLACK), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
    ('LINEBELOW',(0,0),(-1,-1),0.5,LINE), ('VALIGN',(0,0),(-1,-1),'TOP'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, ROW]),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
E.append(t)
E.append(Paragraph('Matched ~25-hour windows (same start clock, same season, same animals &mdash; ~17 active '
                   'tags per group). A &ldquo;group&rdquo; is one of the four zones of the study area.', small))

# ---- results ----
E.append(Paragraph('Result, by zone', h2))
rows = [['Zone', 'Baseline positions', 'Current positions', 'Per-tag rate', 'Change']]
for i, g in enumerate(groups):
    rows.append([g, f'{fixes_b[i]:,}', f'{fixes_a[i]:,}', f'{base[i]:.2f} → {now[i]:.2f}', '▲ '+delta[i]])
rows.append(['TOTAL', f'{TOT_B:,}', f'{TOT_A:,}', '', '▲ '+TOT_D])
rt = Table(rows, colWidths=[20*mm, 34*mm, 34*mm, 40*mm, 22*mm])
rt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLACK), ('TEXTCOLOR',(0,0),(-1,0),colors.white),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'), ('FONTSIZE',(0,0),(-1,-1),9), ('ALIGN',(1,0),(-1,-1),'CENTER'),
    ('ROWBACKGROUNDS',(0,1),(-1,-2),[colors.white, ROW]), ('LINEBELOW',(0,0),(-1,-1),0.5,LINE),
    ('BACKGROUND',(0,-1),(-1,-1),GREY), ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),
    ('FONTNAME',(4,1),(4,-1),'Helvetica-Bold'), ('TEXTCOLOR',(4,1),(4,-1),BLACK),
    ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
E.append(rt)

d = Drawing(440, 165)
bc = VerticalBarChart(); bc.x, bc.y, bc.width, bc.height = 30, 22, 300, 124
bc.data = [base, now]; bc.categoryAxis.categoryNames = groups
bc.valueAxis.valueMin, bc.valueAxis.valueMax, bc.valueAxis.valueStep = 0, 0.5, 0.1
bc.barWidth = 8; bc.groupSpacing = 16
bc.bars[0].fillColor = SLATE; bc.bars[1].fillColor = YELLOW; bc.bars.strokeColor = None
bc.valueAxis.strokeColor = LINE; bc.categoryAxis.strokeColor = LINE
bc.valueAxis.gridStrokeColor = LINE; bc.valueAxis.gridStrokeWidth = 0.5; bc.valueAxis.visibleGrid = 1
d.add(bc)
d.add(Rect(345, 130, 8, 8, fillColor=SLATE, strokeColor=None)); d.add(String(357, 130, 'Baseline (30 May)', fontName='Helvetica', fontSize=8, fillColor=BLACK))
d.add(Rect(345, 114, 8, 8, fillColor=YELLOW, strokeColor=None)); d.add(String(357, 114, 'Current', fontName='Helvetica', fontSize=8, fillColor=BLACK))
E.append(Spacer(1, 4)); E.append(d)
E.append(Paragraph('Positions per tag per minute, by zone.', small))

# ---- cell network ----
maps = Table([[Paragraph('Cell network &mdash; to 30 May', body), Paragraph('Cell network &mdash; now', body)],
              [fitted(os.path.join(HERE, 'cells_before.png'), 86*mm), fitted(os.path.join(HERE, 'cells_after.png'), 86*mm)]],
             colWidths=[87*mm, 87*mm])
maps.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0), ('RIGHTPADDING',(0,0),(-1,-1),0),
                          ('TOPPADDING',(0,0),(-1,-1),0), ('BOTTOMPADDING',(0,0),(-1,-1),2), ('VALIGN',(0,0),(-1,-1),'TOP')]))
E.append(KeepTogether([
    Paragraph('A rebuilt receiver network', h2),
    Paragraph('We re-derived the cells from <b>measured</b> radio reception. '
              'Each animal is now covered by more, better-placed reference anchors. Green lines mark strong, '
              'reliable links between anchors.', body),
    maps,
    Paragraph('Dots = anchors; stars = the central anchor of each cell; shaded areas = the ground each cell '
              'covers &mdash; covering more of the study area, with no idle, unused cells left over.', small)]))

# ---- what we changed ----
E.append(Paragraph('What we changed, and why it helps in vegetation', h2))
E.append(ListFlowable([ListItem(Paragraph(x, body), leftIndent=8, value='▪') for x in [
    '<b>Rebuilt the cell network from real reception.</b> More anchors now hear each animal together, so a '
    'position can still be computed when foliage blocks some of the links &mdash; better coverage where the '
    'vegetation is densest.',
    '<b>A moving measurement window.</b> Because vegetation can block the scheduling messages, a tag sometimes '
    'acts on out-of-date instructions and transmits when the anchors are not listening for it. By letting the '
    'measurement window drift through the cycle, such a stray transmission now falls on quiet time instead of '
    'spoiling a live measurement &mdash; fewer wasted attempts.',
    '<b>Smarter, location-aware scheduling.</b> Each animal is measured in the cell nearest to where it '
    'actually is, instead of cycling blindly through all cells &mdash; more of every transmission turns into a '
    'usable position.',
    '<b>Transmissions matched to need.</b> Tags now transmit at their planned rate rather than over-transmitting, '
    'so the gains above come <i>without</i> extra radio traffic &mdash; extending tag battery life and study duration.']],
    bulletType='bullet'))
E.append(Spacer(1, 4))
E.append(Paragraph('Net effect: the system delivers more reliable animal positions through dense vegetation, '
                   'while transmitting no more often than before. Every zone improved; the hardest-to-cover '
                   'zones (grp2, grp3) improved most.', small))

# ---- Ilvo project work delivered ----
E.append(KeepTogether([
    Paragraph('Project work delivered', h2),
    ListFlowable([ListItem(Paragraph(x, body), leftIndent=8, value='▪') for x in [
        '<b>Code consolidation.</b> Recent improvements from the Wish deployment were integrated into the '
        'Ilvo code tree and merged into a single shared repository (support context).',
        '<b>Weekly data archiving.</b> Data is archived weekly, so each run processes only records that are at '
        'least one week old. Restricting the logic to a single weekly data set minimises the volume evaluated per '
        'run, keeping performance and scalability stable as the overall data volume grows.',
        '<b>Cell-network analysis.</b> Current and newly proposed cells were analysed from measured reception. '
        'Coverage improved from <b>20 cells / 68%</b> to <b>13 cells / 82%</b>.',
        '<b>Roaming cell selection.</b> Tag-to-cell assignment moved from round-robin to <b>roaming</b> &mdash; '
        'each animal is measured in the cell nearest its recent position.',
        '<b>Field follow-up.</b> Data follow-up runs <b>3 June &ndash; 13 July</b>.']],
        bulletType='bullet'),
    Paragraph('Cell analysis (current vs proposed): '
              '<link href="https://drive.google.com/drive/folders/14fUezDfRjrZ3RMO-GMcRQNRdSmjYQQh_">'
              '<font color="#1A1A1A"><u>shared Google Drive folder</u></font></link>', small)]))

doc.build(E)
print('wrote lopos_w2w_report.pdf')
