# 附录 B：术语表 {#sec:appendix-glossary}

## 硬件单元

| 缩写 | 全称 | 说明 |
| --- | --- | --- |
| AME | Attached Matrix Extension | 附着的矩阵扩展 |
| AMU | — | 矩阵访存与命令管理单元 |
| CUTE | — | 矩阵计算单元 |
| MTE | Matrix Tensor Engine | 矩阵乘加通路，PE 阵列的外积数据流 |
| FPE | Floating Point Engine | 浮点运算引擎，MTE 内的基本运算单元 |
| ADC / BDC | A / B Data Controller | A / B 路操作数读出 |
| AML / BML / CML | A / B / C Memory Loader | A / B / C 矩阵搬运通路 |
| LocalMMU | — | 矩阵单元对外的数据面接口，统一访问 LLC 与内存层次 |
| TaskController | — | 矩阵任务调度与发射 |
| HBL2 | High Bandwidth L2 | 高带宽二级缓存，基于 `CoupledL2` 改造 |
| PMU / HPM | Hardware Performance Monitor | 硬件性能监测单元 |
| LCOFIP | Local Counter Overflow Interrupt Pending | 性能计数溢出中断，向量号 **13**（12 是 `SGEI`） |

## 寄存器与编程模型

| 术语 | 说明 |
| --- | --- |
| `tr0` – `tr3` | A / B tile 寄存器 |
| `acc0` – `acc3` | C 累加寄存器 |
| `mcfg0` – `mcfg7` | 与矩阵寄存器一一关联的配置寄存器；3 位选择符同时选择两者 |
| `sync0` – `sync15` | ZMASYNC 同步寄存器（`sync16` – `sync31` 为保留编码） |
| `mtilem` / `mtilen` / `mtilek` | 当前 tile 的 M / N / K 三个维度，`mtilek` 是共用的约简维 |
| `TLEN` / `TRLEN` | tile 寄存器长度与行宽；`ROWNUM = TLEN / TRLEN` |
| `ALEN` / `ARLEN` | 累加器长度与行宽 |
| raw `mcfg` | `mcfg` 的原始值，由软件生成后交给 `msetcfg`；`mgetcfg` 原样读回 |
| `type_code` / `table_sel` | `mcfg` 低 8 位中的两个字段：类型选择与编码表选择 |
| whole-register transfer | 整寄存器搬运（`mla.whole` 等），不解释元素类型，stride 位置固定为 `zero` |
| `minit` | 把矩阵寄存器内容标记为可丢弃 |
| `msyncregreset` | 重置同步寄存器；每张 tile 使用前调用 |
| `mrelease` / `macquire` | 推进与等待同步状态；`macquire syncN, rs1` 等待 `syncN >= x[rs1]` |
| `mfence` | 使非矩阵访存对后续矩阵访存可见 |
| MSC 基址寄存器 | `msc` 存 C 指令的地址操作数寄存器，需钉住（如 `s11`）并保活到 `macquire` |
| `MS` 状态域 | `mstatus` / `sstatus` / `vsstatus` 中表达矩阵状态的状态域，纳入 `SD` 脏状态聚合 |

## 性能

| 术语 | 说明 |
| --- | --- |
| MFU | Model FLOPs Utilisation；本手册区分矩阵单元利用率与算子利用率，两者不可混用 |
| Roofline | 以算术强度与带宽为轴的性能上界模型 |
| prefill / decode | 大模型推理的两个阶段，瓶颈结构不同，必须分开统计 |
| Top-down 分析 | 把停顿周期逐层分解到主因、子类与具体来源的方法 |
| `consistency.json` | TMA-toolkit 的产物，用于校验各层计数是否自洽 |
| epilogue | GEMM 之后的 scale、zero-point、requant、clamp 与激活处理，需与框架参考实现一致 |
| per-oc | per-output-channel 的 scale 粒度，最常见的一种 |

## 验证与调试

| 术语 | 说明 |
| --- | --- |
| difftest | 差分验证，与参考模型逐步比对 |
| checkpoint / GCPT | 程序状态快照，以及被链接进镜像用于恢复体系结构状态的恢复程序（`gcpt.bin`） |
| SimPoint | 通过聚类选取代表性切片的方法 |
| `GOOD_TRAP` | 标记负载执行终点，通常也是 RTL 仿真终点 |
| UB | Undefined Behaviour，未定义行为 |

## 软件栈

| 术语 | 说明 |
| --- | --- |
| `elempack` | NCNN 的打包层级；大于 1 时需先解包，或让打包逻辑感知 |
| PGO | Profile-Guided Optimisation；仿真器构建选项，收益见[功能模拟器](../software/simulators.md#sec:sw-simulators) |
| GSIM | 一类 RTL 仿真后端，与 Verilator 并列 |
| 尾包 | 像素数少于 `DST_XUNIT` 的最后一个包，布局为紧凑排布 |
