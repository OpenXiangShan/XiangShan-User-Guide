"""hpm-flow: hardware performance monitor data flow.

Sources: docs/zh/hardware/pmu.md 30-46 (events defined in sub-modules,
packed by generatePerfEvent into io_perf of Frontend / Backend / MemBlock /
CoupledL2; each of the first three hosts a PFEvent copy of mhpmevent and an
HPerfMonitor that computes counter increments; CSR accumulates into
mhpmcounter3-31; CoupledL2 events go straight to an HPerfMonitor inside the
CSR); pmu.md 20-26 (overflow -> LCOFI, interrupt 13); pmu.md event-pool table.
RTL: XSAI NewCSR.scala ~1306-1320 ("frontend 8, ctrlblock 8, memblock 8,
cache 5"; csrevents = mhpmevents.slice(24, 29) -> mhpmevent27-31).
"""
from dsl import *

f = Fig('hpm-flow')

N = 4
COL_W = 210
COL_G = 36
PAD = 16
SUB_H = 30
MOD_TT = 30
SUB_G = 10
W = N * COL_W + (N - 1) * COL_G
colx = [i * (COL_W + COL_G) for i in range(N)]
mods = [('Frontend', 'mhpmevent3-10'), ('Backend', 'mhpmevent11-18'),
        ('MemBlock', 'mhpmevent19-26'), ('CoupledL2', 'mhpmevent27-31')]

y_mod = 0
VG_IN = 30
mod_h = MOD_TT + 2 * SUB_H + VG_IN + PAD
iw = COL_W - 2 * PAD
hw = (iw - 10) / 2
for i, (name, _) in enumerate(mods):
    x = colx[i]
    f.group(x, y_mod, COL_W, mod_h, name, kind='panel', dashed=False, fs=FS_MAIN, pad=10)
    sy = y_mod + MOD_TT
    if i < 3:
        f.box(x + PAD, sy, hw, SUB_H, 'events', kind='neutral', fs=FS_SUB)
        f.box(x + PAD + hw + 10, sy, hw, SUB_H, 'PFEvent', kind='control', fs=FS_SUB)
        f.box(x + PAD, sy + SUB_H + VG_IN, iw, SUB_H, 'HPerfMonitor', kind='compute', fs=FS_SUB)
        f.line([(x + PAD + hw / 2, sy + SUB_H), (x + PAD + hw / 2, sy + SUB_H + VG_IN)], sw=W_STRUCT, size=5)
        px = x + PAD + hw + 10 + hw / 2
        f.line([(px, sy + SUB_H), (px, sy + SUB_H + VG_IN)], sw=W_STRUCT, dashed=True, open_arrow=True, size=5)
    else:
        f.box(x + PAD, sy, hw, SUB_H, 'events', kind='neutral', fs=FS_SUB)
ev_y = y_mod + MOD_TT + SUB_H / 2

# CSR block
GAP = 70
y_csr = y_mod + mod_h + GAP
CSR_TT = 30
csr_h = CSR_TT + SUB_H + 24 + 44 + 24 + PAD
f.group(0, y_csr, W, csr_h, 'CSR', kind='panel', dashed=False, fs=FS_MAIN, pad=10)
hx = colx[3] + PAD
f.box(hx, y_csr + CSR_TT, iw, SUB_H, 'HPerfMonitor', kind='compute', fs=FS_SUB)
ctr_y = y_csr + CSR_TT + SUB_H + 24
ranges = ['mhpmcounter3-10', 'mhpmcounter11-18', 'mhpmcounter19-26', 'mhpmcounter27-31']
for i, r in enumerate(ranges):
    f.box(colx[i] + PAD, ctr_y, iw, 44, r, 'accumulate increments', kind='control', fs=FS_SUB, sub_fs=FS_PIN)

# flows
for i in range(3):
    x = colx[i] + COL_W / 2
    f.line([(x, y_mod + mod_h - PAD), (x, ctr_y)])
    f.note(x + 8, y_mod + mod_h + GAP / 2, 'increments', align='left')
xl2 = colx[3] + PAD + hw / 2
f.line([(xl2, y_mod + MOD_TT + SUB_H), (xl2, y_csr + CSR_TT)])
f.note(xl2 + 8, y_mod + mod_h + GAP / 2, 'raw events', align='left')
f.note(xl2 + 14, y_mod + MOD_TT + SUB_H + VG_IN + SUB_H / 2, 'no local\nmonitor', align='left', italic=True)
f.line([(xl2, y_csr + CSR_TT + SUB_H), (xl2, ctr_y)], size=6)

# event selectors written by software (mhpmevent) -> PFEvent copies: implicit; label left
f.note(-14, ev_y, 'io_perf\n(generatePerfEvent)', align='right', italic=True)

# overflow interrupt
oy = ctr_y + 44 + 14
for i in range(N):
    f.line([(colx[i] + COL_W / 2, ctr_y + 44), (colx[i] + COL_W / 2, oy)], arrow='none', sw=W_STRUCT)
f.line([(colx[0] + COL_W / 2, oy), (W + 70, oy)], sw=W_STRUCT)
f.note(W + 76, oy, 'overflow interrupt\nLCOFI (irq 13)', align='left')

# legend
ly = y_csr + csr_h + 22
x = f.legend_line(0, ly, 'event / increment data')
f.legend_line(x + 30, ly, 'event selector (mhpmevent)', sw=W_STRUCT, dashed=True, open_arrow=True)

f.save()
