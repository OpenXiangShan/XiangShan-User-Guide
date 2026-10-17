"""kmh-multicore: multi-core block diagram (core subsystem x N + multicore subsystem).

Source: docs/zh/processor.md 14-16 (core subsystem unit list), 18-21 (IFU
32 B / cycle, ICache, FDIP, BPU), 23-26 (6-wide decode, fusion), 28-31
(rename, ROB compression, move elimination), 33-37 (dispatch / issue,
regfile read after issue), 39-52 (Int / FP / Vec units), 54-59 (3 ld + 2 st
+ 2 vec issue, DCache), 61-65 (ROB, RAB, 8 retire / cycle), 67-72 (MMU Sv39 /
Sv48, H, Sv39x4 / Sv48x4, PBMT), 74-83 (PMP / PMA 16 + 16, 4 KB), 85-92 (L2
1 MB, 8-way, 4 banks, inclusive, CHI Issue B / E.b), 94-118 (multicore
subsystem: IMSIC M + S + 5 VS, CLINT, timer broadcast, JTAG debug).
External port protocols (TL / AXI4 MMIO, TL / AXI4-Lite IMSIC) follow the
previous figure. Per FIG-GUIDE 6.12 only the main components are kept.
"""
from dsl import *

f = Fig('kmh-multicore')

W = 980
PAD = 20
IW = W - 2 * PAD
G = 30
TT = 44

# ---------------------------------------------------------------- core tile (x N)
yA = TT
hA = 64
y_bus = yA + hA + 22
yB = yA + hA + 44
hB = 84
yC = yB + hB + 26
hC = 64
yD = yC + hC + 26
hD = 52
TILE_H = yD + hD + PAD

for k in (2, 1):
    f.rect(k * 10, -k * 10, W, TILE_H, 'panel')
f.group(0, 0, W, TILE_H, 'Core subsystem', kind='panel', dashed=False, fs=FS_GROUP, pad=12)
f.note(W - 12, 20, 'x N cores', align='right', italic=True)

wa = (IW - 4 * G) / 5
A = [('BPU', 'branch prediction'), ('IFU', '32 B / cycle\nICache, FDIP'), ('IDU', '6 / cycle, fusion'),
     ('Rename', 'move elim.\nROB compression'), ('Dispatch / Issue', 'regfile read\nafter issue')]
ax = [PAD + i * (wa + G) for i in range(5)]
for x, (t, s) in zip(ax, A):
    f.box(x, yA, wa, hA, t, s, kind='control', sub_fs=FS_PIN)
for i in range(4):
    f.line([(ax[i] + wa, yA + hA / 2), (ax[i + 1], yA + hA / 2)], size=6)

wb = (IW - 3 * G) / 4
B = [('IntExu', 'ALU, MUL, DIV,\nBJU, CSR', 'compute'), ('FPExu', 'FALU, FMA,\nFDIV, FCVT', 'compute'),
     ('VecExu', 'int / FP ALU, FMA,\nFP, CVT', 'compute'), ('LSU', '3 ld + 2 st + 2 vec\nDCache, prefetch', 'storage')]
bx = [PAD + i * (wb + G) for i in range(4)]
for x, (t, s, k) in zip(bx, B):
    f.box(x, yB, wb, hB, t, s, kind=k, sub_fs=FS_PIN)
# issue bus: dispatch -> every execution block
dx = ax[4] + wa / 2
f.line([(dx, yA + hA), (dx, y_bus)], arrow='none')
f.line([(bx[0] + wb / 2, y_bus), (dx, y_bus)], arrow='none')
for x in bx:
    f.line([(x + wb / 2, y_bus), (x + wb / 2, yB)], size=6)
f.note(dx - 8, (yA + hA + y_bus) / 2, 'issue', align='right')

C = [('ROB', 'RAB, 8 retire / cycle', 'control'), ('MMU', 'Sv39 / Sv48, H ext., PBMT', 'storage'),
     ('PMP / PMA', '16 + 16 entries, 4 KB', 'neutral')]
for x, (t, s, k) in zip(bx, C):
    f.box(x, yC, wb, hC, t, s, kind=k, sub_fs=FS_PIN)
f.box(PAD, yD, IW, hD, 'L2 Cache', '1 MB, 8-way, 4 banks, inclusive', kind='storage', sub_fs=FS_PIN)
# L2 clients that sit directly above it
f.line([(bx[3] + wb / 2, yB + hB), (bx[3] + wb / 2, yD)], arrow='both', size=6)
f.line([(bx[1] + wb / 2, yC + hC), (bx[1] + wb / 2, yD)], arrow='both', size=6)
f.note(bx[3] + wb / 2 + 8, (yC + yC + hC) / 2, 'L1 miss', align='left')
f.note(bx[1] + wb / 2 + 8, yC + hC + 13, 'PTW', align='left')

# ---------------------------------------------------------------- multicore subsystem
GAP = 96
yM = TILE_H + GAP
MW = 700
HDR = 130
MH = 70 + 2 * PAD
f.rect(0, yM, MW, MH, 'panel')
f.text(12, yM, HDR - 12, MH, 'Multicore\nsubsystem\n(shared)', FS_GROUP, bold=True, align='left')
wm = (MW - HDR - PAD - 2 * G) / 3
M = [('IMSIC', 'M + S + 5 VS files'), ('CLINT', 'mtime, timer, IPI'), ('Debug', 'JTAG DTM + DM')]
mx = [HDR + i * (wm + G) for i in range(3)]
for x, (t, s) in zip(mx, M):
    f.box(x, yM + PAD, wm, 70, t, s, kind='neutral', sub_fs=FS_PIN)
sig = ['MSI', 'MTIP / MSIP, time', 'debug interrupt']
for x, s in zip(mx, sig):
    f.line([(x + wm / 2, yM + PAD), (x + wm / 2, TILE_H)], sw=W_STRUCT, dashed=True, open_arrow=True, size=6)
    f.note(x + wm / 2 + 8, TILE_H + GAP / 2, s, align='left')

# external ports
yP = yM + MH + 40
ports = ['TL / AXI4-Lite', 'MMIO, TL / AXI4', 'JTAG']
for x, s in zip(mx, ports):
    f.line([(x + wm / 2, yP), (x + wm / 2, yM + PAD + 70)], sw=W_STRUCT, size=6)
    f.note(x + wm / 2, yP + 10, s, align='center')

# ---------------------------------------------------------------- off-cluster memory system
ex = MW + 60
f.box(ex, yM, W - ex, MH, 'NoC / LLC / memory', 'outside the core cluster', kind='plain', dashed=True,
      sub_fs=FS_PIN)
cxl = ex + (W - ex) / 2
f.line([(cxl, yD + hD), (cxl, yM)], arrow='both')
f.note(cxl + 8, TILE_H + GAP / 2, 'CHI Issue B / E.b\n(clock / voltage\ncrossing)', align='left')

# legend
ly = yP + 40
x = f.legend(0, ly, [('control', 'pipeline control'), ('compute', 'execution'), ('storage', 'memory system'),
                     ('neutral', 'protection / shared devices')])
x = f.legend_line(x + 36, ly + 6, 'data')
f.legend_line(x + 30, ly + 6, 'interrupt / debug signal (to every core)', sw=W_STRUCT, dashed=True, open_arrow=True)
f.save()
