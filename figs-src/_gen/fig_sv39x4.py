"""sv39x4: Sv39x4 guest-physical address layout (G-stage).

Source: docs/zh/memory-model.md 159-163 (hgatp MODE 8 = Sv39x4); RISC-V
H extension: GPA is 41 bits, the root VPN[2] widened by 2 bits (root page
table 16 KiB, four times larger). RTL: Parameters.scala GPAddrBitsSv39x4 = 41.
"""
from dsl import *

f = Fig('sv39x4')
sp = bitfield(f, 0, 0, [
    {'hi': 63, 'lo': 41, 'name': 'zero', 'kind': 'zero'},
    {'hi': 40, 'lo': 30, 'name': 'VPN[2]'},
    {'hi': 29, 'lo': 21, 'name': 'VPN[1]'},
    {'hi': 20, 'lo': 12, 'name': 'VPN[0]'},
    {'hi': 11, 'lo': 0, 'name': 'page offset'},
], BF_W, name='Sv39x4 GPA')
yb = BF_ROW_H + 22
bf_brace(f, sp[1][0], sp[1][1], yb, '11 b: Sv39 VPN[2] + 2')
bf_brace(f, sp[0][0], sp[0][1], yb, 'non-zero: guest-page fault')
f.save()
