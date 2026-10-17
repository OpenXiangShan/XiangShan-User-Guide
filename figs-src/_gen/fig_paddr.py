"""paddr: physical address layout.

Source: docs/zh/memory-model.md 75 ("physical address is 48 bits");
FIG-GUIDE 6.11 ([55:48] reserved, [47:12] PPN, [11:0] offset). RTL:
Parameters.scala PAddrBitsMax = 56 (bits a Sv39/Sv48/Sv57 PTE can name);
the implemented PAddrBits is 48. PPN split follows the Sv48 page levels.
"""
from dsl import *

f = Fig('paddr')
sp = bitfield(f, 0, 0, [
    {'hi': 55, 'lo': 48, 'name': 'not impl.', 'kind': 'reserved'},
    {'hi': 47, 'lo': 39, 'name': 'PPN[3]'},
    {'hi': 38, 'lo': 30, 'name': 'PPN[2]'},
    {'hi': 29, 'lo': 21, 'name': 'PPN[1]'},
    {'hi': 20, 'lo': 12, 'name': 'PPN[0]'},
    {'hi': 11, 'lo': 0, 'name': 'page offset'},
], BF_W, name='PA')
yb = BF_ROW_H + 22
bf_brace(f, sp[1][0], sp[4][1], yb, 'PPN, 36 b')
bf_brace(f, sp[0][0], sp[0][1], yb, 'above 48-bit PA')
f.save()
