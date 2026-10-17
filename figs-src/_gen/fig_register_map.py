"""register-map: 3-bit selector -> matrix register / mcfg pairs, and mcfg layout.

Source: docs/zh/isa/registers.md 10-16 (tr0-tr3 A/B tiles, acc0-acc3
accumulators) and 34-42 (mcfg bit fields; "000-011 -> tr0-tr3 / mcfg0-3,
100-111 -> acc0-acc3 / mcfg4-7"). Geometric alignment after ARM-SME Fig1:
every selector code, register and mcfg sits in the same column, no fan-out
lines needed.
"""
from dsl import *

f = Fig('register-map')

LBL_W = 150
CW = 92               # column width
CG = 10               # gap inside a group
GG = 40               # gap between the two groups
RH = 34
RG = 16

colx = []
for i in range(8):
    colx.append(LBL_W + i * (CW + CG) + (GG - CG if i >= 4 else 0))
W = colx[-1] + CW - LBL_W
y_grp = 0
y_code = y_grp + 44
y_reg = y_code + RH + RG
y_cfg = y_reg + RH + RG

# group headers (bracket lines)
for g, (title, kind) in enumerate((('selector[2] = 0: tile registers (A / B)', 'compute'),
                                   ('selector[2] = 1: accumulators (C)', 'storage'))):
    x0 = colx[4 * g]
    x1 = colx[4 * g + 3] + CW
    f.text(x0, y_grp, x1 - x0, 18, title, FS_SUB, bold=True)
    f.line([(x0, y_grp + 24), (x1, y_grp + 24)], arrow='none', sw=W_STRUCT, color=INK)
    f.line([(x0, y_grp + 24), (x0, y_grp + 30)], arrow='none', sw=W_STRUCT, color=INK)
    f.line([(x1, y_grp + 24), (x1, y_grp + 30)], arrow='none', sw=W_STRUCT, color=INK)

rows = [('selector', y_code), ('matrix register', y_reg), ('config register', y_cfg)]
for name, y in rows:
    f.text(0, y, LBL_W - 16, RH, name, FS_SUB, bold=True, align='right')

for i in range(8):
    x = colx[i]
    kind = 'compute' if i < 4 else 'storage'
    f.box(x, y_code, CW, RH, format(i, '03b'), kind='plain', fs=FS_MAIN)
    reg = f'tr{i}' if i < 4 else f'acc{i - 4}'
    f.box(x, y_reg, CW, RH, reg, kind=kind, fs=FS_MAIN, bold=True)
    f.box(x, y_cfg, CW, RH, f'mcfg{i}', kind='control', fs=FS_MAIN)
    # vertical alignment ties (thin)
    f.line([(x + CW / 2, y_code + RH), (x + CW / 2, y_reg)], sw=W_STRUCT, size=5)
    f.line([(x + CW / 2, y_reg + RH), (x + CW / 2, y_cfg)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)

# ---------------------------------------------------------------- mcfg layout
y_bf = y_cfg + RH + 60
f.text(0, y_bf, LBL_W - 16, BF_ROW_H, 'mcfgN layout', FS_SUB, bold=True, align='right')
fields = [
    {'hi': 'XLEN-1', 'lo': 8, 'name': 'uninterpreted payload', 'kind': 'reserved', 'bits': 56},
    {'hi': 7, 'lo': 4, 'name': 'table_sel', 'bits': 4},
    {'hi': 3, 'lo': 0, 'name': 'type_code', 'bits': 4},
]
# custom widths (XLEN is symbolic); draw with the shared bitfield style
ws = [W - 2 * 150, 150, 150]
cx = LBL_W
for k, (fd, w) in enumerate(zip(fields, ws)):
    grey = fd.get('kind') == 'reserved'
    fill = PAL['neutral'][0] if grey else (PAL['compute'][0] if k == 1 else '#FFFFFF')
    f.rect(cx, y_bf, w, BF_ROW_H, 'plain', fill=fill, stroke=INK)
    f.text(cx, y_bf, w, BF_ROW_H, fd['name'], FS_SUB, italic=grey)
    ty = y_bf - BF_LABEL_GAP - FS_PIN * 1.2
    f.text(cx + 3, ty, w / 2, FS_PIN * 1.2, str(fd['hi']), FS_PIN, color=NOTE, align='left')
    f.text(cx + w / 2 - 3, ty, w / 2, FS_PIN * 1.2, str(fd['lo']), FS_PIN, color=NOTE, align='right')
    cx += w
f.note(LBL_W + ws[0] / 2, y_bf + BF_ROW_H + 14, 'stored by msetcfg, returned by mgetcfg unchanged', align='center',
       italic=True)
f.note(LBL_W + ws[0] + ws[1] / 2, y_bf + BF_ROW_H + 14, 'type table', align='center', italic=True)
f.note(LBL_W + ws[0] + ws[1] + ws[2] / 2, y_bf + BF_ROW_H + 14, 'type in table', align='center', italic=True)

# legend
ly = y_bf + BF_ROW_H + 44
x = f.legend_line(LBL_W, ly, 'selector code picks the register', sw=W_STRUCT)
f.legend_line(x + 30, ly, 'register and its config travel together (same code)', sw=W_STRUCT, dashed=True)
f.cells[-2] = f.cells[-2].replace('endArrow=block', 'endArrow=none').replace(f'strokeColor={INK}', f'strokeColor={NOTE}')

f.save()
