"""pmp: PMP configuration and address register layouts.

Source: docs/zh/memory-model.md 205-262: 16 entries, each an 8-bit cfg and
a 64-bit address register; pmpcfg0 / pmpcfg2 pack 8 cfg bytes each; cfg
byte L [7], reserved [6:5], A [4:3] (OFF / TOR / NA4 / NAPOT), X, W, R;
pmpaddr [63:46] not implemented (read zero), [45:0] = PA[47:2].
RTL: PMP.scala PMPConfig (bits 6:5 are c / atomic, unused in PMP).
"""
from dsl import *

f = Fig('pmp')
NAME_W = 110
y = 0
for reg, base in (('pmpcfg0', 0), ('pmpcfg2', 8)):
    bitfield(f, 0, y, [{'hi': 8 * k + 7, 'lo': 8 * k, 'name': f'pmp{base + k}cfg'} for k in range(7, -1, -1)],
             BF_W, name=reg, show_widths=False, alternate=False)
    y += BF_ROW_H + 34
# expanded cfg byte, under pmp0cfg
CB_W = 420
y += 10
cx = BF_W - CB_W
sp = bitfield(f, cx, y, [
    {'hi': 7, 'lo': 7, 'name': 'L'},
    {'hi': 6, 'lo': 5, 'name': 'res., 0', 'kind': 'reserved'},
    {'hi': 4, 'lo': 3, 'name': 'A'},
    {'hi': 2, 'lo': 2, 'name': 'X'},
    {'hi': 1, 'lo': 1, 'name': 'W'},
    {'hi': 0, 'lo': 0, 'name': 'R'},
], CB_W, name='pmpNcfg', show_widths=False, min_w=50)
# zoom lines from pmp8cfg (last byte of pmpcfg2) to the expanded byte
src_y = BF_ROW_H + 34 + BF_ROW_H
f.line([(BF_W - BF_W / 8, src_y), (cx, y - 18)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)
f.line([(BF_W, src_y), (BF_W, y - 18)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)
bf_brace(f, sp[2][0], sp[2][1], y + BF_ROW_H + 6, 'OFF / TOR / NA4 / NAPOT')
bf_brace(f, sp[0][0], sp[0][1], y + BF_ROW_H + 6, 'lock')
f.note(0, y + BF_ROW_H / 2, '16 entries; each = one cfg byte + one pmpaddr', italic=True)
y += BF_ROW_H + 64
spa = bitfield(f, 0, y, [
    {'hi': 63, 'lo': 46, 'name': 'not impl., read 0', 'kind': 'reserved'},
    {'hi': 45, 'lo': 0, 'name': 'address = PA[47:2]'},
], BF_W, name='pmpaddrN')
f.save()
