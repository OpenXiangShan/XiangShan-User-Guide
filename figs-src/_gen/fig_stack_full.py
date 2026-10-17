"""stack-full: XSAI AI software / hardware overview.

Left: the software stack top-down (models -> frameworks -> operators ->
toolchain -> ISA), landing on the hardware platform below the HW/SW line.
ISA and hardware share a 4-column grid so RISC-V / RVV / AME sit directly
above the scalar core / vector unit / matrix unit they target.
Right: system runtime support and development & verification tools.
Bottom: ecosystem strip.

Monochrome except one accent (compute blue) marking the AME matrix
extension and the unit that executes it. Primary port vs ecosystem path is
encoded by line weight / dash, not colour.
"""
from dsl import *

NAME_W = 182         # layer-name column inside each band
PAD = 11             # band inner padding
COL_W = 132          # one grid column of the left stack
CG = 12              # gap between columns
ROW_H = 60           # standard band height
OP_H = 100           # operator-development band (two-level content)
GAP = 28             # gap between bands (hosts the flow arrows)
HW_GAP = 44          # larger gap that hosts the HW / SW interface line
RIGHT_GAP = 32       # gap between left stack and right column
RIGHT_W = 262
ECO_GAP = 32

BAND_W = NAME_W + 4 * COL_W + 3 * CG + PAD
ARW = dict(sw=W_STRUCT, size=6)

f = Fig('stack-full')
x0 = NAME_W                       # first grid column


def col(i, span=1):
    return x0 + i * (COL_W + CG), span * COL_W + (span - 1) * CG


def band(y, h, name):
    f.rect(0, y, BAND_W, h, 'panel')
    f.text(16, y, NAME_W - 22, h, name, FS_MAIN, bold=True, align='left')


rows = [('Model workloads', ROW_H), ('Inference frameworks', ROW_H),
        ('Operator development', OP_H), ('Compilation toolchain', ROW_H),
        ('ISA spec', ROW_H), ('Hardware platform', ROW_H)]
ys, y = [], 0
for i, (name, h) in enumerate(rows):
    if i:
        y += HW_GAP if i == 5 else GAP
    ys.append(y)
    band(y, h, name)
    y += h
bottom = y
iy = lambda i: ys[i] + PAD
ih = lambda i: rows[i][1] - 2 * PAD

# ---------------------------------------------------------------- 1 models
for j, m in enumerate(['Qwen', 'LLaMA', 'DeepSeek', 'other LLMs']):
    cx, cw = col(j)
    if j == 3:
        f.box(cx, iy(0), cw, ih(0), m, dashed=True)
    else:
        f.box(cx, iy(0), cw, ih(0), m)

# ---------------------------------------------------------------- 2 frameworks
fx_l, fw = col(0, 2)
fx_r, _ = col(2, 2)
f.box(fx_l, iy(1), fw, ih(1), 'llama.cpp / ggml', 'primary port', sw=W_DATA)
f.box(fx_r, iy(1), fw, ih(1), 'PyTorch', 'ecosystem', dashed=True)

# ---------------------------------------------------------------- 3 operators
f.box(fx_l, iy(2), fw, ih(2), 'xsai-blas', 'lightweight operator library\n+ AME acceleration')
oy, oh = iy(2), ih(2)
f.rect(fx_r, oy, fw, oh, 'plain')
f.text(fx_r, oy + 7, fw, 18, 'DSL operator compilation', FS_MAIN)
sw_ = (fw - 2 * 14 - 12) / 2
for j, d in enumerate(['Triton', 'TileLang']):
    f.box(fx_r + 14 + j * (sw_ + 12), oy + 30, sw_, 24, d, fs=FS_SUB, kind='neutral')
f.text(fx_r, oy + oh - 22, fw, 14, 'kernel description → IR → low-level code', FS_PIN,
       italic=True, color=NOTE)

# ---------------------------------------------------------------- 4 toolchain
tx, tw = col(0, 4)
f.box(tx, iy(3), tw, ih(3), 'buddy-mlir / LLVM 21 + AME',
      'operator compilation  ·  assembly / C / C++  ·  AME intrinsics')

# ---------------------------------------------------------------- 5 ISA
blue = PAL['compute']
c0, cw0 = col(0)
f.box(c0, iy(4), cw0, ih(4), 'RISC-V', 'base ISA')
c1, _ = col(1)
f.box(c1, iy(4), cw0, ih(4), 'RVV', 'vector extension')
ax_, aw = col(2, 2)
f.box(ax_, iy(4), aw, ih(4), 'AME', 'community AME v0.6 draft extension', kind='compute')

# ---------------------------------------------------------------- 6 hardware
hw = [('XSAI CPU', 'scalar core', 'plain'), ('Vector unit', 'RVV', 'plain'),
      ('Matrix unit', 'AME', 'compute'), ('L2 cache', 'high bandwidth', 'plain')]
for j, (t, s, k) in enumerate(hw):
    cx, cw = col(j)
    f.box(cx, iy(5), cw, ih(5), t, s, kind=k)

# ---------------------------------------------------------------- flow arrows
def down(x, i, dashed=False, from_band=False):
    """Arrow in the gap below band i, from its inner box (or the band edge) to the next one."""
    y0 = ys[i] + rows[i][1] if from_band else iy(i) + ih(i)
    f.line([(x, y0), (x, iy(i + 1))], dashed=dashed, **ARW)


cl, cr = fx_l + fw / 2, fx_r + fw / 2
down(cl, 0, from_band=True); down(cr, 0, dashed=True, from_band=True)
down(cl, 1); down(cr, 1, dashed=True)
down(cl, 2); down(cr, 2)
for j in range(3):
    cx, cw = col(j)
    down(cx + cw / 2, 3)
    down(cx + cw / 2, 4)

# HW / SW interface between ISA and hardware
ly = ys[5] - HW_GAP / 2
f.line([(0, ly), (BAND_W, ly)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)
lab = 'HW / SW interface'
lw = text_w(lab, FS_PIN, italic=True) + 8
f.rect(0, ly - 8, lw, 16, 'plain', fill='#FFFFFF', stroke='#FFFFFF')
f.text(0, ly - 8, lw, 16, lab, FS_PIN, italic=True, color=NOTE, align='left')

# ---------------------------------------------------------------- right column
rx = BAND_W + RIGHT_GAP
TITLE_H = 34
BOX_IN = 14


def side(y0, y1, title, items, h):
    f.rect(rx, y0, RIGHT_W, y1 - y0, 'panel')
    f.text(rx + BOX_IN, y0 + 8, RIGHT_W - 2 * BOX_IN, 20, title, FS_MAIN, bold=True, align='left')
    top, bot = y0 + TITLE_H, y1 - PAD
    g = CG
    h = (bot - top - (len(items) - 1) * g) / len(items)
    for k, it in enumerate(items):
        t, s = it if isinstance(it, tuple) else (it, '')
        f.box(rx + BOX_IN, top + k * (h + g), RIGHT_W - 2 * BOX_IN, h, t, s)


side(ys[0], ys[2] + OP_H, 'System runtime support',
     [('Linux', 'context & exception management'),
      ('OpenSBI', 'hardware init  ·  PMU'),
      ('Device tree  ·  RootFS', '')], 54)
side(ys[3], bottom, 'Development & verification tools',
     ['Bare-metal MicroBenchmark', 'QEMU user / system', 'NEMU + DiffTest',
      'RTL simulation'], 36)

# ---------------------------------------------------------------- ecosystem
ey = bottom + ECO_GAP
full = rx + RIGHT_W
f.rect(0, ey, full, ROW_H, 'panel')
f.text(16, ey, NAME_W - 22, ROW_H, 'Ecosystem', FS_MAIN, bold=True, align='left')
f.box(x0, ey + PAD, full - x0 - BOX_IN, ROW_H - 2 * PAD, 'XSAI × RuyiAI',
      'MoU signed: jointly building the XSAI software ecosystem')

# ---------------------------------------------------------------- legend
gy = ey + ROW_H + 22
x = f.legend(0, gy, [('compute', 'AME matrix extension')]) + 36
x = f.legend_line(x, gy + 6, 'primary path', sw=W_STRUCT) + 30
f.legend_line(x, gy + 6, 'ecosystem path', sw=W_STRUCT, dashed=True)

f.save()
