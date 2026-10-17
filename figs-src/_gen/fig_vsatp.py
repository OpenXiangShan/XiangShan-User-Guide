"""vsatp: vsatp register layout (SXLEN = 64).

Source: docs/zh/memory-model.md 145-151 (vsatp controls VS-stage, SXLEN
fixed at 64) and 177-185 (satp fields: MODE [63:60] 0 / 8 / 9 = Bare /
Sv39 / Sv48, ASID [59:44] 16 b, PPN [43:0]); vsatp replaces satp in
virtualized mode and its PPN is a guest physical page number.
"""
from dsl import *

f = Fig('vsatp')
sp = bitfield(f, 0, 0, [
    {'hi': 63, 'lo': 60, 'name': 'MODE'},
    {'hi': 59, 'lo': 44, 'name': 'ASID'},
    {'hi': 43, 'lo': 0, 'name': 'PPN'},
], BF_W, name='vsatp', min_w=110)
yb = BF_ROW_H + 22
bf_brace(f, sp[0][0], sp[0][1], yb, '0 Bare, 8 Sv39, 9 Sv48')
bf_brace(f, sp[1][0], sp[1][1], yb, 'address-space ID, up to 16 b')
bf_brace(f, sp[2][0], sp[2][1], yb, 'root page table, guest physical page number')
f.note(BF_W + 14, BF_ROW_H + 12, 'all fields WARL', align='left', italic=True)
f.save()
