"""pma: PMA configuration and address register layouts.

Source: docs/zh/memory-model.md 264-305: 16 entries, M-mode custom CSRs
(pmacfg0 0x7C0, pmacfg2 0x7C2, pmaaddr0-15 0x7C8-0x7D7), reset values set;
cfg byte L [7], C [6] cacheable (0 = MMIO), Atomic [5], A [4:3], X, W, R;
pmaaddr [63:46] not implemented (read zero), [45:0] = PA[47:2].
RTL: PMA.scala PMAConfigEntry (l, c, atomic, a, x, w, r).
"""
from dsl import *

f = Fig('pma')
y = 0
for reg, base in (('pmacfg0', 0), ('pmacfg2', 8)):
    bitfield(f, 0, y, [{'hi': 8 * k + 7, 'lo': 8 * k, 'name': f'pma{base + k}cfg'} for k in range(7, -1, -1)],
             BF_W, name=reg, show_widths=False, alternate=False)
    y += BF_ROW_H + 34
CB_W = 420
y += 10
cx = BF_W - CB_W
sp = bitfield(f, cx, y, [
    {'hi': 7, 'lo': 7, 'name': 'L'},
    {'hi': 6, 'lo': 6, 'name': 'C'},
    {'hi': 5, 'lo': 5, 'name': 'Atomic'},
    {'hi': 4, 'lo': 3, 'name': 'A'},
    {'hi': 2, 'lo': 2, 'name': 'X'},
    {'hi': 1, 'lo': 1, 'name': 'W'},
    {'hi': 0, 'lo': 0, 'name': 'R'},
], CB_W, name='pmaNcfg', show_widths=False, min_w=50)
src_y = BF_ROW_H + 34 + BF_ROW_H
f.line([(BF_W - BF_W / 8, src_y), (cx, y - 18)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)
f.line([(BF_W, src_y), (BF_W, y - 18)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)
bf_brace(f, sp[1][0], sp[1][1], y + BF_ROW_H + 6, 'cacheable')
f.note(0, y + BF_ROW_H / 2 - 9, '16 entries, M-mode custom CSRs', italic=True)
f.note(0, y + BF_ROW_H / 2 + 9, 'non-zero reset values (platform map)', italic=True)
bf_brace(f, sp[3][0], sp[3][1], y + BF_ROW_H + 6, 'OFF / TOR / NA4 / NAPOT')
y += BF_ROW_H + 64
bitfield(f, 0, y, [
    {'hi': 63, 'lo': 46, 'name': 'not impl., read 0', 'kind': 'reserved'},
    {'hi': 45, 'lo': 0, 'name': 'address = PA[47:2]'},
], BF_W, name='pmaaddrN')
f.save()
