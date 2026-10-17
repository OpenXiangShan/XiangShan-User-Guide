"""pmbt: Svpbmt page-based memory types (PTE.PBMT encoding).

Source: docs/zh/memory-model.md 89-103: PMA (0) keeps the physical PMA;
NC (1) non-cacheable, idempotent, weakly ordered, main memory; IO (2)
non-cacheable, non-idempotent, strongly ordered, I/O; 3 reserved; needs
menvcfg.PBMTE. Attributes not covered by PBMT stay with the PMA.
"""
from dsl import *

f = Fig('pmbt')
COLS = [('Mode', 70), ('PBMT', 60), ('Cacheable', 100), ('Idempotent', 100), ('Ordering', 180),
        ('Typical use', 180)]
ROWS = [('PMA', '0', 'from PMA', 'from PMA', 'from PMA', 'follow physical PMA', 'plain'),
        ('NC', '1', 'no', 'yes', 'weak (RVWMO / RVTSO)', 'main memory', 'compute'),
        ('IO', '2', 'no', 'no', 'strong (I/O)', 'peripherals', 'control'),
        ('-', '3', '', '', '', 'reserved', 'neutral')]
RH = 30
x = 0
W = sum(w for _, w in COLS)
for c, (h, w) in enumerate(COLS):
    f.text(x, 0, w, RH, h, FS_SUB, bold=True, align='left' if c >= 5 else 'center')
    x += w
f.line([(0, RH), (W, RH)], arrow='none', sw=W_DATA, color=INK)
f.line([(0, 0), (W, 0)], arrow='none', sw=W_STRUCT, color=INK)
for r, row in enumerate(ROWS):
    y = RH + r * RH
    kind = row[6]
    x = 0
    for c, (h, w) in enumerate(COLS):
        italic = row[c].startswith('from') or row[c] == 'reserved'
        f.text(x, y, w, RH, row[c], FS_SUB, bold=(c == 0), italic=italic,
               color=NOTE if italic else INK, align='left' if c >= 5 else 'center')
        x += w
    f.line([(0, y + RH), (W, y + RH)], arrow='none', sw=W_STRUCT if r < 3 else W_DATA,
           color='#C0C0C0' if r < 3 else INK)
f.note(0, RH * 5 + 14, 'PTE[62:61]; active only when menvcfg.PBMTE = 1. Attributes PBMT does not set stay with the PMA.',
       italic=True)
f.save()
