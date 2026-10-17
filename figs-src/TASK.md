# 任务：重画《香炉峰用户手册》全部插图为 ISCA 顶会学术风格

你是一位擅长体系结构论文插图的专家。本任务要求把一份处理器手册的全部插图
重画为 **drawio 原生源文件 + 导出 SVG**，风格对齐 ISCA / MICRO / ASPLOS 论文插图。

**当前插图被用户明确批评为"太丑、不专业"**，所以本次的标准是"要是能放进顶会论文
的水平"。请把美观与专业当作一等目标，不是附加项。

---

## 1. 必读：完整规范

`/nfs/home/leguochun/xsai-user-guide/tools/figs/FIG-GUIDE.md`

这份 341 行的规范给出：配色表、字号表、排版原则、drawio 生成规则、
**"为什么图看起来不专业"的反面清单与正面手法**、程序化布局建议、
以及**逐图的详细规格**（每张图画什么、依据哪段正文、关键要求）。

**请完整读完再动手。** 下面只做提要。

### 硬性要求（不满足即返工）

1. **图中不得出现任何中文**——一个汉字都不行。全部英文术语。
2. 字体统一 Helvetica；无阴影、无渐变；`rounded=0`。
3. **`.drawio` 必须写 `html=0`**——否则 drawio 生成 `foreignObject`，
   而本仓库的 PDF 管线（`rsvg-convert`）会显示 "Text is not SVG" 占位文本。
4. 字号三级：16px（组标题）/ 14px（主标签）/ 12px（次级）/ 11px（位域·引脚）。
5. 颜色只用于编码语义，且全套图语义一致（配色表见规范第 2 节）。
6. 白底、对齐、等距、留白充足、线不穿框、文字不溢出。
7. 交付 `figs-src/<name>.drawio` + `docs/zh/figs/<name>.svg`（导出物）。

### 强烈建议：用程序生成坐标

规范第 4.5 节说明了理由：手写 x/y 靠估算是"丑"的主因。
建议在 `figs-src/_gen/` 下写一个共享样式/布局模块（`dsl.py`）+ 每图一个脚本，
坐标由网格算出。**全套图共用同一模块，观感才能统一成一个家族**——
这是手册插图专业度的关键，单张好看不如一套统一。

简单图或位域图可以直接手写 XML，但位域图必须共用一个绘制函数。

---

## 2. 工具链（已就绪）

需要设置 drawio webapp 路径（首次）：

```bash
export DRAWIO_WEBAPP=/nfs/home/leguochun/tmp/figwork/asar/drawio/src/main/webapp
```

导出（写 `.drawio` 后运行）：

```bash
cd /nfs/home/leguochun/xsai-user-guide
bash tools/figs/export.sh figs-src/<name>.drawio          # 导出单个
bash tools/figs/export.sh                                  # 导出 figs-src 下全部
```

渲染 PNG 供**目视检查**（不是交付物）：

```bash
bash tools/figs/render_png.sh docs/zh/figs/<name>.svg /tmp/figcheck
```

`drawio_export.py` 已自动处理三处兼容问题（`foreignObject`、`light-dark()`
颜色函数、drawio 附加的提示节点）——你不需要关心，但要**保持 `html=0`**。

背景见 `tools/figs/README.md`。

---

## 3. 强制工作流：每张图迭代 ≥3 轮，且必须真的看图

对**每一张**图：

1. 写/生成 `.drawio`
2. `bash tools/figs/export.sh figs-src/<name>.drawio`
3. `bash tools/figs/render_png.sh docs/zh/figs/<name>.svg /tmp/figcheck`
4. **用 Read 工具读取那张 PNG，真的看它**（Claude Code 的 Read 支持读图）
5. 逐项自查（规范第 3.5 节末尾的自查问句），把发现的问题列出来
6. 修，回到第 2 步

**至少 3 轮**（草稿 → 修 → 再修 → 定稿）。若某一轮"没发现问题"，
说明看的不够细——请更严格：把 PNG 缩到 25% 看层次，遮住文字看信息流，
逐条核对对齐与间距。

**收敛标准**：连续一轮目视检查找不到任何排版或语义问题。

同时做两类检查：
- **机器检查**：导出后的 SVG 里 `grep -c foreignObject` 应为 0、
  不含 `Text is not SVG`、不含任何 CJK 字符（正则 `[\u4e00-\u9fff]`）。
- **目视检查**：如上。

---

## 4. 要画的图（25 张）

### 优先组：手册自身的图（10 张，先完成这批）

| 图名 | 内容 | 正文出处 |
| --- | --- | --- |
| `stack-full` | AI 软硬件栈 6 层 | `docs/zh/start/stack.md` 8–22 行 |
| `delta-overview` | 相对昆明湖 V2R2 的增量 | `docs/zh/start/stack.md` 23–27 行 |
| `cute-subsystems` | CUTE 四个子系统 | `docs/zh/hardware/microarchitecture.md` 10–20 行 |
| `load-compute-store` | 三阶段流水 + 双缓冲 | `docs/zh/hardware/microarchitecture.md` 30–36 行 |
| `memory-path` | 矩阵访存路径 | `docs/zh/hardware/memory.md` 55–70 行 |
| `hpm-flow` | HPM 数据流 | `docs/zh/hardware/pmu.md` 30–50 行 |
| `register-map` | 3 位选择子 → 寄存器对映射 | `docs/zh/isa/registers.md` 70–82 行 |
| `sdk-layout` | SDK 组件构成 | `docs/zh/sdk/layout.md` 8–20 行 |
| `framework-seam` | 三框架接缝对比 | `docs/zh/software/frameworks.md` 80–95 行 |
| `verify-ladder` | 验证阶梯 | `docs/zh/software/simulators.md` 25–35 行 |

**这几张是"体系结构图"的主体，用户特别强调要有学术水准。**
每张的详细规格（画什么、布局、要点、配色）见规范第 6.1–6.10 节。

### 次优先组：RISC-V 规范类图（12 张）

位域与地址翻译图，按规范手册的严谨度画，**位域图必须共用同一绘制函数**
以保证 12 张之间完全一致。见规范第 6.11 节（含每张的字段定义与统一画法）。

`Sv39vaddr`、`Sv48vaddr`、`sv39x4`、`sv48x4`、`pte`、`vsatp`、`pmp`、`pma`、
`pmbt`、`paddr`、`two-stage-translation-sv39-sv39x4`、`two-stage-translation-sv48-sv48x4`

注意：`pmp`/`pma`/`paddr` 的地址位宽以**正文更正后的值**为准（PMP/PMA 地址字段
46 位、`[63:46]` 未实现；物理地址 48 位），不要沿用旧图的 36 位。

### 末优先组：调试与多核图（3 张）

`kmh-multicore`（昆明湖多核框图，最复杂，参考 ISCA SoC 框图风格）、
`debugmodule`（Debug module 拓扑）、`debug2harts`（调试器与 hart 连接及时钟域）。
见规范第 6.12 节。

---

## 5. 素材与事实来源

- **技术事实**：以正文为准。正文在 `/nfs/home/leguochun/xsai-user-guide/docs/zh/`。
  规格里给了每张图对应的正文行号。
- **源码**（需要更细的微架构细节时）：`/nfs/home/leguochun/tmp/xsai-env1/`
  （RTL 在 `XSAI/`，CUTE 设计文档在 `docs/CUTE-Design-Doc/`）
- **现有图**（仅作参考，不要照抄其风格）：`docs/zh/figs/`
- 若规格描述与正文冲突，**以正文/源码为准**，并在交付说明里指出。

---

## 6. 进度与交付

**边做边落盘**，不要憋到最后：

- 每完成一张图，就在 `/nfs/home/leguochun/xsai-user-guide/figs-src/PROGRESS.md`
  追加一行：图名 / 状态 / 迭代轮数 / 本轮改了什么 / 遗留问题。
- 每张图完成后**立即** `git add` 对应的 `.drawio` 与 `.svg`（不要 commit，
  留给我统一提交）—— 只需 `git add`，或用 `git status` 确认文件已写入即可。

最终回复里逐图列出：
- 图名、源文件路径、导出路径、迭代轮数
- 每轮改了什么（一句话）
- 依据的正文出处
- 仍存在的取舍或不确定处

**不要**声称"已检查"却没真的看过那张 PNG。我会用独立渲染复核每张图。

---

## 7. 开始

1. 读 `tools/figs/FIG-GUIDE.md`（全文）
2. 读优先组 10 张图对应的正文段落
3. 先做 `dsl.py`（若采用程序化布局）
4. 从 `stack-full` 与 `delta-overview` 开始——这两张是"门面图"，
   先做好它们以确立全套的视觉语言
5. 逐张推进，每张 ≥3 轮迭代 + 目视检查

现在开始。先回一句：你已读完规范，准备采用哪种布局方式（程序化生成 / 手写 XML），
以及从哪张图开始。

---

## 8. 参考素材（本次新增，**必读必看**）

用户的判断是对的：抄真实论文的图，比凭空设计专业得多。

**每张手册图都配了结构最接近的真实论文插图**，位置：

```
figs-src/refs/<图名>/          例：figs-src/refs/hpm-flow/2608.04247__Centralized-PMU-HeteroSoC__Fig2.png
```

**逐图的"看什么、学什么"写在 `figs-src/refs/README.md`**，请完整读它。

工作方式改为：

1. **先 Read 参考图**（用 Read 工具看 PNG），理解它的布局手法、配色克制程度、
   线宽用法、标注方式、留白比例。
2. **再用 drawio 重画成我们自己的内容**——抄的是**结构手法**，不是内容。
3. 对照参考图检查自己的图：
   - 我的用色是不是比它多？（顶会图多是黑白灰 + 1~2 个强调色）
   - 我的线宽有没有分级？（数据通路 vs 控制）
   - 我的对齐、间距、留白是否达到它的水准？
   - 我的标注位置是否同样贴近元素？

素材出自 21 篇真实论文（含 ISCA/OSDI/JSSC 等），出处清单见 refs/README.md 末尾。
其中 `2409.00661` 是本团队自己的香山 Nanhu LLM 加速论文。

**特别注意几条从参考图里能直接看出的共性**（这是"专业感"的真正来源）：

- **克制用色**：现在我们图里 6 个模块 6 种颜色，这是业余感的主要来源。
  参考图基本是白底 + 灰阶 + 1 个强调色。
- **靠布局而非颜色表达结构**：分区用虚线框或浅底色，不用彩色填充堆叠。
- **位域图用同色系深浅**而非彩虹色，且 12 张必须完全一致。
- **时间轴横放**来表达流水/重叠（`load-compute-store`、`verify-ladder` 的关键手法）。
- **严格对齐**：平行结构左右边缘严格对齐。
