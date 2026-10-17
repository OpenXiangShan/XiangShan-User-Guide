# 矩阵数据寄存器 {#sec:xsai-registers}

本章描述香炉峰新增的矩阵相关寄存器。标量与向量寄存器与昆明湖 V2R2 一致，不在此重复。读本章前需要读过[指令集扩展](instruction-set.md#sec:xsai-instruction-set)。

## 矩阵寄存器

| 类型 | 名称 | 用途 |
| --- | --- | --- |
| A / B tile | `tr0` – `tr3` | 矩阵乘加的操作数 |
| C / acc tile | `acc0` – `acc3` | 累加与结果 |

整数路径的累加器为 int32（i8 × i8 → i32），浮点路径（bf16 等）为 fp32；低精度输入不改变累加器宽度。

## 原生 tile 尺寸

矩阵单元的原生尺寸是 **M128 × N128 × K64**，由硬件配置决定，软件不能假设。

尺寸不要写死，启动时通过 CSR 读一次实际值，读法见[矩阵 CSR](csr.md#sec:xsai-csr)。用错尺寸不会报错，只会算错：上板整层结果错、同一个负载在 QEMU 上却全对，通常就是这个原因。

| 探针 | 读出值 | 含义 |
| --- | --- | --- |
| `tlenb` | 8192 B | 一个 tile 寄存器的长度 |
| `trlenb` | 64 B | tile 行宽 |
| `alenb` | 65536 B | 一个累加器的长度 |

`ROWNUM = tlenb / trlenb = 128`，是 M 和 N 的上限。设计文档用 M-K-N 顺序写作 `128x64x128`，与这里的 M-N-K 顺序是同一套尺寸。

寄存器容量：单个 AB 寄存器（`tr0` – `tr3`）8 KiB，单个累加器（`acc0` – `acc3`）64 KiB。

## 配置寄存器

`mcfg0` – `mcfg7` 由 `msetcfg` 写入、`mgetcfg` 读回，位域如下：

| 位 | 字段 | 含义 |
| --- | --- | --- |
| `[3:0]` | `type_code` | 在所选 type table 内选择数据类型（编码见[指令集扩展](instruction-set.md#sec:xsai-instruction-set)） |
| `[7:4]` | `table_sel` | 选择 type encoding table |
| `[XLEN-1:8]` | uninterpreted payload | `msetcfg` 存储、`mgetcfg` 原样读回；矩阵执行语义不解释这些位 |

三个 selector 位同时选择矩阵寄存器与其关联的 `mcfg`：`000`–`011` 对应 `tr0`–`tr3` / `mcfg0`–`mcfg3`，`100`–`111` 对应 `acc0`–`acc3` / `mcfg4`–`mcfg7`。tile 形状由 `mtilem` / `mtilen` / `mtilek` 决定，转置与整块（whole）模式编码在访存指令里。

### 形状与类型参数

- `msettilem` / `msettilen` / `msettilek`：设置 tile 的 M、N、K 维度。
- bf16 路径下 `msettilek` 按**元素**计（`msettilek=32`），而 `mla` / `mlb` 的 stride 操作数按**字节**计（对应 64 字节）。
- K 需按 tile 的 K 上限对齐：i8 为 64 个元素、bf16 为 32 个元素；调用侧要求 K 为 32 的整数倍，不足部分需 padding 或走尾数处理。
- `type_code = 1111` 保留。软件不要依赖未使能的类型；取用前先用 `mgetcfg` 读回确认。

### 非法与遗留配置

以下写法不被 ZAMES 路径接受，出现时应视为错误：

| 写法 | 问题 | 正确写法 |
| --- | --- | --- |
| `msettype mtype0, a0` | ZAMES 不使用旧 `mtype` 配置语法 | `msetcfg mcfg0, a0` |
| `mla.whole tr0, (a0)` | 当前工具链要求显式写出第三操作数，省略会被汇编器拒绝 | `mla.whole tr0, (a0), zero` |
| `macquire a0, sync0` | 这是 legacy Xuantie-0.6 操作数顺序 | `macquire sync0, a0` |
| `tok0` | 旧 token 拼写不再作为用户可见语法 | `sync0` |
| `sync16` – `sync31` | 保留编码，汇编器与反汇编器都会拒绝 | `sync0` – `sync15` |

## 同步寄存器

`sync0` – `sync15` 用于异步矩阵操作的同步与依赖跟踪。用户可见范围是 `sync0` – `sync15`，`sync16` – `sync31` 是保留编码。每个工作项开始前调用 `msyncregreset syncN`；生产侧用 `mrelease syncN` 推进，消费侧用 `macquire syncN, rs1` 等待 `syncN >= x[rs1]`。

`minit` 把矩阵寄存器中的数据标记为可丢弃，用于降低上下文切换开销。

同步语义的完整说明见[指令集扩展](instruction-set.md#sec:xsai-instruction-set)。当前不建议在 ZAMES 路径直接依赖 `mcsr`、`mstatus` / `sstatus.MS` 等 CSR 机制。

## 布局与对齐约束

- 操作数缓冲必须物理连续：AMU 行寻址按 `PA_base + row × stride` 计算且不逐行重查 TLB，非连续缓冲在行数较大时会静默读错。池基址是运行期解析的（环境变量 → 设备树 `direct_map` → 编译期默认值），不是固定值；默认布局为 6 GiB @ `0x1_0000_0000`，mega 布局为 4 GiB @ `0x3_8000_0000`，详见[内存子系统与 HBL2](../hardware/memory.md#sec:xsai-memory)。
- `0x2_8000_0000` 是默认布局下 RAM 的顶端（即池的结束地址），不是基址。
- 转置访存有行主序 / 列主序约定，由访存指令的 stride 控制。
- 差分验证 dump 比对时要剔除 16 B 对齐引入的 padding（未初始化内存），只比对有效元素，否则会产生假失败。

### 上下文切换

矩阵架构状态包含 `tr0` – `tr3`、`acc0` – `acc3` 及其关联的 `mcfg0` – `mcfg7`。保存与恢复使用 whole-register 传输，它按完整寄存器搬运，不按当前 element type 或 active tile shape 解释数据：

```plain
msa.whole tr0, (save_tr0), zero
msc.whole acc0, (save_acc0), zero

mla.whole tr0, (save_tr0), zero
mlc.whole acc0, (save_acc0), zero
```

`minit` 把矩阵状态标记为可丢弃，因此切换出去后若已调用 `minit`，可以不做完整保存。
