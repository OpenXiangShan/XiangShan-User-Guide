#!/usr/bin/env python3
"""把 .drawio（mxGraphModel XML）导出为 SVG。

为什么用 drawio 自带 webapp 而不是 drawio-desktop
--------------------------------------------------
drawio-desktop 是无头导出最直接的工具，但它是 Electron 应用，必须有 X display；
本机既无 Xvfb 也无 sudo 权限安装它。drawio 官方发行包（AppImage）内含完整的
webapp，并实现了官方的 embed 导出协议（postMessage + `{action:"export"}`）。
用 Playwright 的 Chromium 承载这个 webapp，就能拿到与 drawio 桌面版一致的
SVG 导出结果，全程不需要 GUI。

前置
----
1. 取 drawio 发行包并解包出 webapp（一次性）：
     curl -L -o drawio.AppImage <release-url>
     chmod +x drawio.AppImage && ./drawio.AppImage --appimage-extract
     npx -y @electron/asar extract squashfs-root/resources/app.asar asar
   webapp 位于 asar/drawio/src/main/webapp
2. 用 --webapp 指向该目录（或用环境变量 DRAWIO_WEBAPP）。

用法
----
    python3 drawio2svg.py --webapp /path/to/webapp figs/*.drawio
    python3 drawio2svg.py --webapp ... --outdir docs/zh/figs figs/*.drawio

产物与输入同名、扩展名换成 .svg。
"""
import argparse
import asyncio
import functools
import http.server
import json
import os
import socketserver
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent

WRAPPER = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;overflow:hidden;background:#fff}
iframe{border:0;width:1200px;height:900px}
</style></head><body>
<iframe id="f" src="index.html?embed=1&proto=json&spin=1&libraries=0&noSaveBtn=1&noExitBtn=1&saveAndExit=0"></iframe>
<script>
window.__ready = false;
window.__export = function (xml, fmt, transparent) {
  return new Promise(function (resolve, reject) {
    var f = document.getElementById('f');
    var timer = setTimeout(function () { reject(new Error('export timeout')); }, 60000);
    function onMsg(ev) {
      var d;
      try { d = JSON.parse(ev.data); } catch (e) { return; }
      if (d.event === 'init') {
        f.contentWindow.postMessage(JSON.stringify({
          action: 'load', xml: xml, autosave: 0, title: 'fig'
        }), '*');
        return;
      }
      if (d.event === 'load') {
        f.contentWindow.postMessage(JSON.stringify({
          action: 'export', format: fmt, xml: xml,
          spinKey: 'export', transparent: !!transparent
        }), '*');
        return;
      }
      if (d.event === 'export') {
        clearTimeout(timer);
        window.removeEventListener('message', onMsg);
        if (d.data) { resolve(d.data); }
        else { reject(new Error('empty export' + (d.message ? ': ' + d.message : ''))); }
        return;
      }
      if (d.event === 'error') {
        clearTimeout(timer);
        window.removeEventListener('message', onMsg);
        reject(new Error(d.message || 'drawio error'));
      }
    }
    window.addEventListener('message', onMsg);
    /* 若 init 早已发生，直接触发一次握手 */
    try { f.contentWindow.postMessage(JSON.stringify({action: 'hello'}), '*'); } catch (e) {}
  });
};
</script></body></html>
"""


def serve(directory: Path, port: int):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))

    class Q(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = Q(('127.0.0.1', port), handler)
    httpd.log_message = lambda *a, **k: None
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd


async def export_all(pairs, webapp: Path, outdir=None, fmt='svg', transparent=False,
                     timeout_ms=90000, width=1400, height=1000):
    from playwright.async_api import async_playwright

    port = 0
    # 选一个空闲端口
    with socketserver.TCPServer(('127.0.0.1', 0), None) as s:
        port = s.server_address[1]
    httpd = serve(webapp, port)

    (HERE / '_wrapper.html').write_text(WRAPPER, encoding='utf-8')
    wrapper_url = f'http://127.0.0.1:{port}/../_wrapper.html'
    # 把 wrapper 放进 webapp 目录内，保证同源
    (webapp / '_wrapper.html').write_text(WRAPPER, encoding='utf-8')
    wrapper_url = f'http://127.0.0.1:{port}/_wrapper.html'

    results = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=['--no-sandbox', '--force-color-profile=srgb'])

            async def fresh_page():
                """每次导出都用一个全新的页面。

                drawio webapp 在一次导出后会残留状态，导致同一会话里的后续导出
                永远等不到 `export` 事件（表现为 export timeout）。实测：连续导出
                三张时只有第一张成功，单独导出则每张都成功。因此逐张重建页面。
                """
                pg = await browser.new_page(viewport={'width': width, 'height': height},
                                            device_scale_factor=1)
                pg.on('pageerror', lambda e: None)
                await pg.goto(wrapper_url, wait_until='load')
                await pg.wait_for_function(
                    "() => { try { var f=document.getElementById('f');"
                    " return !!(f && f.contentWindow && f.contentWindow.EditorUi); }"
                    " catch(e){ return false; } }", timeout=timeout_ms)
                return pg

            for src in pairs:
                xml = normalise_page(Path(src).read_text(encoding='utf-8'))
                page = await fresh_page()
                try:
                    data = await page.evaluate(
                        '([xml,fmt,tr]) => window.__export(xml,fmt,tr)',
                        [xml, fmt, transparent])
                    out = Path(outdir or Path(src).parent) / (Path(src).stem + f'.{fmt}')
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(postprocess_svg(decode_payload(data)), encoding='utf-8')
                    results.append((src, out, f'{out.stat().st_size} bytes'))
                except Exception as e:
                    results.append((src, None, str(e)[:160]))
                finally:
                    await page.close()
            await browser.close()
    finally:
        httpd.shutdown()
    return results




def postprocess_svg(svg: str) -> str:
    """把 drawio 导出的 SVG 处理成可移植形式。

    两处必须处理，否则仓库既有的渲染链路会出问题：

    1. `<switch>` 里的 `foreignObject`。drawio 用 HTML 排版标签，并同时给出
       `<text>` 回退；但 rsvg（本仓库 Makefile 用 `rsvg-convert` 把 SVG 转 PDF）
       仍会渲染 foreignObject，于是页面上出现 "Text is not SVG" 占位文本。
       删掉 foreignObject，保留同内容的 <text>，两种渲染器结果一致。
    2. `light-dark(...)`。这是较新的 CSS 颜色函数，rsvg 不认识，会退化成黑色
       （深色模式分支），实测把箭头填充渲染成黑块。按亮色分支展开。
    """
    import re

    def strip_foreign(html: str) -> str:
        out, i = [], 0
        open_re = re.compile(r'<foreignObject\b[^>]*>', re.I)
        while True:
            m = open_re.search(html, i)
            if not m:
                out.append(html[i:])
                break
            out.append(html[i:m.start()])
            depth, j = 1, m.end()
            tag = re.compile(r'<(/?)foreignObject\b[^>]*?(/?)>', re.I)
            while depth:
                t2 = tag.search(html, j)
                if not t2:
                    j = len(html)
                    break
                if t2.group(2) == '/':
                    pass
                elif t2.group(1) == '/':
                    depth -= 1
                else:
                    depth += 1
                j = t2.end()
            i = j
        return ''.join(out)

    svg = strip_foreign(svg)

    # drawio 会在末尾附一条“Text is not SVG”的提示链接（当绘制文本不会被
    # 渲染器保留时用它提示用户）。它属于导出器的告警，不是图内容，必须删除，
    # 否则会出现在文档页面上。
    svg = re.sub(
        r'<switch>\s*<g requiredFeatures="http://www\.w3\.org/TR/SVG11/feature#Extensibility"/>'
        r'\s*<a[^>]*>.*?</a>\s*</switch>',
        '', svg, flags=re.S)

    # light-dark(a, b) -> a ；同时清理只含 light-dark 的 style 属性残留
    def ld(m):
        return m.group(1)

    svg = re.sub(r'light-dark\(\s*([^,]+?)\s*,\s*[^)]*\)', ld, svg)
    svg = re.sub(r'\sstyle="\s*"', '', svg)
    svg = re.sub(r'<svg([^>]*?)\scolor-scheme:\s*light dark;', r'<svg\1', svg)
    return svg



def normalise_page(xml: str) -> str:
    """把 pageWidth/pageHeight 调整到能容纳全部内容。

    若内容坐标超出页面尺寸，drawio 的导出会长时间不返回（表现为 export timeout）。
    这里按所有 mxGeometry 的最大范围重设页面尺寸，留一点边距。
    """
    import re
    xs = [int(v) for v in re.findall(r'<mxGeometry[^>]*\sx="(-?\d+)"', xml)]
    ys = [int(v) for v in re.findall(r'<mxGeometry[^>]*\sy="(-?\d+)"', xml)]
    ws = [int(v) for v in re.findall(r'<mxGeometry[^>]*\swidth="(\d+)"', xml)]
    hs = [int(v) for v in re.findall(r'<mxGeometry[^>]*\sheight="(\d+)"', xml)]
    if not xs or not ys:
        return xml
    need_w = max(x + w for x, w in zip(xs, ws)) if ws else max(xs)
    need_h = max(y + h for y, h in zip(ys, hs)) if hs else max(ys)
    m = re.search(r'pageWidth="(\d+)"\s+pageHeight="(\d+)"', xml)
    if not m:
        return xml
    cur_w, cur_h = int(m.group(1)), int(m.group(2))
    if need_w + 20 <= cur_w and need_h + 20 <= cur_h:
        return xml
    new_w, new_h = max(cur_w, need_w + 20), max(cur_h, need_h + 20)
    return xml[:m.start()] + f'pageWidth="{new_w}" pageHeight="{new_h}"' + xml[m.end():]


def decode_payload(data: str) -> str:
    """drawio 的导出结果是 data URI（base64 或 URL 编码），解出真正的 SVG 文本。"""
    import base64
    import urllib.parse
    if not data.startswith('data:'):
        return data
    head, _, body = data.partition(',')
    if ';base64' in head:
        raw = base64.b64decode(body)
        return raw.decode('utf-8')
    return urllib.parse.unquote(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--webapp', default=os.environ.get('DRAWIO_WEBAPP'),
                    help='drawio webapp 目录（含 index.html）')
    ap.add_argument('--outdir')
    ap.add_argument('--format', default='svg', choices=['svg'])
    ap.add_argument('--transparent', action='store_true')
    a = ap.parse_args()
    if not a.webapp or not (Path(a.webapp) / 'index.html').exists():
        sys.exit('需要 --webapp <drawio webapp 目录>（内含 index.html）')
    res = asyncio.run(export_all(a.files, Path(a.webapp), a.outdir, a.format, a.transparent))
    bad = 0
    for src, out, msg in res:
        if out is None:
            bad += 1
            print(f'  FAIL {Path(src).name}: {msg}')
        else:
            print(f'  ok   {Path(src).name} -> {out}  ({msg})')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
