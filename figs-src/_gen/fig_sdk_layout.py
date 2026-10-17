"""sdk-layout: xsai-env components under one top-level Makefile.

Source: docs/zh/sdk/layout.md 8-75 (positioning table: repository root is
the default entry, root Makefile; submodule table / VERSIONS; directory
responsibilities; software framework submodules). The four columns follow
FIG-GUIDE 6.8 (RTL & simulator / simulators / firmware & bring-up /
compiler & software); members are the real directories from layout.md.
"""
from dsl import *

f = Fig('sdk-layout')

COLS = [
    ('RTL & spec', 'compute', ['XSAI', 'XSAI/CUTE', 'riscv-matrix-spec', 'docs/CUTE-Design-Doc']),
    ('Simulators', 'compute', ['NEMU', 'qemu', 'DRAMsim3', 'NutShell']),
    ('Firmware & bring-up', 'storage', [('linux-6.18', 'opensbi'), ('riscv-rootfs', 'nemu_board'),
                                        ('gcpt_restore', 'LibCheckpoint'), 'nexus-am']),
    ('Compiler & software', 'control', ['llvm-project-ame', 'DSL', ('MNN', 'ncnn'),
                                        ('llama.cpp', 'TMA-toolkit')]),
]
SUBS = {0: 'RTL, Verilog, DUT difftest', 1: 'ISA reference, DRAM, ref. core',
        2: 'firmware/*, nexus-am/', 3: 'llvm, DSL/, software/*, tools/*'}

CW = 230
CG = 24
PAD = 14
TT = 50
IH = 28
IG = 8
W = 4 * CW + 3 * CG
nmax = max(len(c[2]) for c in COLS)
col_h = TT + nmax * IH + (nmax - 1) * IG + PAD

MK_H = 46
y_col = 0
for i, (title, kind, items) in enumerate(COLS):
    x = i * (CW + CG)
    f.rect(x, y_col, CW, col_h, 'panel')
    f.text(x + PAD, y_col + 8, CW - 2 * PAD, 18, title, FS_MAIN, bold=True, align='left')
    f.text(x + PAD, y_col + 27, CW - 2 * PAD, 15, SUBS[i], FS_PIN, italic=True, color=NOTE, align='left')
    for j, it in enumerate(items):
        iy = y_col + TT + j * (IH + IG)
        if isinstance(it, tuple):
            hw = (CW - 2 * PAD - IG) / 2
            for k, sub in enumerate(it):
                f.box(x + PAD + k * (hw + IG), iy, hw, IH, sub, kind=kind, fs=FS_SUB)
        else:
            f.box(x + PAD, iy, CW - 2 * PAD, IH, it, kind=kind, fs=FS_SUB)

# top-level Makefile: the single entry everything is driven from
y_mk = y_col + col_h + 44
f.box(0, y_mk, W, MK_H, 'Top-level Makefile  (repository root)', 'env.sh  /  scripts/  /  mk/  /  VERSIONS',
      kind='neutral', bold=True)
for i in range(4):
    cx = i * (CW + CG) + CW / 2
    f.line([(cx, y_mk), (cx, y_col + col_h)], sw=W_STRUCT, dashed=True, open_arrow=True)
f.note(CW / 2 + 8, y_mk - 22, 'make targets', align='left')

# shared spec / generated output strips
y_s = y_mk + MK_H + 20
SH = 30
f.box(0, y_s, W, SH, 'Generated outputs, not tracked:  local/   build/   log/   firmware/checkpoints/',
      kind='plain', fs=FS_SUB, dashed=True)

# legend
ly = y_s + SH + 22
end = f.legend(0, ly, [('compute', 'hardware / ISA model'), ('storage', 'firmware / runtime image'),
                       ('control', 'compiler / software')])
f.legend_line(end + 40, ly + 6, 'driven by root make targets', sw=W_STRUCT, dashed=True, open_arrow=True)

f.save()
