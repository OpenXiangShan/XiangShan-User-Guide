"""Shared layout for the two two-stage translation figures.

Source: docs/zh/memory-model.md 141-173: vsatp drives VS-stage (GVA -> GPA),
hgatp drives G-stage (GPA -> HPA); every guest page-table address produced
by VS-stage is a GPA and must itself go through G-stage before the PTE can
be read; the final GPA is translated once more. Widths: Sv39 GVA 39 b,
Sv39x4 GPA 41 b; Sv48 GVA 48 b, Sv48x4 GPA 50 b; HPA 48 b (memory-model.md
75, Parameters.scala GPAddrBitsSv39x4 / Sv48x4).
"""
from dsl import *


def draw(name, levels, vs_mode, g_mode, gva_w, gpa_w):
    f = Fig(name)
    NW, NH = 74, 34          # walk node
    HG = 34                  # horizontal gap between G nodes
    RG = 30                  # vertical gap between rows (hosts the return lane)
    rows = levels + 1        # one row per VS level + the final GPA
    y0 = 60
    ry = [y0 + r * (NH + RG) for r in range(rows)]
    spine_x = 30
    x_vs = 120
    vs_r = x_vs + NW + 24
    xg0 = vs_r + 104
    gx = [xg0 + k * (NW + HG) for k in range(levels)]
    g_end = gx[-1] + NW
    lane = g_end + 22        # return lane, inside the G container
    g_r = lane + 16

    top = y0 - 30
    bot = ry[-1] + NH + 26
    f.group(spine_x - 22, top, vs_r - spine_x + 22, bot - top, f'VS-stage ({vs_mode})', kind='group',
            dashed=True, fs=FS_MAIN, title_inside=False)
    f.group(xg0 - 18, top, g_r - xg0 + 18, bot - top, f'G-stage ({g_mode}), root from hgatp', kind='group',
            dashed=True, fs=FS_MAIN, title_inside=False)

    # GVA spine
    f.box(spine_x - 18, top + 6, 84, 22, f'GVA, {gva_w} b', kind='plain', fs=FS_SUB, bold=True)
    f.line([(spine_x, top + 28), (spine_x, ry[-1] + NH / 2)], arrow='none', sw=W_DATA)
    for r in range(rows):
        y = ry[r] + NH / 2
        lab = f'VPN[{levels - 1 - r}]' if r < levels else 'offset'
        f.line([(spine_x, y), (x_vs, y)])
        f.note(spine_x + 8, y - 10, lab, align='left')
        if r < levels:
            f.box(x_vs, ry[r], NW, NH, f'VS-L{levels - 1 - r}', kind='compute', fs=FS_SUB)
        else:
            f.box(x_vs, ry[r], NW, NH, 'GPA', kind='plain', fs=FS_SUB, bold=True)
    f.note(x_vs + NW / 2, top + 14, 'vsatp', align='center', italic=True)
    f.line([(x_vs + NW / 2, top + 24), (x_vs + NW / 2, ry[0])], sw=W_STRUCT, dashed=True, open_arrow=True, size=5)

    for r in range(rows):
        y = ry[r] + NH / 2
        kind = 'storage' if r < levels else 'control'
        f.line([(x_vs + NW, y), (gx[0], y)])
        f.note(vs_r + 8, y - 10, 'GPA of PTE' if r < levels else f'GPA, {gpa_w} b', align='left', fs=FS_PIN)
        for k in range(levels):
            f.box(gx[k], ry[r], NW, NH, f'G-L{levels - 1 - k}', kind=kind, fs=FS_SUB)
            if k:
                f.line([(gx[k - 1] + NW, y), (gx[k], y)], size=6)
        if r < levels:
            yr = ry[r] + NH + RG / 2
            f.line([(g_end, y), (lane, y), (lane, yr), (x_vs + NW / 2, yr), (x_vs + NW / 2, ry[r + 1])],
                   sw=W_STRUCT)
    yh = ry[-1] + NH / 2
    hx = g_r + 40
    f.line([(g_end, yh), (hx, yh)])
    f.box(hx, ry[-1], 90, NH, 'HPA, 48 b', kind='plain', fs=FS_SUB, bold=True)

    ly = bot + 24
    f.legend(spine_x - 22, ly, [('compute', 'VS-stage walk step'), ('storage', 'G-stage walk of a PTE address'),
                                ('control', 'G-stage walk of the final GPA')])
    x = f.legend_line(spine_x - 22, ly + 30, 'address being translated')
    f.legend_line(x + 30, ly + 30, 'PTE read at HPA, base for next level', sw=W_STRUCT)
    f.save()
