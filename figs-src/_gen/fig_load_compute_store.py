"""load-compute-store: three-stage CUTE pipeline over two MatrixReg sets.

Source: docs/zh/hardware/microarchitecture.md 28-42 (Load: MemoryLoader via
LocalMMU / CUTE2TL into AB / C MatrixReg; Compute: DataController reads per
bank into MatrixTE; Store: CMemoryLoader writes back; two MatrixReg sets
alternate so the next tile's load overlaps the current tile's compute;
AB MatrixReg 8 KiB / 8 banks, C MatrixReg 64 KiB / 8 banks).
Timeline layout after AME-PIM Fig5 (time runs left to right).
"""
from dsl import *

f = Fig('load-compute-store')

LBL_W = 110          # left label column (shared by both panels)
COL_W = 220
COL_GAP = 60
BH = 52
VG = 46
STAGES = ['Load', 'Compute', 'Store']
W = 3 * COL_W + 2 * COL_GAP
x0 = LBL_W
colx = [x0 + i * (COL_W + COL_GAP) for i in range(3)]
PAD = 20

# ------------------------------------------------------------ (a) structure
pa_y = 0
f.text(0, pa_y, 300, 20, '(a) Datapath', FS_GROUP, bold=True, align='left')
y_mem = pa_y + 34
f.box(x0, y_mem, W, 40, 'L2 / LLC / DDR', 'through LocalMMU and CUTE2TL', kind='neutral')
y_stage = y_mem + 40 + VG
units = [('MemoryLoader', 'AML / BML / CML'), ('MatrixTE', 'fed by DataController'),
         ('CMemoryLoader', 'C write-back')]
for i, (t, sub) in enumerate(units):
    f.text(colx[i], y_stage - 22, COL_W, 18, STAGES[i], FS_MAIN, bold=True)
    f.box(colx[i], y_stage, COL_W, BH, t, sub, kind='compute')
y_reg = y_stage + BH + VG
SET_H = 34
reg_h = 30 + 2 * SET_H + 10 + 12
f.group(x0, y_reg, W, reg_h, 'MatrixReg, double-buffered', kind='storage', dashed=False, fs=FS_MAIN, pad=10)
ab_w = 150
for k in range(2):
    sy = y_reg + 30 + k * (SET_H + 10)
    f.text(x0 + 12, sy, 60, SET_H, f'set {k}', FS_SUB, align='left')
    f.box(x0 + 70, sy, ab_w, SET_H, 'AB  8 KiB, 8 banks', kind='plain', fs=FS_SUB)
    f.box(x0 + 70 + ab_w, sy, W - 70 - ab_w - 12, SET_H, 'C  64 KiB, 8 banks', kind='plain', fs=FS_SUB)

mx = lambda i: colx[i] + COL_W / 2 + (60 if i != 1 else 0)
# Load: memory -> loader -> MatrixReg
f.line([(mx(0), y_mem + 40), (mx(0), y_stage)])
f.line([(mx(0), y_stage + BH), (mx(0), y_reg)])
f.note(mx(0) + 8, y_stage + BH + VG / 2, 'write A, B, C', align='left')
# Compute: MatrixReg <-> MatrixTE (operands up, C accumulate down)
f.line([(mx(1) - 20, y_reg), (mx(1) - 20, y_stage + BH)])
f.line([(mx(1) + 20, y_stage + BH), (mx(1) + 20, y_reg)])
f.note(mx(1) - 28, y_stage + BH + VG / 2, 'A, B, C per bank', align='right')
f.note(mx(1) + 28, y_stage + BH + VG / 2, 'C acc.', align='left')
# Store: MatrixReg -> CMemoryLoader -> memory
f.line([(mx(2), y_reg), (mx(2), y_stage + BH)])
f.line([(mx(2), y_stage), (mx(2), y_mem + 40)])
f.note(mx(2) + 8, y_stage + BH + VG / 2, 'read C', align='left')
pa_bot = y_reg + reg_h

# ------------------------------------------------------------ (b) timeline
pb_y = pa_bot + 50
f.text(0, pb_y, 300, 20, '(b) Overlap in time', FS_GROUP, bold=True, align='left')
NS = 7
slot = W / NS
RH = 34
RG = 12
ty0 = pb_y + 34
# (stage, slot, tile) -- tile t uses set t % 2; a set is reused only after its Store
sched = [(0, 0, 0), (1, 1, 0), (2, 2, 0),
         (0, 1, 1), (1, 2, 1), (2, 3, 1),
         (0, 3, 2), (1, 4, 2), (2, 5, 2),
         (0, 4, 3), (1, 5, 3), (2, 6, 3)]
for r, st in enumerate(STAGES):
    ry = ty0 + r * (RH + RG)
    f.text(0, ry, LBL_W - 14, RH, st, FS_MAIN, bold=True, align='right')
    f.line([(x0, ry + RH / 2), (x0 + W, ry + RH / 2)], arrow='none', sw=W_STRUCT, color='#D0D0D0')
SET_FILL = ['#DAE8F4', '#FFFFFF']
for st, s, t in sched:
    ry = ty0 + st * (RH + RG)
    f.box(x0 + s * slot + 3, ry, slot - 6, RH, f'tile {t}', kind='plain', fill=SET_FILL[t % 2],
          stroke=PAL['compute'][1], fs=FS_SUB)
# set reuse: tile 2 may load into set 0 only after tile 0 has been stored
rs = ty0 + 2 * (RH + RG)
dx = x0 + 3 * slot
f.line([(dx, rs), (dx, ty0 + RH)], sw=W_STRUCT, dashed=True, open_arrow=True)
f.note(dx + 10, ty0 + RH + RG + RH / 2, 'set 0 released', align='left', italic=True)
# slot grid ticks and time axis
ax_y = ty0 + 3 * (RH + RG) + 6
for s in range(NS + 1):
    if s == 3:
        continue
    f.line([(x0 + s * slot, ty0 - 6), (x0 + s * slot, ax_y)], arrow='none', sw=W_STRUCT, dashed=True,
           color='#D0D0D0')
f.line([(x0, ax_y), (x0 + W + 20, ax_y)], sw=W_STRUCT, size=6)
f.note(x0 + W + 26, ax_y, 'time', italic=True)
for s in range(NS):
    f.note(x0 + (s + 0.5) * slot, ax_y + 12, f't{s}', align='center')

# legend
ly = ax_y + 34
end = f.legend(x0, ly, [('plain', 'tile in MatrixReg set 0'), ('plain', 'tile in MatrixReg set 1')])
f.cells[-4] = f.cells[-4].replace('fillColor=#FFFFFF;strokeColor=#333333', 'fillColor=#DAE8F4;strokeColor=#3D6E9E')
f.cells[-2] = f.cells[-2].replace('strokeColor=#333333', 'strokeColor=#3D6E9E')

f.save()
