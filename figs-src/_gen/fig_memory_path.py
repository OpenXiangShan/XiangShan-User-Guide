"""memory-path: matrix memory access path from CUTE through HBL2 to memory.

Sources: docs/zh/hardware/memory.md 20-75 (dedicated matrix read path,
512 b per bank; M channel; DefaultMatrixConfig 1 MiB / 8 banks; AML / BML /
CML go through LocalMMU and CUTE2TL; LocalMMU is the only data-plane port,
io.mmu2llc; outsideDataWidth typically 512 b); XSAI/src/main/scala/
xiangshan/XSTile.scala 270-306 (l2top.io.matrixDataOut512L2, Vec(L2NBanks),
zipped 1:1 onto cute.io.matrix_data_in when the channel counts match);
LLC attached over CHI (io.chi).
"""
from dsl import *

f = Fig('memory-path')

TT = 34
PAD = 20
BANK_H, BANK_G, NB = 22, 8, 8
Y_TOP = TT + 10                       # first module row inside the panels
Y_BANK = Y_TOP + 56                   # first bank strip
bank_y = [Y_BANK + i * (BANK_H + BANK_G) for i in range(NB)]
Y_BOT = bank_y[-1] + BANK_H
PANEL_H = Y_BOT + PAD

LD_W, MMU_W, TL_W = 120, 110, 110
COL_G = 76
cute_w = PAD + LD_W + COL_G + MMU_W + COL_G + TL_W + PAD
GAP = 230                              # CUTE -> HBL2 gap (hosts the two paths)
hx = cute_w + GAP
HW = 300

# ---------------------------------------------------------------- CUTE
f.group(0, 0, cute_w, PANEL_H, 'CUTE matrix unit', kind='panel', dashed=False, fs=FS_GROUP)
lx = PAD
mx = lx + LD_W + COL_G
tx = mx + MMU_W + COL_G
mod_h = Y_BOT - Y_TOP
f.box(mx, Y_TOP, MMU_W, mod_h, 'LocalMMU', 'TLB,\nrequest\narbitration', kind='compute')
f.box(tx, Y_TOP, TL_W, mod_h, 'CUTE2TL', 'TileLink\nclient', kind='compute')
loaders = [('AML', 'A matrix'), ('BML', 'B matrix'), ('CML', 'C load / store')]
LH = 48
lg = (mod_h - 3 * LH) / 4
for i, (t, sub) in enumerate(loaders):
    ly = Y_TOP + lg + i * (LH + lg)
    f.box(lx, ly, LD_W, LH, t, sub, kind='compute')
    f.line([(lx + LD_W, ly + LH / 2), (mx, ly + LH / 2)], arrow='both')
ymid = Y_TOP + mod_h / 2
f.line([(mx + MMU_W, ymid), (tx, ymid)], arrow='both')
f.note(mx + MMU_W + COL_G / 2, ymid - 22, 'io.mmu2llc', align='center')
f.note(mx + MMU_W + COL_G / 2, ymid + 14, '512 b', align='center')

# ---------------------------------------------------------------- HBL2
f.group(hx, 0, HW, PANEL_H, 'HBL2  (1 MiB, 8 banks)', kind='panel', dashed=False, fs=FS_GROUP)
mp = (hx + PAD, Y_TOP, HW - 2 * PAD, 40)
f.box(*mp, 'Request pipeline / MSHR', kind='storage')
for i, by in enumerate(bank_y):
    f.box(hx + PAD, by, HW - 2 * PAD, BANK_H, f'data bank {i}', kind='storage', fs=FS_PIN)

# request path (TileLink A) and dedicated read path (M channel)
ry = Y_TOP + 20
f.line([(tx + TL_W, ry), (mp[0], ry)])
f.note(tx + TL_W + GAP / 2, ry - 12, 'A: matrix Get / Put', align='center')
RED = PAL['new'][1]
for by in bank_y:
    f.line([(hx + PAD, by + BANK_H / 2), (tx + TL_W, by + BANK_H / 2)], sw=W_DATA, color=RED, size=6)
lab_y = (ry + bank_y[0]) / 2 + 2
f.note(tx + TL_W + GAP / 2, lab_y, 'M: matrix read return, 8 x 512 b', align='center', color=RED)

# ---------------------------------------------------------------- scalar core, LLC, DDR
CORE_W = 150
cx = hx + HW + 80
f.box(cx, mp[1], CORE_W, mp[3], 'Scalar core', 'L1 I / D', kind='neutral')
f.line([(cx, mp[1] + mp[3] / 2), (mp[0] + mp[2], mp[1] + mp[3] / 2)], arrow='both')
f.note(cx - 40, mp[1] + mp[3] / 2 - 12, 'TileLink', align='center')

RH = 44
y_llc = bank_y[3] + BANK_H / 2 - RH / 2 + (BANK_H + BANK_G) / 2
y_ddr = Y_BOT - RH
f.box(cx, y_llc, CORE_W, RH, 'External LLC', kind='storage')
f.box(cx, y_ddr, CORE_W, RH, 'Memory (DDR)', kind='storage')
f.line([(hx + HW, y_llc + RH / 2), (cx, y_llc + RH / 2)], arrow='both')
f.note(hx + HW + 40, y_llc + RH / 2 - 12, 'CHI', align='center')
f.line([(cx + CORE_W / 2, y_llc + RH), (cx + CORE_W / 2, y_ddr)], arrow='both')

# ---------------------------------------------------------------- legend
ly = PANEL_H + 24
x = f.legend_line(0, ly, 'shared request / data path')
f.legend_line(x + 30, ly, 'dedicated matrix read path, one per bank')
f.cells[-2] = f.cells[-2].replace(f'strokeColor={INK}', f'strokeColor={RED}')

f.save()
