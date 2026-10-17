#!/usr/bin/env bash
# 把导出的 SVG 渲染为 PNG，供目视检查排版（评审用，不作为交付物）。
# 用法: bash tools/figs/render_png.sh docs/zh/figs/foo.svg [输出目录] [宽度]
set -euo pipefail
SVG="$1"; OUTDIR="${2:-/tmp/figcheck}"; W="${3:-1600}"
mkdir -p "$OUTDIR"
rsvg-convert -w "$W" -o "$OUTDIR/$(basename "${SVG%.svg}").png" "$SVG"
echo "$OUTDIR/$(basename "${SVG%.svg}").png"
