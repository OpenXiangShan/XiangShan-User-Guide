"""Sv48vaddr: Sv48 virtual address layout.

Source: docs/zh/memory-model.md 73-79 (Sv48: 48-bit VA, 12-bit page offset,
upper 36 bits split into four 9-bit VPN fields). Bits 63:48 must equal
bit 47 (RISC-V privileged spec). RTL: Parameters.scala VAddrBitsSv48 = 48.
"""
from dsl import *

f = Fig('Sv48vaddr')
sp = bitfield(f, 0, 0, [
    {'hi': 63, 'lo': 48, 'name': 'sign-ext. of bit 47', 'kind': 'ext'},
    {'hi': 47, 'lo': 39, 'name': 'VPN[3]'},
    {'hi': 38, 'lo': 30, 'name': 'VPN[2]'},
    {'hi': 29, 'lo': 21, 'name': 'VPN[1]'},
    {'hi': 20, 'lo': 12, 'name': 'VPN[0]'},
    {'hi': 11, 'lo': 0, 'name': 'page offset'},
], BF_W, name='Sv48 VA')
yb = BF_ROW_H + 22
bf_brace(f, sp[1][0], sp[4][1], yb, '4-level page-table index (9 b each)')
bf_brace(f, sp[0][0], sp[0][1], yb, 'must equal bit 47')
f.save()
