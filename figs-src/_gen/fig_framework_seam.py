"""framework-seam: where each framework is cut open for the matrix kernel.

Source: docs/zh/software/frameworks.md 87-93 (seam table: MNN core functions
table, MNNPackedMatMul etc., CPUMatMul / CPUAttention / BatchMatMul share the
table; NCNN arch layer implementation, registry + Convolution_riscv::forward,
no function table; ggml ggml-cpu/arch/riscv/ame/ame-matmul.c, kernel
selection M >= 64 and N >= 64), 60-66 (seam priority, single compilation
unit, guard + fallback to the framework kernel), 122 (kernel does GEMM only,
epilogue stays in the framework). Column comparison after TensorLift Fig3:
identical row structure, only the seam row differs.
"""
from dsl import *

f = Fig('framework-seam')

LBL_W = 110
CW = 250
CG = 36
BH = 52
VG = 34
colx = [LBL_W + i * (CW + CG) for i in range(3)]
W = 3 * CW + 2 * CG
y_hdr = 0
rows_y = [y_hdr + 36 + r * (BH + VG) for r in range(4)]
ROW_LBL = ['operator', 'layer impl.', 'kernel dispatch', 'fallback']

# column content per row: (title, sub, kind); None = level absent
COLS = [
    ('MNN', [('CPU ops', 'CPUMatMul, CPUAttention, BatchMatMul', 'neutral'),
             ('CPU backend', 'calls kernels through the table', 'neutral'),
             ('core functions table', 'MNNPackedMatMul, ...', 'new')]),
    ('NCNN', [('Convolution layer', 'registry picks the arch impl.', 'neutral'),
              ('Convolution_riscv::forward', 'new riscv int8 path (was empty)', 'new'),
              None]),
    ('ggml', [('GGML_OP_MUL_MAT', 'prefill GEMM; decode stays GEMV', 'neutral'),
              ('ggml-cpu backend', 'per-arch kernel files', 'neutral'),
              ('ame-matmul.c', 'arch/riscv/ame, M ≥ 64 and N ≥ 64', 'new')]),
]

for r, name in enumerate(ROW_LBL):
    f.text(0, rows_y[r], LBL_W - 16, BH, name, FS_SUB, bold=True, align='right', color=NOTE)

y_bar = rows_y[3] + BH + VG
BAR_H = 52
xp = lambda c: c + CW * 0.28            # guard-pass lane
xf = lambda c: c + CW * 0.75            # guard-fail lane
for i, (fw, rows) in enumerate(COLS):
    c = colx[i]
    f.text(c, y_hdr, CW, 22, fw, FS_GROUP, bold=True)
    seam = max(r for r, it in enumerate(rows) if it and it[2] == 'new')
    for r, it in enumerate(rows):
        if it is None:
            continue
        t, sub, kind = it
        f.box(c, rows_y[r], CW, BH, t, sub, kind=kind, fs=FS_MAIN, sub_fs=FS_PIN, bold=(kind == 'new'))
        if r < seam:
            f.line([(c + CW / 2, rows_y[r] + BH), (c + CW / 2, rows_y[r + 1])])
    if seam == 1:
        ph_x0, ph_x1 = xp(c) + 16, xf(c) - 16
        f.rect(ph_x0, rows_y[2], ph_x1 - ph_x0, BH, 'group', dashed=True)
        f.text(ph_x0, rows_y[2], ph_x1 - ph_x0, BH, 'no function\ntable', FS_PIN, italic=True, color=NOTE)
    # fallback: framework's own kernel
    fb_x = c + CW * 0.5
    f.box(fb_x, rows_y[3], CW * 0.5, BH, 'native kernel', 'RVV / scalar', kind='plain', fs=FS_SUB,
          sub_fs=FS_PIN)
    sy = rows_y[seam] + BH
    f.line([(xf(c), sy), (xf(c), rows_y[3])], sw=W_STRUCT, dashed=True, open_arrow=True)
    f.line([(xp(c), sy), (xp(c), y_bar)])
    f.note(xf(c) + 10, rows_y[3] - VG / 2, 'guard fails', align='left', italic=True)
    f.note(xp(c) - 10, y_bar - VG / 2, 'guard passes', align='right', italic=True)

f.box(colx[0], y_bar, W, BAR_H, 'Shared matrix kernel  (single compilation unit)',
      'tile geometry from probe; GEMM only, quantization epilogue stays in the framework', kind='compute', bold=True,
      sub_fs=FS_SUB)

ly = y_bar + BAR_H + 26
x = f.legend(colx[0], ly, [('new', 'seam'), ('neutral', 'framework layer'), ('compute', 'matrix kernel')])
x = f.legend_line(x + 30, ly + 6, 'call path')
f.legend_line(x + 30, ly + 6, 'fallback', sw=W_STRUCT, dashed=True, open_arrow=True)

f.save()
