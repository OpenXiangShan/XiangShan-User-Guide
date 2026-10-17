# 性能监测与 Top-down 分析 {#sec:xsai-pmu}

本章描述香炉峰在基线 HPM 之上新增的性能监测能力。基线 HPM 的通用机制见《香山开源处理器用户手册·性能监测单元》；本章只覆盖香炉峰的增量部分。

## HPM 能力概览

| 项 | 香炉峰 |
| --- | --- |
| 性能事件计数器 | 29 个（`mhpmcounter3` – `mhpmcounter31`） |
| 性能事件选择器 | 29 个（`mhpmevent3` – `mhpmevent31`） |
| 每个选择器可组合事件数 | 最多 4 个（事件索引 + 组合方式 + 采样特权级） |
| 可定义事件总数 | 最多 2^10 种 |
| 溢出中断 | `LCOFIP`，中断向量号 **13**，使能与处理同普通私有中断 |
| 扩展 | 基础 HPM，额外支持 `sstc` 与 `sscofpmf` |

溢出中断向量号 13 的依据：向量 12 由 `SGEI` 占用，LCOFIP 取 13。溢出中断只由 HPM 计数器溢出产生，与矩阵单元没有专线；矩阵性能事件并入后端事件池后，矩阵活动可以间接触发它。

## 事件池划分

`mhpmevent` 按事件池划分，一个池内共享同一张事件索引表：

| 事件池 | 选择器范围 |
| --- | --- |
| 前端 | `mhpmevent3` – `mhpmevent10` |
| 后端 | `mhpmevent11` – `mhpmevent18` |
| 访存 | `mhpmevent19` – `mhpmevent26` |
| 缓存 | `mhpmevent27` – `mhpmevent31` |

香炉峰前端与缓存事件池语义与基线一致，矩阵相关事件追加在**后端**和**访存**两个池里。两个池的事件编号各自独立。

## 矩阵相关事件

### 后端事件池（`mhpmevent11` – `mhpmevent18`）

19 个追加事件，覆盖矩阵重命名、调度队列状态与 CUTE 任务生命周期：

| 索引 | 事件 | 含义 |
| --- | --- | --- |
| 95 | `rename_stall_cycle_mx` | rename 因矩阵 free list 无法分配而停顿的周期 |
| 96 | `me_freelist_1_4_valid` | 矩阵 free list 剩余量处于 1/4 档位 |
| 97 | `me_freelist_2_4_valid` | 矩阵 free list 剩余量处于 2/4 档位 |
| 98 | `me_freelist_3_4_valid` | 矩阵 free list 剩余量处于 3/4 档位 |
| 99 | `me_freelist_4_4_valid` | 矩阵 free list 剩余量处于 4/4 档位 |
| 100 | `IssueQueueMsetmtilexriwmfMrelease_full` | 矩阵整数调度队列满 |
| 101 | `issueQueue_enq_fire_cnt` | 矩阵浮点 / 算术调度队列入队数 |
| 102 | `IssueQueueMsetmtilexrmfwmf_full` | 矩阵浮点 / 搬运调度队列满 |
| 103 | `IssueQueueMmaMarith_full` | 矩阵计算 / 算术调度队列满 |
| 104 | `IssueQueueMls_full` | 矩阵访存调度队列满 |
| 105 | `amu_active_cycle` | CUTE 处于 active 状态的周期数 |
| 106 | `amu_retire` | CUTE 任务 retire 次数 |
| 107 | `amu_comp_done` | CUTE 计算完成次数 |
| 108 | `amu_release_done` | CUTE release 完成次数 |
| 109 | `amu_mte_active` | MTE busy 周期数 |
| 110 | `amu_mma_nonfp` | 非浮点 MMA 完成次数 |
| 111 | `amu_mma_fp16` | FP16 MMA 完成次数 |
| 112 | `amu_mma_bf16` | BF16 MMA 完成次数 |
| 113 | `amu_mma_tf32` | TF32 MMA 完成次数 |

### 访存事件池（`mhpmevent19` – `mhpmevent26`）

12 个追加事件，覆盖矩阵搬运通路与 LocalMMU 流量：

| 索引 | 事件 | 含义 |
| --- | --- | --- |
| 145 | `amu_load_a_done` | A 矩阵 load 完成次数 |
| 146 | `amu_load_b_done` | B 矩阵 load 完成次数 |
| 147 | `amu_load_c_done` | C 矩阵 load 完成次数 |
| 148 | `amu_store_done` | C 矩阵 store 完成次数 |
| 149 | `amu_aml_active` | AML busy 周期数 |
| 150 | `amu_bml_active` | BML busy 周期数 |
| 151 | `amu_cml_load_active` | CML load busy 周期数 |
| 152 | `amu_cml_store_active` | CML store busy 周期数 |
| 153 | `amu_mem_rd_req` | LocalMMU 向外发出的读请求次数 |
| 154 | `amu_mem_wr_req` | LocalMMU 向外发出的写请求次数 |
| 155 | `amu_mem_rd_32B` | LocalMMU 读流量，以 32 B 为单位 |
| 156 | `amu_mem_wr_32B` | LocalMMU 写流量，以 32 B 为单位 |

表中索引是各事件池**内部**编号，填入 `mhpmevent` 的 `EVENT0`–`EVENT3` 域。

### 用法示例

同时统计 MTE 忙碌周期数与 LocalMMU 读请求次数：

```asm
# 后端事件池：mhpmevent11 的 EVENT0 = 109（amu_mte_active）
# 访存事件池：mhpmevent19 的 EVENT0 = 153（amu_mem_rd_req）
csrw mhpmevent11, <109 按域编码后的值>
csrw mhpmevent19, <153 按域编码后的值>
csrw mcountinhibit, 0        # 允许全部计数器计数
...                          # 运行负载
csrr t0, mhpmcounter11       # MTE busy 周期数
csrr t1, mhpmcounter19       # LocalMMU 读请求次数
```

## Top-down 性能分析

香炉峰实现了三层 Top-down 性能事件树，从整体分类逐层下钻定位瓶颈。`IssueBW` 为发射宽度，当前为 **6 发射**。

| Level 1 | Level 2 | Level 3 | 含义 |
| --- | --- | --- | --- |
| Retiring | — | — | 指令提交影响 |
| FrontEnd Bound | — | — | 前端影响 |
| — | Fetch Latency Bound | — | 取指延迟影响 |
| — | Fetch Bandwidth Bound | — | 取指带宽影响 |
| Bad Speculation | — | — | 错误预测影响 |
| — | Branch Misspredict | — | 分支预测错误影响 |
| — | Machine Clears | — | 机器清除事件影响 |
| BackEnd Bound | — | — | 后端影响 |
| — | Core Bound | — | 内核影响 |
| — | Memory Bound | — | 访存影响 |
| — | — | L1 / L2 / L3 Bound | 各层缓存影响 |
| — | — | Mem Bound | 外部内存影响 |
| — | — | Store Bound | 存储指令影响 |

示例：统计前端取指延迟影响，把 `mhpmevent3` 的 `EVENT0` 域设为 22，运行后读 `mhpmcounter3`。

## CUTE Top-down 逐层分解

矩阵单元的分析重点不是吞吐，而是**停顿落在哪里**。分层定义在 `tools/TMA-toolkit/presets/cute/default.yaml`，共四层：

### L0：总停顿

| 计数器 | 含义 |
| --- | --- |
| `CUTE_L0_TC_HeadValidSlot` | 头部任务有效的槽位数 |
| `CUTE_L0_TC_IssueFire` | 成功发射的槽位数 |
| `CUTE_L0_TC_Stall` | 派生：`HeadValidSlot - IssueFire` |

### L1：主因分类（互斥）

`CUTE_L1_TC_Stall_Memory`、`CUTE_L1_TC_Stall_Compute`、`CUTE_L1_TC_Stall_Dependency` 三个互斥桶回答停顿主因是访存、计算还是依赖。配套 gate 观测计数：`CUTE_L1_TC_Need_{AML,BML,CML,ADC,BDC,CDC}` 与 `CUTE_L1_TC_Block_{AML,BML,CML,ADC,BDC,CDC}`。

### L2：依赖子类

| 分类 | 计数器 |
| --- | --- |
| 数据依赖 | `CUTE_L2_SB_Block_Dep_SrcNotReady`、`_DestBusy`、`_DestHasConsumers`、`_CMLStoreConsumer` |
| 资源占用 | `CUTE_L2_SB_Block_Res_AMLBusy`、`_BMLBusy`、`_CMLLoadBusy`、`_CMLStoreBusy`、`_ComputeBusy` |

### L3：来源细分

`SrcNotReady` 与 `DestBusy` 各按四路生产者拆分：`CUTE_L3_SB_Dep_{SrcNotReady,DestBusy}_By_{AML,BML,CML,Compute}`。

### 读表注意事项

计数桶分三类，混起来会误读结果：

- **互斥桶**：同一停顿周期只落一个桶，L1 各桶之和等于 L0 的停顿总量；
- **非互斥桶**：同一周期可命中多个条件，总和可超过父项（如 Compute 域内 ADC/BDC/CDC 可同时命中）；
- **残差桶**：父项减去已显式子项，承接未下钻部分，如 `CUTE_L2_Memory_Remain`。

`consistency.json` 自动校验数学与语义关系。校验失败说明分类定义存在重叠，先修 preset 再看结论。

## 使用 TMA-toolkit

分析需求通过新建或调整 YAML preset 扩展，不需要手动修改 RTL 代码。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
make -C tools/TMA-toolkit sync                            # 准备依赖

make -C tools/TMA-toolkit apply-dry PRESET=cute/default   # 预览插桩锚点，不改文件
make -C tools/TMA-toolkit apply     PRESET=cute/default   # 执行插桩

make run-emu PAYLOAD=<payload>                            # 跑仿真

make -C tools/TMA-toolkit report        PRESET=cute/default LOG=log/emu-error.log
make -C tools/TMA-toolkit report-strict PRESET=cute/default LOG=log/emu-error.log
```

`report` 恒返回 0，适合日常；`report-strict` 在一致性检查失败时返回非 0，适合放进自动化流程。产物包括 `values.csv`、`combined.png`、`report.md`、`consistency.json`。

常用 preset：`cute/default`（L1 互斥）与 `cute/legacy_v1`（历史非互斥分类，用于版本对比）。

读报告固定三步：先看 L1 占比确定主因，再看该主因下一层定位子类，最后看 `consistency.json` 确认各层计数自洽。

## 推荐分析流程

1. 算子级性能表：周期数、IPC、有效带宽、算术强度、峰值占比；
2. HPM 或 CUTE Top-down 确定瓶颈类型（访存 / 计算 / 调度 / 依赖）；
3. 波形或结构化追踪定位到具体模块与时刻。
