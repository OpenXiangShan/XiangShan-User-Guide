"""sv48x4: Sv48x4 guest-physical address layout (G-stage).

Source: docs/zh/memory-model.md 159-165 (hgatp MODE 9 = Sv48x4); RISC-V
H extension: GPA is 50 bits, the root VPN[3] widened by 2 bits. RTL:
Parameters.scala GPAddrBitsSv48x4 = 50.
"""
from dsl import *

f = Fig('sv48x4')
sp = bitfield(f, 0, 0, [
    {'hi': 63, 'lo': 50, 'name': 'zero', 'kind': 'zero'},
    {'hi': 49, 'lo': 39, 'name': 'VPN[3]'},
    {'hi': 38, 'lo': 30, 'name': 'VPN[2]'},
    {'hi': 29, 'lo': 21, 'name': 'VPN[1]'},
    {'hi': 20, 'lo': 12, 'name': 'VPN[0]'},
    {'hi': 11, 'lo': 0, 'name': 'page offset'},
], BF_W, name='Sv48x4 GPA')
yb = BF_ROW_H + 22
bf_brace(f, sp[1][0], sp[1][1], yb, '11 b: Sv48 VPN[3] + 2')
bf_brace(f, sp[0][0], sp[0][1], yb, 'non-zero: guest-page fault')
f.save()
