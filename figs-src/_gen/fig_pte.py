"""pte: Sv39 / Sv48 page-table entry layout.

Source: docs/zh/memory-model.md 83-121 (PTE figure; PBMT, RSW, D, A, G, U,
X, W, R, V descriptions; PBMT needs menvcfg.PBMTE). RTL: MMUBundle.scala
PteBundle (n, pbmt, reserved, ppn_high, ppn, rsw, perm{d a g u x w r v});
MMUConst.scala pteResLen = 7, ptePbmtLen = 2, pteNLen = 1, ppnLen =
PAddrBits - 12 = 36, ppn_high = 44 - 36 = 8 b.
"""
from dsl import *

f = Fig('pte')
sp = bitfield(f, 0, 0, [
    {'hi': 63, 'lo': 63, 'name': 'N'},
    {'hi': 62, 'lo': 61, 'name': 'PBMT'},
    {'hi': 60, 'lo': 54, 'name': 'reserved', 'kind': 'reserved'},
    {'hi': 53, 'lo': 28, 'name': 'PPN[2]'},
    {'hi': 27, 'lo': 19, 'name': 'PPN[1]'},
    {'hi': 18, 'lo': 10, 'name': 'PPN[0]'},
    {'hi': 9, 'lo': 8, 'name': 'RSW'},
    {'hi': 7, 'lo': 7, 'name': 'D'},
    {'hi': 6, 'lo': 6, 'name': 'A'},
    {'hi': 5, 'lo': 5, 'name': 'G'},
    {'hi': 4, 'lo': 4, 'name': 'U'},
    {'hi': 3, 'lo': 3, 'name': 'X'},
    {'hi': 2, 'lo': 2, 'name': 'W'},
    {'hi': 1, 'lo': 1, 'name': 'R'},
    {'hi': 0, 'lo': 0, 'name': 'V'},
], BF_W, name='PTE', min_w=40)
yb = BF_ROW_H + 22
bf_brace(f, sp[3][0], sp[5][1], yb, 'PPN, 44 b (36 b used with 48-bit PA)')
bf_brace(f, sp[7][0], sp[14][1], yb, 'permission / status bits')
bf_brace(f, sp[1][0], sp[1][1], yb, 'needs PBMTE')
f.save()
