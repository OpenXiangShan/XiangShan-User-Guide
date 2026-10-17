"""debug2harts: debug module to hart connections and clock domains.

Source: docs/zh/debug.md 19-21 (figure only: connection and clock-domain
relation between debugger and harts); content follows the existing figure
(jtag_clk / soc_reset for DM outer, soc_clk for DM inner, CLINT, IMSIC;
noc_clk for the CMN interconnect; cpu_clk for each XSTop; ndmreset from DM
to the soc / noc / cpu resets; hartIsInReset and debug interrupt per core;
sysbus AXI master and debug MMIO AXI slave on DM inner).
RTL: top/XSNoCTop.scala 80-88 (noc_clock, soc_clock, per-domain ResetGen),
492-497 (XSTop scope runs on soc_clock, core_with_l2 on a gated cpu clock);
device/RocketDebugWrapper.scala 61-73 (tl_clock for DM inner, debug_clock
for outer, hartIsInReset, ndreset).
"""
from dsl import *

f = Fig('debug2harts')
DOM = [('JTAG domain', 'jtag_clk / soc_reset', 0, 200),
       ('SoC domain', 'soc_clk / soc_reset', 200, 560),
       ('NoC domain', 'noc_clk / noc_reset', 560, 720),
       ('CPU domain', 'cpu_clk / cpu_reset', 720, 1010)]
Y_TOP = 0
Y_LANE_H, Y_LANE_I = 70, 92
Y0 = 124
Y_BUS = 420
Y_RST = 440
Y_END = Y_RST + 26 + 16
RED = PAL['new'][1]

for k, (name, clk, x0, x1) in enumerate(DOM):
    f.text(x0 + 12, Y_TOP, x1 - x0 - 24, 18, name, FS_MAIN, bold=True, align='left')
    f.text(x0 + 12, Y_TOP + 20, x1 - x0 - 24, 16, clk, FS_PIN, italic=True, color=NOTE, align='left')
    if k:
        f.line([(x0, Y_TOP - 4), (x0, Y_END)], arrow='none', sw=W_STRUCT, dashed=True, color=NOTE)

# DM spans the JTAG / SoC boundary: outer and inner halves
f.group(16, Y0 - 8, 412, 100, 'DM', kind='group', dashed=False, fs=FS_SUB, title_inside=False)
ox, ix, MW, MH = 30, 284, 130, 70
f.box(ox, Y0 + 10, MW, MH, 'DM outer', 'dmOuter', kind='control', sub_fs=FS_PIN)
f.box(ix, Y0 + 10, MW, MH, 'DM inner', 'dmInner', kind='control', sub_fs=FS_PIN)
f.line([(ox + MW, Y0 + 45), (ix, Y0 + 45)], arrow='both', sw=W_STRUCT, size=6)
f.note(DOM[1][2] + 6, Y0 + 33, 'async', align='left', italic=True)
f.box(ix, 270, MW, 36, 'CLINT', kind='neutral', fs=FS_SUB)
f.box(ix, 326, MW, 36, 'IMSIC', kind='neutral', fs=FS_SUB)

# CMN
cx, CW = 590, 100
f.box(cx, Y0, CW, 260, 'CMN', 'CHI\ninterconnect', kind='storage', sub_fs=FS_PIN)
f.line([(ix + MW, Y0 + 30), (cx, Y0 + 30)], size=6)
f.note(ix + MW + 22, Y0 + 12, 'sysbus\n(AXI master)', align='left')
f.line([(cx, Y0 + 62), (ix + MW, Y0 + 62)], size=6)
f.note(ix + MW + 22, Y0 + 82, 'debug MMIO\n(AXI slave)', align='left')

# cores
tx, TW, TH = 790, 140, 80
ty = [Y0 + 10, Y0 + 150]
for k, y in enumerate(ty):
    f.box(tx, y, TW, TH, f'XSTop {k}', 'core + L2', kind='compute', sub_fs=FS_PIN)
    f.line([(cx + CW, y + TH / 2), (tx, y + TH / 2)], arrow='both', size=6)
    f.note((DOM[3][2] + tx) / 2, y + TH / 2 - 12, 'CHI', align='center')

# debug interrupt: DM inner -> every core
bi, bh = tx + TW + 30, tx + TW + 56
ctl = dict(sw=W_STRUCT, dashed=True, open_arrow=True, size=6)
f.line([(ix + 40, Y0 + 10), (ix + 40, Y_LANE_I), (bi, Y_LANE_I), (bi, ty[1] + 22), (tx + TW, ty[1] + 22)], **ctl)
f.line([(bi, ty[0] + 22), (tx + TW, ty[0] + 22)], **ctl)
f.note(cx + CW / 2, Y_LANE_I + 10, 'debug interrupt (per hart)', align='center')
# hartIsInReset: every core -> DM inner
f.line([(tx + TW, ty[0] + 58), (bh, ty[0] + 58)], arrow='none', sw=W_STRUCT, dashed=True)
f.line([(tx + TW, ty[1] + 58), (bh, ty[1] + 58), (bh, Y_LANE_H), (ix + 90, Y_LANE_H), (ix + 90, Y0 + 10)], **ctl)
f.note(cx + CW / 2, Y_LANE_H - 10, 'hartIsInReset (1 b per hart)', align='center')

# ndmreset from DM to the soc / noc / cpu reset generators
for (name, clk, x0, x1), lab in zip(DOM[1:], ('soc_reset', 'noc_reset', 'cpu_reset')):
    bx = (x0 + x1) / 2 - 50
    f.box(bx, Y_RST, 100, 26, lab, kind='plain', fs=FS_PIN)
    f.line([(bx + 50, Y_BUS), (bx + 50, Y_RST)], sw=W_STRUCT, color=RED, size=6)
x_last = (DOM[3][2] + DOM[3][3]) / 2
f.line([(ox + 40, Y0 + 10 + MH), (ox + 40, Y_BUS), (x_last, Y_BUS)], arrow='none', sw=W_STRUCT, color=RED)
f.note(ox + 48, Y_BUS - 10, 'ndmreset', align='left', color=RED)

ly = Y_END + 24
x = f.legend_line(0, ly, 'data (AXI / CHI)')
x = f.legend_line(x + 30, ly, 'debug control', sw=W_STRUCT, dashed=True, open_arrow=True)
x = f.legend_line(x + 30, ly, 'reset request', sw=W_STRUCT)
f.cells[-2] = f.cells[-2].replace(f'strokeColor={INK}', f'strokeColor={RED}')
f.note(x + 30, ly, 'dashed vertical lines: clock-domain boundaries', italic=True)
f.save()
