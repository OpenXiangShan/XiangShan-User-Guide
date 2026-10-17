"""cute-subsystems: CUTE's four subsystems and their connections.

Sources: docs/zh/hardware/microarchitecture.md 10-36 (subsystem table, core
interface, Load/Compute/Store flow); CUTE-Design-Doc hardware/*
(TaskController macro->micro inst, CDC writes D back, AfterOps passthrough,
LocalMMU is the single data-plane port).
"""
from dsl import *

f = Fig('cute-subsystems')

QW = 400            # quadrant width
GQ = 56             # gap between quadrants
PADQ = 20           # quadrant inner padding
TT = 34             # quadrant title band
BH = 48             # standard module height
VG = 40             # vertical gap between modules inside a quadrant
EXT_W = 130
EXT_GAP = 70

cx0 = EXT_W + EXT_GAP            # CUTE container x
q0x = cx0 + 24
q1x = q0x + QW + GQ
y0 = 40
top_h = TT + 2 * BH + VG + PADQ
y1 = y0 + top_h + GQ
MR_H = 70                         # matrix-register block (title + two slots)
bot_h = TT + 2 * (BH + VG) + MR_H + VG + BH + PADQ

# ---- container
f.group(cx0, 0, (q1x + QW + 24) - cx0, y1 + bot_h + 24, 'CUTE matrix unit', kind='group',
        dashed=False, fs=FS_GROUP, pad=12)

# ---- quadrants
for (qx, qy, qh, title) in ((q0x, y0, top_h, 'Interface integration'),
                             (q1x, y0, top_h, 'Control logic'),
                             (q0x, y1, bot_h, 'Storage system'),
                             (q1x, y1, bot_h, 'Compute engine')):
    f.group(qx, qy, QW, qh, title, kind='panel', dashed=True, fs=FS_MAIN, pad=12)

iw = QW - 2 * PADQ
# Interface quadrant
ifa = (q0x + PADQ, y0 + TT, iw, BH)
ifb = (q0x + PADQ, y0 + TT + BH + VG, iw, BH)
f.box(*ifa, 'AMU control interface', 'AmuCtrlIO  /  amuRelease', kind='control')
f.box(*ifb, 'CUTE2TL', 'TileLink client to the memory hierarchy', kind='compute')

# Control quadrant
cw2 = (iw - 50) / 2
c_ygjk = (q1x + PADQ, y0 + TT, cw2, BH)
c_task = (q1x + PADQ + cw2 + 50, y0 + TT, cw2, BH)
f.box(*c_ygjk, 'CUTE2YGJK', 'command adapter', kind='control')
f.box(*c_task, 'TaskController', 'macro -> micro inst', kind='control')
# micro-instruction FIFOs (one per stage, depth 4)
fq_y = y0 + TT + BH + VG
fq_w = (iw - 2 * 20) / 3
fifo = {}
for k, nm in enumerate(('Load', 'Compute', 'Store')):
    fx = q1x + PADQ + k * (fq_w + 20)
    f.rect(fx, fq_y, fq_w, BH, 'plain')
    for j in range(1, 4):
        f.line([(fx + fq_w * j / 4, fq_y), (fx + fq_w * j / 4, fq_y + 14)], arrow='none', sw=W_STRUCT,
               color='#909090')
    f.text(fx, fq_y + 14, fq_w, BH - 14, nm + ' FIFO', FS_SUB)
    fifo[nm] = (fx, fq_y, fq_w, BH)

# Storage quadrant
sy = y1 + TT
s_mmu = (q0x + PADQ, sy, iw, BH)
s_ml = (q0x + PADQ, sy + BH + VG, iw, BH)
f.box(*s_mmu, 'LocalMMU', 'address translation, request arbitration', kind='storage')
f.box(*s_ml, 'MemoryLoader', 'AML  /  BML  /  CML', kind='storage')

mr_y = sy + 2 * (BH + VG)
mr_w = (iw - 40) / 2


def matreg(x, title, spec):
    f.rect(x, mr_y, mr_w, MR_H, 'storage')
    f.text(x, mr_y + 4, mr_w, 18, title, FS_MAIN)
    sw = (mr_w - 3 * 10) / 2
    for k in range(2):
        f.box(x + 10 + k * (sw + 10), mr_y + 28, sw, MR_H - 38, f'buf {k}', kind='plain', fs=FS_PIN)
    return (x, mr_y, mr_w, MR_H)


m_ab = matreg(q0x + PADQ, 'AB MatrixReg', '')
m_c = matreg(q0x + PADQ + mr_w + 40, 'C MatrixReg', '')
dc_y = mr_y + MR_H + VG
s_dc = (q0x + PADQ, dc_y, iw, BH)
f.box(*s_dc, 'DataController', 'ADC  /  BDC  /  CDC', kind='storage')

# Compute quadrant: MatrixTE with a PE grid, then AfterOps
te_h = 2 * (BH + VG) + MR_H
te = (q1x + PADQ, sy, iw, te_h)
f.rect(*te, 'compute')
f.text(te[0], te[1] + 6, iw, 18, 'MatrixTE  (outer-product PE array)', FS_MAIN)
n, pe, pg = 6, 22, 8
gw = n * pe + (n - 1) * pg
gx = te[0] + (iw - gw) / 2
gy = te[1] + 34 + (te_h - 34 - gw - 24) / 2
for r in range(n):
    for c in range(n):
        f.rect(gx + c * (pe + pg), gy + r * (pe + pg), pe, pe, 'plain', stroke='#3D6E9E')
f.note(gx + gw / 2, gy + gw + 16, 'each cell: one FReducePE', fs=FS_PIN, align='center')
c_ao = (q1x + PADQ + 90, dc_y, iw - 90, BH)
f.box(*c_ao, 'AfterOps', 'post-processing (passthrough)', kind='compute')

# ---- external blocks
core = (0, ifa[1], EXT_W, BH)
mem = (0, ifb[1], EXT_W, BH)
f.box(*core, 'Scalar core', kind='neutral')
f.box(*mem, 'HBL2 / LLC', kind='neutral')

R = lambda b: b[0] + b[2]
B = lambda b: b[1] + b[3]
MX = lambda b: b[0] + b[2] / 2
MY = lambda b: b[1] + b[3] / 2

# control path (1 px dashed, open arrows)
ctl = dict(sw=W_STRUCT, dashed=True, open_arrow=True)
f.line([(R(core), MY(core) - 8), (ifa[0], MY(core) - 8)], **ctl)
f.line([(ifa[0], MY(core) + 8), (R(core), MY(core) + 8)], **ctl)
f.note((R(core) + cx0) / 2, MY(core) - 20, 'issue', align='center')
f.note((R(core) + cx0) / 2, MY(core) + 20, 'mrelease', align='center')
f.line([(R(ifa), MY(ifa)), (c_ygjk[0], MY(ifa))], **ctl)
f.line([(R(c_ygjk), MY(c_ygjk)), (c_task[0], MY(c_ygjk))], **ctl)
# TaskController -> FIFOs -> stages
by = B(c_task) + VG / 2
f.line([(MX(c_task), B(c_task)), (MX(c_task), by)], arrow='none', sw=W_STRUCT, dashed=True)
f.line([(MX(fifo['Load']), by), (MX(fifo['Store']), by)], arrow='none', sw=W_STRUCT, dashed=True)
for nm in ('Load', 'Compute', 'Store'):
    f.line([(MX(fifo[nm]), by), (MX(fifo[nm]), fq_y)], **ctl)
tx = MX(fifo['Compute'])
f.line([(tx, B(fifo['Compute'])), (tx, te[1])], **ctl)
gut = q0x + QW + GQ / 2
for nm, dx, dy in (('Load', -8, -8), ('Store', 8, 8)):
    fx = MX(fifo[nm])
    f.line([(fx, B(fifo[nm])), (fx, y1 - GQ / 2 + dy), (gut + dx, y1 - GQ / 2 + dy), (gut + dx, MY(s_ml) + dx),
            (R(s_ml), MY(s_ml) + dx)], **ctl)
f.note(gut - 20, (y1 + MY(s_ml)) / 2, 'load / store micro inst', italic=False, vertical=True)

# data path (2 px)
f.line([(R(mem), MY(mem)), (ifb[0], MY(mem))], arrow='both')
f.note((R(mem) + cx0) / 2, MY(mem) - 12, 'TileLink', align='center')
f.note((R(mem) + cx0) / 2, MY(mem) + 12, '512 b', align='center')
mmx = MX(s_mmu)
f.line([(mmx, B(ifb)), (mmx, s_mmu[1])], arrow='both')
f.note(mmx + 8, (B(ifb) + s_mmu[1]) / 2, 'io.mmu2llc', align='left')
f.line([(mmx, B(s_mmu)), (mmx, s_ml[1])], arrow='both')
f.note(mmx + 8, (B(s_mmu) + s_ml[1]) / 2, 'AML / BML / CML requests', align='left')
f.line([(MX(m_ab), B(s_ml)), (MX(m_ab), mr_y)])
f.note(MX(m_ab) + 6, (B(s_ml) + mr_y) / 2, 'A, B', align='left')
f.line([(MX(m_c), B(s_ml)), (MX(m_c), mr_y)], arrow='both')
f.note(MX(m_c) + 6, (B(s_ml) + mr_y) / 2, 'C load / D store', align='left')
f.line([(MX(m_ab), B(m_ab)), (MX(m_ab), dc_y)])
f.line([(MX(m_c), B(m_c)), (MX(m_c), dc_y)], arrow='both')
# DataController <-> compute
f.line([(R(s_dc), MY(s_dc) - 10), (te[0] + 40, MY(s_dc) - 10), (te[0] + 40, B(te))])
gx_mid = q0x + QW + GQ / 2
f.note(gx_mid, MY(s_dc) - 22, 'A, B, C', align='center')
f.line([(MX(c_ao), B(te)), (MX(c_ao), c_ao[1])])
f.note(MX(c_ao) + 6, (B(te) + c_ao[1]) / 2, 'D', align='left')
f.line([(c_ao[0], MY(s_dc) + 10), (R(s_dc), MY(s_dc) + 10)])
f.note(gx_mid, MY(s_dc) + 22, 'D', align='center')

# ---- legend
ly = y1 + bot_h + 24 + 22
end = f.legend(cx0, ly, [('control', 'control'), ('storage', 'storage'), ('compute', 'compute / datapath'),
                         ('neutral', 'outside CUTE')])
x = f.legend_line(end + 40, ly + 6, 'data') + 24
f.legend_line(x, ly + 6, 'command / control', sw=W_STRUCT, dashed=True, open_arrow=True)

f.save()
