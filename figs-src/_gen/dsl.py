"""Thin drawio XML DSL shared by every figure of the XSAI manual.

All figures import this module so that palette, font sizes, stroke widths and
arrow styles are identical across the set. Coordinates are absolute pixels;
figure scripts compute them from grids, never by eye.

Rules baked in (see tools/figs/FIG-GUIDE.md):
  * html=0 everywhere (no foreignObject in the exported SVG)
  * Helvetica, sizes 16 / 14 / 12 / 11 only
  * no shadow, no gradient, rounded=0
  * edges are drawn as explicit polylines (edgeStyle=none + waypoints), so the
    route is exactly what the script says -- drawio never re-routes them.
"""
from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import ImageFont

# ---------------------------------------------------------------- palette
# (fill, stroke) per semantic class. Only these colours are allowed.
PAL = {
    'compute': ('#DAE8F4', '#3D6E9E'),
    'storage': ('#E1EFD9', '#5E8C4A'),
    'control': ('#F6E3CE', '#B5713A'),
    'neutral': ('#EFEFEF', '#909090'),
    'new':     ('#F8D7DA', '#A94442'),
    'plain':   ('#FFFFFF', '#333333'),   # black-and-white module
    'group':   ('none',    '#B0B0B0'),   # logical grouping container
    'panel':   ('#FAFAFA', '#B0B0B0'),   # very light background container
}
INK = '#222222'      # text and primary lines
NOTE = '#555555'     # annotations next to lines
FONT = 'Helvetica'

# font sizes -- the only four allowed
FS_GROUP, FS_MAIN, FS_SUB, FS_PIN = 16, 14, 12, 11

# stroke widths
W_STRUCT, W_DATA = 1, 2

_FONTDIR = '/usr/share/fonts/opentype/urw-base35/'
_fonts = {}


def _font(size, bold=False, italic=False):
    key = (size, bold, italic)
    if key not in _fonts:
        name = 'NimbusSans-' + ({(0, 0): 'Regular', (1, 0): 'Bold',
                                  (0, 1): 'Italic', (1, 1): 'BoldItalic'}[(int(bold), int(italic))])
        _fonts[key] = ImageFont.truetype(_FONTDIR + name + '.otf', size)
    return _fonts[key]


def text_w(s, size=FS_MAIN, bold=False, italic=False):
    """Rendered width of the longest line of `s` in px (Helvetica metrics)."""
    f = _font(size, bold, italic)
    return max(f.getlength(line) for line in s.split('\n'))


def text_h(s, size=FS_MAIN):
    return len(s.split('\n')) * size * 1.2


class Fig:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self.n = 2
        self.warn = []
        self.bbox = [1e9, 1e9, -1e9, -1e9]

    # ------------------------------------------------------------ internals
    def _id(self):
        self.n += 1
        return f'c{self.n}'

    def _grow(self, x, y, w=0, h=0):
        b = self.bbox
        b[0] = min(b[0], x); b[1] = min(b[1], y)
        b[2] = max(b[2], x + w); b[3] = max(b[3], y + h)

    def _vertex(self, x, y, w, h, value, style):
        cid = self._id()
        self.cells.append(
            f'<mxCell id="{cid}" value="{_val(value)}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" as="geometry"/></mxCell>')
        self._grow(x, y, w, h)
        return cid

    def _check_fit(self, label, w, h, fs, bold, italic, pad=6):
        if not label:
            return
        tw = text_w(label, fs, bold, italic)
        th = text_h(label, fs)
        if tw > w - 2 * pad or th > h:
            self.warn.append(f'overflow: {label!r} needs {tw:.0f}x{th:.0f}, box {w:.0f}x{h:.0f}')

    # ------------------------------------------------------------ primitives
    def rect(self, x, y, w, h, kind='plain', dashed=False, sw=W_STRUCT, fill=None, stroke=None):
        f, s = PAL[kind]
        style = (f'rounded=0;html=0;shadow=0;fillColor={fill or f};strokeColor={stroke or s};'
                 f'strokeWidth={sw};' + ('dashed=1;dashPattern=4 3;' if dashed else '') +
                 'fontFamily=Helvetica;')
        return self._vertex(x, y, w, h, '', style)

    def text(self, x, y, w, h, label, fs=FS_MAIN, bold=False, italic=False, color=INK,
             align='center', valign='middle', vertical=False, check=True):
        fstyle = (1 if bold else 0) | (2 if italic else 0)
        style = (f'text;html=0;fontFamily={FONT};fontSize={fs};fontStyle={fstyle};fontColor={color};'
                 f'align={align};verticalAlign={valign};spacing=0;spacingLeft=0;spacingRight=0;'
                 f'spacingTop=0;spacingBottom=0;strokeColor=none;fillColor=none;'
                 + ('horizontal=0;' if vertical else ''))
        if check:
            if vertical:
                self._check_fit(label, h, w, fs, bold, italic, pad=0)
            else:
                self._check_fit(label, w, h, fs, bold, italic, pad=0)
        return self._vertex(x, y, w, h, label, style)

    def box(self, x, y, w, h, title='', sub='', kind='plain', fs=FS_MAIN, bold=False,
            dashed=False, sw=W_STRUCT, sub_fs=FS_SUB, italic_sub=False, fill=None, stroke=None,
            gap=3):
        """Filled module with a centred title and optional smaller spec line(s)."""
        self.rect(x, y, w, h, kind, dashed, sw, fill, stroke)
        if not sub:
            self._check_fit(title, w, h, fs, bold, False)
            self.text(x, y, w, h, title, fs, bold, check=False)
        else:
            th, sh = text_h(title, fs), text_h(sub, sub_fs)
            tot = th + gap + sh
            ty = y + (h - tot) / 2
            self._check_fit(title, w, h, fs, bold, False)
            self._check_fit(sub, w, h, sub_fs, False, italic_sub)
            self.text(x, ty, w, th, title, fs, bold, check=False)
            self.text(x, ty + th + gap, w, sh, sub, sub_fs, italic=italic_sub, color=NOTE if kind == 'plain' else INK,
                      check=False)
        return (x, y, w, h)

    def group(self, x, y, w, h, title='', kind='group', dashed=True, fs=FS_GROUP, bold=True,
              title_align='left', pad=10, sw=W_STRUCT, title_inside=True, italic=False):
        self.rect(x, y, w, h, kind, dashed, sw)
        if title:
            th = text_h(title, fs)
            if title_inside:
                ty = y + pad - 2
            else:
                ty = y - th - 4
            if title_align == 'left':
                self.text(x + pad, ty, w - 2 * pad, th, title, fs, bold, italic, align='left')
            elif title_align == 'right':
                self.text(x + pad, ty, w - 2 * pad, th, title, fs, bold, italic, align='right')
            else:
                self.text(x, ty, w, th, title, fs, bold, italic)
        return (x, y, w, h)

    def line(self, pts, arrow='end', sw=W_DATA, dashed=False, color=INK, open_arrow=False, size=None):
        """Polyline through `pts` [(x,y),...]. arrow: 'end' | 'start' | 'both' | 'none'."""
        head = 'open' if open_arrow else 'block'
        fill = 0 if open_arrow else 1
        sz = size or (7 if sw >= 2 else 6)
        end = head if arrow in ('end', 'both') else 'none'
        start = head if arrow in ('start', 'both') else 'none'
        style = (f'edgeStyle=none;rounded=0;html=0;strokeColor={color};strokeWidth={sw};'
                 f'endArrow={end};endFill={fill};startArrow={start};startFill={fill};'
                 f'endSize={sz};startSize={sz};jumpStyle=none;'
                 + ('dashed=1;dashPattern=4 3;' if dashed else ''))
        cid = self._id()
        (sx, sy), (tx, ty) = pts[0], pts[-1]
        mids = ''.join(f'<mxPoint x="{_n(px)}" y="{_n(py)}"/>' for px, py in pts[1:-1])
        arr = f'<Array as="points">{mids}</Array>' if mids else ''
        self.cells.append(
            f'<mxCell id="{cid}" value="" style="{style}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{_n(sx)}" y="{_n(sy)}" as="sourcePoint"/>'
            f'<mxPoint x="{_n(tx)}" y="{_n(ty)}" as="targetPoint"/>{arr}</mxGeometry></mxCell>')
        for px, py in pts:
            self._grow(px, py)
        return cid

    def note(self, x, y, label, fs=FS_PIN, align='left', italic=False, color=NOTE, bold=False,
             valign='middle', vertical=False):
        """Free annotation anchored at (x, y): align picks which edge sits on x; y is the centre."""
        w = text_w(label, fs, bold, italic) + 2
        h = text_h(label, fs)
        if vertical:
            w, h = h, w
            return self.text(x - w / 2, y - h / 2, w, h, label, fs, bold, italic, color, 'center',
                             'middle', vertical=True, check=False)
        bx = {'left': x, 'center': x - w / 2, 'right': x - w}[align]
        by = {'middle': y - h / 2, 'top': y, 'bottom': y - h}[valign]
        return self.text(bx, by, w, h, label, fs, bold, italic, color, align, 'middle', check=False)

    def legend(self, x, y, items, sw=18, sh=12, gap=24, fs=FS_SUB):
        """Horizontal legend: items = [(kind, label, dashed?)]."""
        cx = x
        for it in items:
            kind, label = it[0], it[1]
            dashed = it[2] if len(it) > 2 else False
            self.rect(cx, y, sw, sh, kind, dashed)
            self.note(cx + sw + 6, y + sh / 2, label, fs=fs, color=INK)
            cx += sw + 6 + text_w(label, fs) + gap
        return cx - gap

    def legend_line(self, x, y, label, sw=W_DATA, dashed=False, open_arrow=False, length=34, fs=FS_SUB):
        self.line([(x, y), (x + length, y)], sw=sw, dashed=dashed, open_arrow=open_arrow)
        self.note(x + length + 6, y, label, fs=fs, color=INK)
        return x + length + 6 + text_w(label, fs)

    # ------------------------------------------------------------ output
    def xml(self, margin=40, frame=16):
        # drawio crops the export to the content bounds; an invisible white frame
        # gives every figure the same outer margin.
        b = self.bbox
        self.cells.insert(0,
            f'<mxCell id="frame" value="" style="rounded=0;html=0;fillColor=#FFFFFF;strokeColor=none;" '
            f'vertex="1" parent="1"><mxGeometry x="{_n(b[0] - frame)}" y="{_n(b[1] - frame)}" '
            f'width="{_n(b[2] - b[0] + 2 * frame)}" height="{_n(b[3] - b[1] + 2 * frame)}" as="geometry"/></mxCell>')
        dx, dy = margin - self.bbox[0], margin - self.bbox[1]
        W = int(self.bbox[2] - self.bbox[0] + 2 * margin)
        H = int(self.bbox[3] - self.bbox[1] + 2 * margin)

        def shift(m):
            k, v = m.group(1), float(m.group(2))
            return f'{k}="{_n(v + (dx if k == "x" else dy))}"'

        body = '\n    '.join(re.sub(r'\b([xy])="(-?[\d.]+)"', shift, c) for c in self.cells)
        return (f'<mxfile host="drawio"><diagram name="{self.name}" id="{self.name}">'
                f'<mxGraphModel dx="{W}" dy="{H}" grid="0" gridSize="10" guides="0" tooltips="0" '
                f'connect="0" arrows="1" fold="0" page="1" pageScale="1" pageWidth="{W}" '
                f'pageHeight="{H}" background="#FFFFFF" math="0" shadow="0">\n  <root>\n'
                f'    <mxCell id="0"/>\n    <mxCell id="1" parent="0"/>\n    {body}\n'
                f'  </root>\n</mxGraphModel></diagram></mxfile>\n')

    def save(self, outdir=None):
        out = Path(outdir or Path(__file__).resolve().parent.parent) / f'{self.name}.drawio'
        out.write_text(self.xml(), encoding='utf-8')
        for w in self.warn:
            print(f'  WARN {self.name}: {w}')
        if re.search(r'[一-鿿]', out.read_text(encoding='utf-8')):
            raise SystemExit(f'{self.name}: CJK character in figure')
        return out


def _n(v):
    v = round(v, 2)
    return str(int(v)) if v == int(v) else str(v)


def _val(s):
    return escape(s, {'"': '&quot;', '\n': '&#xa;'})


# ------------------------------------------------------------------ bitfield
# Single drawing routine for every register / address layout figure.
BF_ROW_H = 30        # height of the field bar
BF_LABEL_GAP = 4


def bitfield(fig, x, y, fields, width, name=None, show_widths=True, min_w=26,
             name_gap=14, alternate=True):
    """Draw one horizontal bit-field bar, MSB on the left.

    fields: list of dicts {hi, lo, name, kind}; kind in {'field', 'reserved', 'zero', 'ext'}.
      'reserved' / 'zero' / 'ext' are drawn grey with italic names.
    Field widths: proportional to bit count with a floor of `min_w`, then the
    remainder distributed proportionally so the bar is exactly `width` wide.
    Bit numbers are printed above (hi at the left edge, lo at the right edge),
    the field width in bits below. Returns list of (x0, x1) per field.
    """
    bits = [f['hi'] - f['lo'] + 1 for f in fields]
    # iterative floor allocation
    ws = [None] * len(fields)
    free = width
    rest = list(range(len(fields)))
    while True:
        tot = sum(bits[i] for i in rest)
        changed = False
        for i in list(rest):
            w = free * bits[i] / tot
            if w < min_w:
                ws[i] = min_w
                free -= min_w
                rest.remove(i)
                changed = True
        if not changed:
            for i in rest:
                ws[i] = free * bits[i] / tot
            break
    spans = []
    cx = x
    # alternate from the LSB so the lowest field has the same fill in every figure
    nf = sum(1 for f in fields if f.get('kind', 'field') not in ('reserved', 'zero', 'ext'))
    ti = nf - 1
    for f, w, nb in zip(fields, ws, bits):
        grey = f.get('kind', 'field') in ('reserved', 'zero', 'ext')
        if grey:
            fill = PAL['neutral'][0]
        else:
            fill = PAL['compute'][0] if (ti % 2 == 0 or not alternate) else '#FFFFFF'
            ti -= 1
        fig.rect(cx, y, w, BF_ROW_H, 'plain', fill=fill, stroke=INK)
        fs = FS_SUB if text_w(f['name'], FS_SUB, italic=grey) <= w - 6 else FS_PIN
        fig.text(cx, y, w, BF_ROW_H, f['name'], fs, italic=grey)
        # bit numbers above
        ty = y - BF_LABEL_GAP - FS_PIN * 1.2
        if f['hi'] == f['lo'] or w < 46:
            lab = str(f['hi']) if f['hi'] == f['lo'] else f"{f['hi']}:{f['lo']}"
            fig.text(cx, ty, w, FS_PIN * 1.2, lab, FS_PIN, color=NOTE)
        else:
            fig.text(cx + 3, ty, w / 2, FS_PIN * 1.2, str(f['hi']), FS_PIN, color=NOTE, align='left')
            fig.text(cx + w / 2 - 3, ty, w / 2, FS_PIN * 1.2, str(f['lo']), FS_PIN, color=NOTE, align='right')
        if show_widths:
            fig.text(cx, y + BF_ROW_H + BF_LABEL_GAP, w, FS_PIN * 1.2, str(nb), FS_PIN, color=NOTE)
        spans.append((cx, cx + w))
        cx += w
    if name:
        fig.text(x + width + name_gap, y, text_w(name, FS_MAIN, bold=True) + 2, BF_ROW_H, name,
                 FS_MAIN, bold=True, align='left')
    return spans


def bf_brace(fig, x0, x1, y, label, depth=6):
    """Square bracket under a span of a bit-field bar, label centred below."""
    fig.line([(x0 + 1, y), (x0 + 1, y + depth), (x1 - 1, y + depth), (x1 - 1, y)], arrow='none', sw=W_STRUCT,
             color=NOTE)
    fig.note((x0 + x1) / 2, y + depth + 10, label, align='center', italic=True)


BF_W = 900           # common bar width for every address / register layout
