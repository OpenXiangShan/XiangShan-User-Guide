#!/usr/bin/env bash
# 把 figs-src/*.drawio 导出为 SVG 到 docs/zh/figs/（英文侧经符号链接共用同一套图）。
#
# 用法:
#   bash tools/figs/export.sh                 # 导出 figs-src 下全部
#   bash tools/figs/export.sh figs-src/a.drawio figs-src/b.drawio
#
# 依赖 drawio 官方 webapp（一次性准备，见 tools/figs/README.md）：
#   export DRAWIO_WEBAPP=/path/to/drawio/webapp
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEBAPP="${DRAWIO_WEBAPP:-/nfs/home/leguochun/tmp/figwork/asar/drawio/src/main/webapp}"
if [ ! -f "$WEBAPP/index.html" ]; then
  echo "找不到 drawio webapp: $WEBAPP" >&2
  echo "请设置 DRAWIO_WEBAPP 指向含 index.html 的 drawio webapp 目录" >&2
  exit 2
fi
ARGS=("$@")
if [ ${#ARGS[@]} -eq 0 ]; then
  shopt -s nullglob
  ARGS=("$ROOT"/figs-src/*.drawio)
fi
[ ${#ARGS[@]} -eq 0 ] && { echo "figs-src 下没有 .drawio" >&2; exit 1; }
exec python3 "$ROOT/tools/figs/drawio_export.py" --webapp "$WEBAPP" --outdir "$ROOT/docs/zh/figs" "${ARGS[@]}"
