"""delta-overview: what XSAI adds on top of Kunminghu V2R2.

Sources: docs/zh/start/stack.md 23-27 (four additions: CUTE, matrix control
path, HBL2, external LLC support); docs/zh/hardware/microarchitecture.md
(AmuCtrlIO / amuRelease core interface); docs/zh/hardware/memory.md 15-25
(HBL2 = upgraded CoupledL2, dedicated matrix read path 512 b per bank).
"""
from dsl import *

PAD = 20             # panel inner padding
TITLE_H = 34         # space for the panel title
GAP_H = 64           # horizontal gap between columns
GAP_V = 40           # vertical gap between rows
CELL_W, CELL_H, CELL_GAP = 124, 40, 12
CORE_PAD = 14
CORE_TITLE = 26
CORE_W = 2 * CELL_W + CELL_GAP + 2 * CORE_PAD
CORE_H = CORE_TITLE + 2 * CELL_H + CELL_GAP + CORE_PAD
CTRL_W = 128
CUTE_W = 170
ROW_H = 44
PANEL_GAP = 50

f = Fig('delta-overview')


def core(x, y):
    f.group(x, y, CORE_W, CORE_H, 'Scalar core', kind='panel', dashed=False, fs=FS_MAIN)
    cells = ['Frontend', 'OoO backend', 'Vector unit', 'L1 I / D caches']
    for i, c in enumerate(cells):
        cx = x + CORE_PAD + (i % 2) * (CELL_W + CELL_GAP)
        cy = y + CORE_TITLE + (i // 2) * (CELL_H + CELL_GAP)
        f.box(cx, cy, CELL_W, CELL_H, c, kind='neutral', fs=FS_SUB)


y_core = TITLE_H
y_l2 = y_core + CORE_H + GAP_V
y_llc = y_l2 + ROW_H + GAP_V
y_mem = y_llc + ROW_H + GAP_V
panel_h = y_mem + ROW_H + PAD

# ---------------------------------------------------------------- (a) baseline
ax = 0
aw = CORE_W + 2 * PAD
f.group(ax, 0, aw, panel_h, '(a) Kunminghu V2R2', kind='group', dashed=True, fs=FS_GROUP)
core(ax + PAD, y_core)
f.box(ax + PAD, y_l2, CORE_W, ROW_H, 'L2 cache (CoupledL2)', kind='neutral')
f.box(ax + PAD, y_mem, CORE_W, ROW_H, 'Memory (DDR)', kind='neutral')
cxa = ax + PAD + CORE_W / 2
f.line([(cxa, y_core + CORE_H), (cxa, y_l2)])
f.line([(cxa, y_l2 + ROW_H), (cxa, y_mem)])
f.note(cxa + 10, y_llc + ROW_H / 2, 'no external LLC', italic=True)

# ---------------------------------------------------------------- (b) XSAI
bx = ax + aw + PANEL_GAP
inner = CORE_W + GAP_H + CTRL_W + GAP_H + CUTE_W
bw = inner + 2 * PAD
f.group(bx, 0, bw, panel_h, '(b) XSAI', kind='group', dashed=True, fs=FS_GROUP)
x0 = bx + PAD
core(x0, y_core)
x_ctrl = x0 + CORE_W + GAP_H
x_cute = x_ctrl + CTRL_W + GAP_H
f.box(x_ctrl, y_core, CTRL_W, CORE_H, 'Matrix\ncontrol path', 'AmuCtrlIO\namuRelease', kind='new',
      italic_sub=False)
f.box(x_cute, y_core, CUTE_W, CORE_H, 'Matrix unit\n(CUTE)', 'Load / Compute / Store', kind='new')
f.box(x0, y_l2, inner, ROW_H, 'High-bandwidth L2 (HBL2)', 'upgraded from CoupledL2', kind='new')
f.box(x0, y_llc, inner, ROW_H, 'External last-level cache (LLC)', kind='new')
f.box(x0, y_mem, inner, ROW_H, 'Memory (DDR)', kind='neutral')

# core <-> control path <-> CUTE (control: 1px dashed, open arrows)
ya, yb = y_core + CORE_H / 2 - 16, y_core + CORE_H / 2 + 16
f.line([(x0 + CORE_W, ya), (x_ctrl, ya)], sw=W_STRUCT, dashed=True, open_arrow=True)
f.line([(x_ctrl, yb), (x0 + CORE_W, yb)], sw=W_STRUCT, dashed=True, open_arrow=True)
f.line([(x_ctrl + CTRL_W, ya), (x_cute, ya)], sw=W_STRUCT, dashed=True, open_arrow=True)
f.line([(x_cute, yb), (x_ctrl + CTRL_W, yb)], sw=W_STRUCT, dashed=True, open_arrow=True)
f.note(x0 + CORE_W + GAP_H / 2, ya - 10, 'issue', align='center')
f.note(x0 + CORE_W + GAP_H / 2, yb + 10, 'release', align='center')

# core -> HBL2 (unchanged path)
cxb = x0 + CORE_W / 2
f.line([(cxb, y_core + CORE_H), (cxb, y_l2)])
# CUTE <-> HBL2: requests down, dedicated matrix read path up (wide)
cr = x_cute + CUTE_W / 2
f.line([(cr + 30, y_core + CORE_H), (cr + 30, y_l2)], sw=W_STRUCT)
f.line([(cr - 30, y_l2), (cr - 30, y_core + CORE_H)], sw=3, size=8)
f.note(cr - 40, y_core + CORE_H + GAP_V / 2, 'matrix read path\n512 b / bank', align='right')
f.note(cr + 38, y_core + CORE_H + GAP_V / 2, 'req', align='left')
# HBL2 -> LLC -> DDR
mx = x0 + inner / 2
f.line([(mx, y_l2 + ROW_H), (mx, y_llc)])
f.line([(mx, y_llc + ROW_H), (mx, y_mem)])

# ---------------------------------------------------------------- legend
ly = panel_h + 18
end = f.legend(0, ly, [('neutral', 'inherited from Kunminghu V2R2'), ('new', 'new in XSAI')])
x = end + 40
x = f.legend_line(x, ly + 6, 'request / data') + 24
f.legend_line(x, ly + 6, 'control', sw=W_STRUCT, dashed=True, open_arrow=True)

f.save()
