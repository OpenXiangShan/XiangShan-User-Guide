#!/usr/bin/env bash
# Build -> export -> machine check -> render PNG for one or more figures.
# usage: bash figs-src/_gen/run.sh <name> [name...]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export DRAWIO_WEBAPP="${DRAWIO_WEBAPP:-/nfs/home/leguochun/tmp/figwork/asar/drawio/src/main/webapp}"
cd "$ROOT"
files=()
for n in "$@"; do
  python3 "figs-src/_gen/fig_${n//-/_}.py"
  files+=("figs-src/$n.drawio")
done
bash tools/figs/export.sh "${files[@]}" 2>&1 | grep -E "ok|FAIL|WARN|Error" || true
for n in "$@"; do
  svg="docs/zh/figs/$n.svg"
  fo=$(grep -c foreignObject "$svg" || true)
  tn=$(grep -c "Text is not SVG" "$svg" || true)
  cjk=$(python3 -c "import re,sys;print(len(re.findall('[一-鿿]',open(sys.argv[1]).read())))" "$svg")
  echo "  check $n: foreignObject=$fo textNotSVG=$tn cjk=$cjk"
  bash tools/figs/render_png.sh "$svg" /tmp/figcheck "${W:-1600}" >/dev/null
done
