# 附录 A：相对昆明湖 V2R2 的差异清单 {#sec:appendix-diff}

这一页是整个增量的总账。本手册各章讲的都是这里的一项或几项。

| 模块 | 增量 | 影响面 | 详见 |
| --- | --- | --- | --- |
| 矩阵计算单元 | 矩阵计算与访存通路、转置引擎 | 指令集、访存、性能 | [微架构增量](../hardware/microarchitecture.md#sec:xsai-microarchitecture) |
| 矩阵控制通路 | 命令下发、完成通知与提交语义 | 指令提交、异常 | 同上 |
| 寄存器 | 矩阵寄存器、配置寄存器、同步寄存器 | 编程模型 | [数据寄存器](../isa/registers.md#sec:xsai-registers) |
| CSR 与设备树 | 矩阵状态域、精度能力的描述方式 | 固件、操作系统 | [矩阵 CSR](../isa/csr.md#sec:xsai-csr)、[系统软件与运行时](../software/system.md#sec:sw-system) |
| 高带宽 L2 | HBL2 与矩阵专用访存通路 | 内存子系统、性能 | [内存子系统与 HBL2](../hardware/memory.md#sec:xsai-memory) |
| 指令编码 | `async` 位区分同步与异步矩阵指令 | 编译、同步 | [微架构增量](../hardware/microarchitecture.md#sec:xsai-microarchitecture) |
| 性能监测 | 矩阵相关 HPM 事件与 Top-down 分层 | 调优 | [性能监测](../hardware/pmu.md#sec:xsai-pmu) |
| 验证与调试 | 差分验证的矩阵支持、checkpoint 采样 | 验证流程 | [差分验证](../verification/difftest.md#sec:debug-difftest)、[Checkpoint 与切片](../verification/checkpoint.md#sec:debug-checkpoint) |
| 精度 | 只使能 INT8、FP8、BF16 三种组合 | 量化、精度验证 | [矩阵数据寄存器](../isa/registers.md#sec:xsai-registers) |

## 验证覆盖

| 层次 | 覆盖范围 |
| --- | --- |
| 单元级 | CUTE 关键点：TileLink 事务的地址对齐与大小、寄存器文件读写时序、矩阵乘加结果、int8 × int8 → int32 与 uint8 × uint8 → uint32 等类型组合、边界条件 |
| 集成级 | CUTE + L2 随机激励框架 |
| 差分验证 | 可完整比对矩阵 CSR 与 `mcfg0` – `mcfg7`，见[差分验证](../verification/difftest.md#sec:debug-difftest) |
