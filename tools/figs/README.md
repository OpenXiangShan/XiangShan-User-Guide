# 插图工具链

手册插图统一为 **drawio 原生源文件 → 导出 SVG**。源文件放在仓库根 `figs-src/`，
导出物放在 `docs/zh/figs/`（英文侧经符号链接共用同一套图，因此图只有一份、全英文）。

规范与逐图规格见 [`FIG-GUIDE.md`](FIG-GUIDE.md)。

## 一次性准备：drawio webapp

`drawio-desktop` 是 Electron 应用，无头导出需要 X display，本机没有 Xvfb 也没有
sudo 权限。因此改用 **drawio 官方发行包内含的 webapp + 官方 embed 导出协议**，
由 Playwright 的 Chromium 承载，结果与桌面版导出一致，且不需要 GUI。

```bash
# 1. 取 drawio 发行包（版本可换）
curl -L -o /tmp/drawio.AppImage \
  https://github.com/jgraph/drawio-desktop/releases/download/v26.0.9/drawio-x86_64-26.0.9.AppImage
chmod +x /tmp/drawio.AppImage

# 2. 解包（--appimage-extract 不需要 FUSE）
cd /tmp && /tmp/drawio.AppImage --appimage-extract

# 3. 从 asar 里取出 webapp
npx -y @electron/asar extract /tmp/squashfs-root/resources/app.asar /tmp/drawio-asar
# webapp 位于 /tmp/drawio-asar/drawio/src/main/webapp
```

## 日常使用

```bash
export DRAWIO_WEBAPP=/tmp/drawio-asar/drawio/src/main/webapp

# 导出全部源文件
bash tools/figs/export.sh

# 只导出指定文件
bash tools/figs/export.sh figs-src/memory-path.drawio

# 渲染 PNG 目视检查（评审用，不是交付物）
bash tools/figs/render_png.sh docs/zh/figs/memory-path.svg /tmp/figcheck
```

## 导出后处理（`drawio_export.py` 已自动处理）

drawio 的 SVG 导出有三处会让本仓库的渲染链路出问题，脚本会自动清理：

| 问题 | 现象 | 处理 |
| --- | --- | --- |
| `foreignObject` | 仓库 Makefile 用 `rsvg-convert` 转 PDF，它会渲染 `foreignObject` 并显示 "Text is not SVG - cannot display" 占位文本 | 删除 `foreignObject`，保留同内容的 `<text>` 回退 |
| `light-dark(...)` 颜色函数 | rsvg 不认识，退化成深色分支，把箭头填充渲染成黑块 | 按亮色分支展开 |
| 末尾提示节点 | drawio 附带的 "Text is not SVG" 告警链接会出现在页面上 | 删除该节点 |

因此 `.drawio` 源文件**必须写 `html=0`**，避免生成 `foreignObject`。

## 依赖

- `playwright`（Chromium 已在本机缓存）
- `rsvg-convert`（仓库 PDF 管线同样依赖它）
