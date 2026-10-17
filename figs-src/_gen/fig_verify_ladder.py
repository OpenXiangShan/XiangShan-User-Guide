"""verify-ladder: QEMU -> NEMU -> gem5 -> RTL simulation -> board.

Source: docs/zh/software/simulators.md 30-38 (division-of-labour table: tool,
speed, check scope, use case) and 19 (QEMU conclusions are arithmetic-only,
must be re-checked on board). Staircase after the FERIVer Fig5 row-per-method
layout. Speeds are the table's qualitative words only -- the text gives no
numbers, and board-level measurement is "near real-time", so speed is NOT drawn
as monotonic.
"""
from dsl import *

f = Fig('verify-ladder')

AX_W = 60          # fidelity arrow column
STEP = 70          # staircase offset per rung
BW = 270
BH = 46
RG = 14
N = 5
RUNGS = [   # bottom -> top
    ('QEMU (user mode)', 'arithmetic only', 'fastest', 'single op / network iteration', 'neutral'),
    ('NEMU', 'ISA semantics + register state', 'fast', 'difftest reference model', 'neutral'),
    ('gem5', 'performance magnitude', 'medium', 'architecture exploration', 'neutral'),
    ('Verilator / VCS', 'full function', 'slow', 'pre-commit re-check, waveforms', 'compute'),
    ('Board-level measurement', 'full function, final verdict', 'near real-time', 'final conclusions', 'compute'),
]
x_bar0 = AX_W
x_tab = x_bar0 + (N - 1) * STEP + BW + 40
SPD_W, USE_W = 120, 230
y_hdr = 0
y0 = y_hdr + 30
ry = lambda r: y0 + (N - 1 - r) * (BH + RG)

f.text(x_bar0, y_hdr, 200, 20, 'tool and check scope', FS_SUB, bold=True, align='left')
f.text(x_tab, y_hdr, SPD_W, 20, 'speed', FS_SUB, bold=True, align='left')
f.text(x_tab + SPD_W, y_hdr, USE_W, 20, 'used for', FS_SUB, bold=True, align='left')
for r, (tool, scope, spd, use, kind) in enumerate(RUNGS):
    y = ry(r)
    x = x_bar0 + r * STEP
    f.box(x, y, BW, BH, tool, scope, kind=kind, bold=True, sub_fs=FS_PIN)
    # dotted leader from bar to the table columns
    f.line([(x + BW + 6, y + BH / 2), (x_tab - 8, y + BH / 2)], arrow='none', sw=W_STRUCT, dashed=True,
           color='#C0C0C0')
    f.text(x_tab, y, SPD_W, BH, spd, FS_SUB, align='left')
    f.text(x_tab + SPD_W, y, USE_W, BH, use, FS_SUB, align='left')

# RTL boundary between gem5 and Verilator
yb = ry(3) + BH + RG / 2
f.line([(x_bar0, yb), (x_tab + SPD_W + USE_W, yb)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)
f.note(x_bar0 + 4, yb - 10, 'RTL-based', italic=True)
f.note(x_bar0 + 4, yb + 10, 'software models', italic=True)

# fidelity arrow
ya, yz = ry(0) + BH, ry(N - 1)
f.line([(AX_W / 2, ya), (AX_W / 2, yz)], sw=W_DATA, size=8)
f.note(AX_W / 2 - 10, (ya + yz) / 2, 'fidelity (closer to silicon)', vertical=True, align='center', italic=True)

# legend + caveat
ly = ry(0) + BH + 30
x = f.legend(x_bar0, ly, [('neutral', 'model (no RTL)'), ('compute', 'executes the RTL')])
f.note(x + 30, ly + 6, 'QEMU passing does not imply hardware-correct: re-check on real hardware', italic=True)

f.save()
