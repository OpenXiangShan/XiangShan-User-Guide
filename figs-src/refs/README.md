# 参考素材索引

我们画图时不凭空设计布局：每张手册图都对应一两张结构最接近的真实论文插图，先看参考图理解布局手法，再用 drawio 重画成自己的内容。

**本目录只保留这份索引，不放论文原图。** 原图是第三方版权素材，不随仓库发布。需要看原图时，按下表 arXiv 编号自行获取：

```bash
# 论文页面
https://arxiv.org/abs/<arXiv 编号>
# PDF 直链（用 pdftoppm / pdftotext -bbox 提取指定图）
https://arxiv.org/pdf/<arXiv 编号>
```

下表给出每张手册图的参考对象、图号与要学的手法。

## 门面图

| 手册图 | 参考论文 | 图 | 学什么 |
| --- | --- | --- | --- |
| `stack-full` | 1802.04799 TVM ★ | Fig2 | 分层栈的画法：层间等高、等宽、间距一致，每层左侧是层名、右侧是该层的具体实例（小字或异色子块）。用"箭头穿层"表示数据流经各层，比单纯堆叠信息量大 |
| `stack-full` | 2502.21027 RISC-V Multicore + GPU SoC | Fig1 | 同类分层栈的另一种排布 |
| `delta-overview` | 1911.09925 Gemmini | Fig5 | 用**虚线框**划分"宿主机部分"与"加速器部分"，两部分的部件在同一张图里对比，边界一眼可见。我们用它区分"继承自昆明湖"与"香炉峰新增"。继承部分用中性灰，新增部分用强调色，图内给 2 项图例 |
| `cute-subsystems` | 2111.15024 可配置 HW/SW 栈 ★最佳 | Fig1 | **微架构图的范本**：模块大小按重要性分级，存储用窄条、计算用方块、控制用细线，数据流用带方向的粗线穿过各模块，左侧标注状态机缩写。整体黑白灰 + 极少彩色，靠布局和线宽表达结构 |
| `cute-subsystems` | 1807.07928 Eyeriss v2 | Fig6 | PE 阵列 + 多级存储的画法 |
| `load-compute-store` | 2604.27808 AME-PIM ★最佳 | Fig5 | 把**时间轴横放**，每个周期一列，色块表示不同阶段同时进行。用时间轴体现重叠，比画三个循环箭头强得多 |
| `load-compute-store` | 2111.15024 | Fig12 | 双缓冲带来的周期数减少，柱状对比 |
| `memory-path` | 2506.10921 Zero-Stall MatMul ★最佳 | Fig3 | 多 bank 存储器画成细长条阵列；DMA 与核的请求路径分开画，用不同线宽区分带宽，清楚表达"两条独立通路" |
| `hpm-flow` | 2608.04247 集中式 PMU ★最贴合 | Fig2 | 结构极简：左侧各来源（带编号端口）、中间互连（一个矩形）、右侧事件过滤器与计数器块，输出箭头标 Overflow Interrupt Lines。几乎没有颜色，全靠线框与箭头方向表达数据流 |
| `register-map` | 2512.21473 ARM SME GEMM | Fig1 | 矩阵/寄存器与运算的对应用**几何对齐**表达——同高的色块相乘得结果色块，不用箭头也能读懂 |
| `sdk-layout` | 2111.15024 / 1802.04799 TVM | Fig1 / Fig2 | 组件构成图的分组方式与层次标注 |
| `framework-seam` | 2604.13523 TensorLift | Fig3 | **对比三个目标**的理想模板：横向三列，每列内部结构相同、只有替换点位置不同，横向一扫即可比较 |
| `framework-seam` | 1802.04799 TVM | Fig20 | 编译器到硬件的层次 |
| `verify-ladder` | 2504.05284 FERIVer ★最贴合 | Fig5 | 用**横向时间轴**对比四种手段，每个手段一行，色块表示执行时间。用时间轴体现精度与速度的权衡，而不是画成台阶 |
| `verify-ladder` | 2508.02236 GSIM | Fig6 | 性能对比的归一化处理 |

## 位域与地址翻译图（12 张）

| 手册图 | 参考论文 | 图 | 学什么 |
| --- | --- | --- | --- |
| `Sv39vaddr`、`Sv48vaddr`、`sv39x4`、`sv48x4`、`paddr`、`pmp`、`pma`、`pmbt`、`pte` | 2406.17796 RISC-V Hypervisor Ext | Fig2 | **位域图的标准画法**：横向长条按字段切分，相邻字段用不同深浅的**同色系**（不是彩虹色）区分，位号标在条上方，字段名居中 |
| `two-stage-translation-sv39-sv39x4`、`two-stage-translation-sv48-sv48x4` | 2406.17796 | Fig3 ★最佳 | 两阶段翻译：用灰色区域表示无效/保留位，用箭头把虚拟地址的字段映射到物理地址的对应字段 |
| `vsatp` | 2406.17796 | Fig1 | trap 委托关系的画法 |

**关键**：全部 12 张位域图共用同一个绘制函数与同一套配色，否则放在一起会明显参差。参考图里这种一致性是刻意的。

## SoC 与调试图

| 手册图 | 参考论文 | 图 | 学什么 |
| --- | --- | --- | --- |
| `kmh-multicore` | 2305.08415 Marsellus ★最佳 | Fig1 | SoC 框图的典范：用**底色分区表示电源域/时钟域**（浅灰 = always-on、白 = SoC、橙 = cluster），外设沿边缘排布，总线用粗横条，处理器核用重复的小方块阵列。信息密度高但毫无杂乱，靠的是严格网格与统一方块尺寸 |
| `kmh-multicore` | 2009.07723 Rocket TLB 层次 | Fig1 | 同类 SoC 分区画法 |
| `debugmodule`、`debug2harts` | 2504.01972 RISC-V Trace in CVA6 | Fig1 | 调试链路图：左侧外部主机 → 中间适配层 → 右侧芯片内部模块，用虚线框表示芯片/域边界，协议名标在连线上 |

## 通用要求

这些是从参考图里直接看出来的共性，比单张图的手法更重要。

1. **克制用色**：顶会插图多是黑白灰 + 1~2 个强调色，颜色只用来编码类别。六个模块六种颜色是"业余感"的主要来源。
2. **线宽分级**：数据通路 2px、控制 1px、虚线表示可选或边界。
3. **标注贴近元素**：位号、位宽、协议名紧邻元素，字号小但清晰。
4. **留白充足**：元素之间留白不少于元素高度的 40%。
5. **不用渐变、阴影、立体**：参考图全是平的。
6. **对齐严格**：所有平行结构严格对齐，"整齐"来自这里。
7. **图注在图外**：图内不写图题。

## 论文清单

上表用到以及曾经参考过的论文，便于追溯。

| arXiv | 论文 |
| --- | --- |
| 1704.04760 | In-Datacenter Performance Analysis of a TPU (ISCA'17) |
| 1802.04799 | TVM: An Automated End-to-End Optimizing Compiler (OSDI'18) |
| 1807.07928 | Eyeriss v2 (JETCAS'19) |
| 1911.09925 | Gemmini (DAC'21) |
| 2009.07723 | Configurable TLB Hierarchy for Rocket Chip |
| 2111.15024 | A Highly Configurable HW/SW Stack for DNN Inference |
| 2305.08415 | Marsellus: Heterogeneous RISC-V AI-IoT SoC (JSSC'23) |
| 2406.17796 | Hypervisor Extension for a RISC-V Processor |
| 2409.00661 | 基于 Matrix 指令集扩展的 RISC-V 处理器"香山"(Nanhu) LLM 加速（本团队） |
| 2502.21027 | RISC-V Multicore + GPU SoC Platform |
| 2504.01972 | Efficient Trace for RISC-V in CVA6 |
| 2504.05284 | FERIVer: FPGA-assisted RTL Verification |
| 2506.10921 | Towards Zero-Stall Matrix Multiplication (RISC-V) |
| 2507.01457 | Tensor Program Optimization for RVV |
| 2507.03522 | A Flexible ISA for Efficient GEMMs (MTE) |
| 2508.02236 | GSIM: Accelerating RTL Simulation |
| 2509.18355 | Chiplet-Based RISC-V SoC with Modular AI Acceleration |
| 2512.21473 | Demystifying ARM SME to Optimize GEMM |
| 2604.13523 | TensorLift: ISA Semantics from Accelerator RTL |
| 2604.27808 | AME-PIM: Can Memory be Your Next Tensor Accelerator? |
| 2608.04247 | Centralized Performance Monitoring Architecture for Hetero SoCs |
