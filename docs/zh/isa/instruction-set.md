# 指令集扩展 {#sec:xsai-instruction-set}

本章描述香炉峰相对昆明湖 V2R2 新增的指令集扩展 ZAMES 与 ZMASYNC。基线指令集见《香山开源处理器用户手册·指令集》；本章只覆盖扩展增量，不重复基线内容。读者需要具备 RISC-V 基础知识。

## 扩展与版本

| 扩展 | 说明 | 规范 |
| --- | --- | --- |
| ZAMES | 矩阵计算扩展（配置、矩阵乘加、矩阵访存） | Zames 草案 v0.6（simplified v0.1）；当前实现对应 proposal-12 |
| ZMASYNC | ZAMES 的同步伴随扩展 | 同上 |
| 低精度转换 | `vfncvtmxfp.f.f.w`、`vfncvtxx8.f.a.w` 等 | 见多精度相关提案 |

规范拼写是 `ZMASYNC`；`zamesync` 应理解为同一扩展。

在 LLVM 工具中通过 `-mattr` 打开：

```bash
llvm-mc -triple=riscv64 -mattr=+zames input.s
llvm-mc -triple=riscv64 -mattr=+zmasync input.s
llc -mtriple=riscv64 -mattr=+zames input.ll
```

| Feature | 含义 |
| --- | --- |
| `+zames` | 简化矩阵配置指令、矩阵 load/store、`mzero` 和 `mmacc` |
| `+zmasync` | ZAMES 的同步伴随扩展，提供 sync register 相关指令；feature 定义上依赖 `+zames` |

`+zmasync` 在编程模型上是矩阵异步同步扩展，不是独立的矩阵计算 ISA。

## 用户可见寄存器

| 类型 | 名称 | 用途 |
| --- | --- | --- |
| A / B tile 寄存器 | `tr0` – `tr3` | 保存 A / B 输入矩阵 tile |
| C 累加寄存器 | `acc0` – `acc3` | 保存 C 输出或累加矩阵 tile |
| 配置选择器 | `mcfg0` – `mcfg7` | `msetcfg` / `mgetcfg` 使用 |
| 同步寄存器 | `sync0` – `sync15` | ZMASYNC 同步寄存器 |
| 标量寄存器 | RISC-V GPR | 地址、stride、tile shape、比较值、raw `mcfg` 值 |

以下约束必须遵守：

- `tok0` – `tok15` 旧拼写不再作为用户可见汇编语法使用；
- `sync16` – `sync31` 是保留编码，汇编器与反汇编器都会拒绝；
- 当前不要把 CSR 当作常规编程接口：`mcsr`、`mstatus` / `sstatus.MS` 相关机制暂时不建议在 ZAMES 路径中直接依赖；
- 矩阵内存可见性必须通过 ZMASYNC 同步指令（`mrelease` / `macquire`）处理，不能依赖其他顺序假设。

### 矩阵寄存器与配置寄存器的对应

ZAMES 使用 3-bit matrix register selector，selector 同时选择矩阵寄存器与其关联的 `mcfg`：

| Selector | 矩阵寄存器 | 配置寄存器 |
| --- | --- | --- |
| `000` | `tr0` | `mcfg0` |
| `001` | `tr1` | `mcfg1` |
| `010` | `tr2` | `mcfg2` |
| `011` | `tr3` | `mcfg3` |
| `100` | `acc0` | `mcfg4` |
| `101` | `acc1` | `mcfg5` |
| `110` | `acc2` | `mcfg6` |
| `111` | `acc3` | `mcfg7` |

尺寸模型：`tr0` – `tr3` 为 `TLEN` bits，行宽 `TRLEN`，行数 `ROWNUM = TLEN / TRLEN`；`acc0` – `acc3` 为 `ALEN` bits，行宽 `ARLEN`，行数同为 `ROWNUM`。

## Tile shape 约定

ZAMES 用 `mtilem`、`mtilek`、`mtilen` 三个独立值描述一次矩阵操作的 active tile shape：

| 矩阵 | 典型 shape | 相关指令 |
| --- | --- | --- |
| A | `mtilem × mtilek` | `mla` / `msa` |
| B | `mtilen × mtilek` | `mlb` / `msb` |
| C | `mtilem × mtilen` | `mlc` / `msc` / `mmacc` |

`mtilek` 是共用的约简维（K 维）。设计文档中常见的 `128×64×128` 按 M-K-N 顺序排列；换算成 M-N-K 写法即为 128×128×64，两者是同一套尺寸。

## 配置与控制指令

| 指令 | 示例 | 说明 |
| --- | --- | --- |
| `minit` | `minit` | 初始化矩阵状态，使矩阵寄存器内容可被视为 discardable |
| `msettilemi` | `msettilemi 16` | 用立即数设置 `mtilem` |
| `msettilem` | `msettilem a0` | 用 GPR 设置 `mtilem` |
| `msettileni` | `msettileni 16` | 用立即数设置 `mtilen` |
| `msettilen` | `msettilen a1` | 用 GPR 设置 `mtilen` |
| `msettileki` | `msettileki 64` | 用立即数设置 `mtilek` |
| `msettilek` | `msettilek a2` | 用 GPR 设置 `mtilek` |
| `msetcfg` | `msetcfg mcfg0, a0` | 设置一个矩阵寄存器关联的 raw `mcfg` |
| `mgetcfg` | `mgetcfg a0, mcfg0` | 读取一个 raw `mcfg` |
| `mzero` | `mzero acc0` | 清零一个 tile 或 accumulator register，不修改其 `mcfg` |

`mcfg` 的编码：低 8 位用于类型选择，`[3:0]` 为 `type_code`（在所选 type table 内选择数据类型），`[7:4]` 为 `table_sel`（选择 type encoding table），`[XLEN-1:8]` 为 uninterpreted payload，由 `msetcfg` 存储、`mgetcfg` 原样读回，当前矩阵执行语义不解释这些位。

## 数据类型

`table_sel = 0` 时 `type_code` 编码：

| `type_code` | 类型 | `type_code` | 类型 |
| --- | --- | --- | --- |
| `0000` | `int4` | `1000` | `fp8e4m3` |
| `0001` | `uint4` | `1001` | `fp16` |
| `0010` | `int8` | `1010` | `bf16` |
| `0011` | `uint8` | `1011` | `tf32` |
| `0100` | `int32` | `1100` | `fp32` |
| `0101` | `nvfp4` | `1101` | `fp2pack4` |
| `0110` | `mxfp4` | `1110` | `fp2pack5` |
| `0111` | `fp8e5m2` | `1111` | 保留 |

共 15 个命名类型。香炉峰当前两套 MatrixConfig 只使能 **int8 → int32、fp8 → fp32、bf16 → fp32** 三项。`MatrixTE` 不接收 `ScaleA` / `ScaleB` 输入，也不支持 MXFP / NVFP 计算，因此 `mxfp4` 与 `nvfp4` 虽在类型表内但不可用。软件不要依赖未使能类型，取用前先用 `mgetcfg` 读回确认。

## 矩阵乘加

| 指令族 | 输入精度 | 输出精度 |
| --- | --- | --- |
| `mmacc` 整数 | i8 × i8 | i32 |
| `mmacc` 浮点 | bf16 × bf16 | fp32 |
| 低精度 | fp8 e4m3 / e5m2 | fp32 |

int4 / uint4 需先 pack / unpack，当前未使能；fp4 系列未使能。

`mmacc acc0, tr1, tr0` 的逻辑含义是对 `acc0` 的 active C 区域累加 A 与 B 的矩阵乘结果。操作数约束：

- `md` 必须是 `acc0` – `acc3`；
- `ms2` 和 `ms1` 必须是 `tr0` – `tr3`；
- 常见写法中 `ms2` 放 B、`ms1` 放 A：`mmacc acc0, tr1, tr0`。

`msettilek` 按**元素**计（bf16 为 32、i8 为 64），tile 的行宽 `TRLEN` 为 **64 字节**；`mla` / `mlb` 的 `stride` 操作数单位为字节。

## 矩阵访存

内存操作数格式为 `op matrix_reg, (base_gpr), stride_gpr`：`base_gpr` 是 tile 左上角元素的基地址，`stride_gpr` 是矩阵行 stride，**单位为 byte**。A / B 的目标或源必须是 `tr0` – `tr3`，C 的必须是 `acc0` – `acc3`。

| 分类 | 指令 |
| --- | --- |
| load | `mla`、`mlb`、`mlc` |
| store | `msa`、`msb`、`msc` |
| transposed load | `mlat`、`mlbt`、`mlct` |
| transposed store | `msat`、`msbt`、`msct` |
| whole-register load | `mla.whole`、`mlb.whole`、`mlc.whole` |
| whole-register store | `msa.whole`、`msb.whole`、`msc.whole` |

```plain
mla tr0, (a0), a1      # load A tile
mlb tr1, (a2), a3      # load B tile
mlc acc0, (a4), a5     # load C tile

msat tr0, (a0), a1     # transposed store A tile
```

### Whole-register 传输

Whole-register transfer 保存或恢复一个**完整** architectural matrix register，不按当前 element type 或 active tile shape 解释数据，stride 位置固定为 `x0`：

```plain
msa.whole tr0, (save_tr0), zero       # 保存完整矩阵寄存器状态
msc.whole acc0, (save_acc0), zero

mla.whole tr0, (save_tr0), zero       # 恢复完整矩阵寄存器状态
mlc.whole acc0, (save_acc0), zero
```

**第三个操作数必须显式写出 `zero`**：只写两个操作数（如 `msa.whole tr0, (a0)`）会被汇编器拒绝；写出非 `zero` 的第三个寄存器会被接受，但那是带 stride 的普通传输，语义不同。

### 地址翻译与对齐约束

当前实现**只对 base address** 完成地址翻译和访问保护检查。软件必须保证整个 matrix 访问范围位于物理连续、权限一致、PMP 允许的区域内；若 tile 访问范围跨入未映射、不连续或 PMP 不允许的物理区域，该情形不受支持。

由此推出三条实践约束：

- 操作数缓冲必须物理连续（见[内存子系统与 HBL2](../hardware/memory.md#sec:xsai-memory)）；
- 行地址由 `PA_base + row × stride` 给出，不做逐行 TLB 重查；
- 尾包（`real_count < DST_XUNIT`）为紧凑布局，不能沿用固定步长。

## 同步与内存序

ZMASYNC 使用 `sync0` – `sync15`：

| 指令 | 示例 | 说明 |
| --- | --- | --- |
| `msyncregreset` | `msyncregreset sync0` | 重置 sync register |
| `mrelease` | `mrelease sync0` | 通常在矩阵 store 可见后递增同步状态 |
| `macquire` | `macquire sync0, a0` | 等待 `sync0 >= x[a0]` |
| `mfence` | `mfence` | 使非矩阵内存数据对之后的矩阵引擎内存操作可见 |

注意 `macquire` 的操作数顺序是 `macquire sync_reg, threshold_gpr`，与旧 Xuantie-0.6 路径相反，两条路径不要混用。

最小示例：

```plain
mfence                 # 先把非矩阵侧准备的输入推给矩阵引擎
msyncregreset sync0    # 复位该 sync register 的计数
# ... 此处发出矩阵 load / mmacc / store ...
mrelease sync0         # 矩阵 store 对后续标量 / 向量可见后递增 sync0
li a0, 1
macquire sync0, a0     # 阻塞至 sync0 >= 1；此后结果可被 CPU 消费
```

阈值寄存器必须先初始化：`a0` 为 0 时 `macquire` 立即通过，等于没有等待。

### 顺序语义

- 矩阵指令异步执行：提交顺序与完成顺序可以不同；
- 矩阵结果对向量 / 标量的可见性用 `macquire`，非矩阵访存对矩阵引擎的可见性用 `mfence`，两者方向不同；
- `mrelease` / `macquire` 必须覆盖**所有**退出分支，否则会出现非稳定复现的偶发错；
- 每个工作项开始前调用 `msyncregreset`；
- `macquire` 之前的 MSC 基址寄存器需要钉住（例如 `s11`）并保活，编译器回收该寄存器会导致偶发错；
- 读取未写入的矩阵寄存器区域属未定义行为。

## 同步 GEMM 示例

以下是最小的同步 GEMM 风格流程（寄存器名与配置值只是示例，实际需要按数据类型、布局和 tile 大小生成 raw `mcfg`、base address 和 stride）：

```plain
# llvm-mc -triple=riscv64 -mattr=+zames,+zmasync

minit

# a0 = M, a1 = K, a2 = N
msettilem a0
msettilek a1
msettilen a2

# t0/t1/t2 = raw mcfg values for A/B/C
msetcfg mcfg0, t0      # tr0 configuration for A
msetcfg mcfg1, t1      # tr1 configuration for B
msetcfg mcfg4, t2      # acc0 configuration for C

# A / B 已由 CPU 侧准备好：先让这些数据对矩阵引擎可见
mfence

# a3 = A base, a4 = B base, a5 = C base
# a6/a7/t3 = row strides in bytes
mla tr0, (a3), a6      # A[M,K]
mlb tr1, (a4), a7      # B[N,K]
mzero acc0             # initialize C accumulator to zero

msyncregreset sync0    # 每个工作项开始前复位 sync 计数

mmacc acc0, tr1, tr0   # C += A x B

msc acc0, (a5), t3     # store C[M,N]

mrelease sync0         # 递增计数，等待 store 可见
li t4, 1
macquire sync0, t4     # 阻塞至 sync0 >= 1；此后 C 可被 CPU 消费
```

**不要在 `msc` 之后直接消费 C**：`mmacc` 与 `msc` 都是非阻塞提交，只有 `macquire` 通过后，C 才可被 CPU 侧的后续代码读取。

需要累加已有 C 时，把 `mzero acc0` 换成 `mlc acc0, (a5), t3`。

标准调用顺序：`minit` → 设置 tile shape → `msetcfg` 配置 A / B / C → load A / B / C 或 `mzero` → `mmacc` → `msc` → `mrelease` / `macquire`。

## 低精度转换指令

代表指令为 `vfncvtmxfp.f.f.w`（转向 MXFP 格式，支持动态缩放因子）与 `vfncvtxx8.f.a.w`（转向 INT8 / FP8），定义在 custom 操作码空间，支持掩码编码。

**本版不包含这两条转换指令**：本版 SDK 固定的 RTL、NEMU、QEMU、LLVM 与 ISA 规范中均未包含其定义，本手册不给出编码，也不承诺其可用性。使用时以你所用工具链实际支持的指令与编码为准。

注意区分两件不同的事：`mcfg` 类型表内的 `mxfp4` / `nvfp4` 是矩阵乘加的**输入类型**，因香炉峰 MatrixTE 无块缩放通路而不可用；本节讨论的是**转换指令的目标格式**，两者含义不同（详见[微架构增量](../hardware/microarchitecture.md#sec:xsai-microarchitecture)的精度路线表）。
