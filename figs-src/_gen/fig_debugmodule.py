"""debugmodule: position of the debug module in the debug environment.

Source: docs/zh/debug.md 8-17: GDB (debug software) and openocd (debug
agent) talk over the network; openocd reaches the on-chip debugger through
a JTAG adapter ("Jtag 仿真器" in the text, FIG-GUIDE 6.12: JTAG adapter);
the debugger (debug module wrapper) = JtagDTM + DMI + DM; JTAG between
adapter and chip. RTL: device/RocketDebugWrapper.scala (DebugModule with
JtagDTM; dtm.io.jtag_clock := TCK; DM drives harts).
"""
from dsl import *

f = Fig('debugmodule')
BW, BH = 120, 56
G = 60
y = 40
xs = [0, BW + G, 2 * (BW + G)]
host = [('GDB', 'debug software'), ('openocd', 'debug agent'), ('JTAG adapter', 'probe')]
for x, (t, s) in zip(xs, host):
    f.box(x, y, BW, BH, t, s, kind='neutral', sub_fs=FS_PIN)
links = ['network', '']
for k, lab in enumerate(links):
    xa = xs[k] + BW
    f.line([(xa, y + BH / 2), (xs[k + 1], y + BH / 2)], arrow='both', sw=W_STRUCT, size=6)
    f.note(xa + G / 2, y + BH / 2 - 12, lab, align='center')
f.group(-12, y - 34, 3 * BW + 2 * G + 24, BH + 52, 'Off-chip', kind='group', dashed=True, fs=FS_SUB)

# chip side
wx = xs[2] + BW + 90
IW = 116
IG = 44
inner = [('JtagDTM', 'compute', ''), ('DMI', 'compute', ''), ('DM', 'control', 'dmOuter / dmInner')]
ww = 3 * IW + 2 * IG + 40
f.group(wx, y - 34, ww, BH + 52, 'debug module wrapper', kind='panel', dashed=False, fs=FS_SUB)
ix = [wx + 20 + k * (IW + IG) for k in range(3)]
for x, (t, kind, sub) in zip(ix, inner):
    f.box(x, y, IW, BH, t, sub, kind=kind, sub_fs=FS_PIN)
f.line([(xs[2] + BW, y + BH / 2), (ix[0], y + BH / 2)], arrow='both', sw=W_STRUCT, size=6)
f.note(xs[2] + BW + 45, y + BH / 2 - 12, 'JTAG', align='center')
f.line([(ix[0] + IW, y + BH / 2 - 10), (ix[1], y + BH / 2 - 10)], size=6)
f.note(ix[0] + IW + IG / 2, y + BH / 2 - 22, 'req', align='center')
f.line([(ix[1], y + BH / 2 + 10), (ix[0] + IW, y + BH / 2 + 10)], size=6)
f.note(ix[0] + IW + IG / 2, y + BH / 2 + 22, 'resp', align='center')
f.line([(ix[1] + IW, y + BH / 2), (ix[2], y + BH / 2)], arrow='both', size=6)

# harts (stacked)
hx = wx + ww + 110
for k in range(2, -1, -1):
    f.box(hx + 8 * k, y - 8 * k, 90, BH, 'hart' if k == 0 else '', kind='storage')
f.line([(wx + ww, y + BH / 2), (hx, y + BH / 2)], arrow='both', sw=W_STRUCT, size=6)
f.note(wx + ww + 55, y + BH / 2 - 12, 'halt / resume', align='center')

ly = y + BH + 50
x = f.legend(0, ly, [('neutral', 'off-chip'), ('compute', 'debug transport'), ('control', 'debug module'),
                     ('storage', 'hart')])
f.save()
