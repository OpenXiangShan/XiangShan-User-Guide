"""Sv39vaddr: Sv39 virtual address layout.

Source: docs/zh/memory-model.md 73-77 (Sv39: 39-bit VA, 12-bit page offset,
upper 27 bits split into three 9-bit VPN fields). Bits 63:39 must equal
bit 38 (RISC-V privileged spec). RTL: Parameters.scala VAddrBitsSv39 = 39.
"""
from dsl import *

f = Fig('Sv39vaddr')
sp = bitfield(f, 0, 0, [
    {'hi': 63, 'lo': 39, 'name': 'sign-ext. of bit 38', 'kind': 'ext'},
    {'hi': 38, 'lo': 30, 'name': 'VPN[2]'},
    {'hi': 29, 'lo': 21, 'name': 'VPN[1]'},
    {'hi': 20, 'lo': 12, 'name': 'VPN[0]'},
    {'hi': 11, 'lo': 0, 'name': 'page offset'},
], BF_W, name='Sv39 VA')
yb = BF_ROW_H + 22
bf_brace(f, sp[1][0], sp[3][1], yb, '3-level page-table index (9 b each)')
bf_brace(f, sp[0][0], sp[0][1], yb, 'must equal bit 38')
f.save()
