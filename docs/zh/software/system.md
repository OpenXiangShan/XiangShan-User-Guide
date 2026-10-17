# 系统软件与运行时 {#sec:sw-system}

矩阵能力要先被固件和操作系统发现，软件才敢用。本章讲设备树怎么描述这个能力、内核与运行时各自要做什么，以及上下文切换和恢复流程的边界。

## 设备树与能力发现

* 矩阵能力通过设备树 `riscv,isa-extensions` 条目（如 `zame`、`zammai8i32`）与 `xmisa` CSR 描述；`riscv,matrix-isa-caps` 是提案中的属性名，当前实现未使用；
* 固件负责填充能力描述，操作系统与运行时据此决定是否启用矩阵路径；
* 上报的能力必须与 RTL 实际配置一致，否则软件会按错误的 tile 尺寸生成核。

### 设备树属性完整列表

生成的 `xiangshan_ai.dts` 中 `/cpus/cpu@0` 节点（`firmware/nemu_board/dts/build/xiangshan_ai.dts:28-40`）包含：

| 属性 | 值 / 说明 |
| --- | --- |
| `reg` | `0x00` |
| `riscv,isa` | `rv64imafdcv`（基础 ISA 字符串） |
| `riscv,isa-base` | `rv64i` |
| `riscv,isa-extensions` | 扩展列表，见下 |
| `riscv,cbom-block-size` / `cbop-block-size` / `cboz-block-size` | 均为 `0x40`（Zicbom / Zicbop / Zicboz 的块大小） |
| `interrupt-controller` | 子节点，`compatible = "riscv,cpu-intc"`，`#interrupt-cells = <0x01>` |
| `timebase-frequency` | 由 `DTSGen.py` 的 `--timebase-freq` 决定，**默认 10 MHz** |

`riscv,isa-extensions` 的完整取值：

```text
i m a f d c v supm zame zammai8i32 zawrs zba zbb zbs zcb zcmop zfa zfhmin
zicbop zicbom zicboz zicntr zicond zicsr zihpm zihintpause zihintntl zimop
zkt zvbb zvfhmin zvkt
```

其中矩阵相关的是 **`zame`**（Attached Matrix Extension）与 **`zammai8i32`**（i8 × i8 → i32 的矩阵乘加）。

**能力发现的约定**：多字母扩展不占 `misa` 的位，而是通过 `riscv,isa-extensions` 上报一个**小写扩展名字符串列表**，软件在其中检查 `"zames"` / `"zame"` 等字符串来判断是否存在对应扩展（`riscv-matrix-spec/spec/program_model.adoc:360`）。

**上报必须与 RTL 实际配置一致**——软件按上报内容决定 tile 尺寸与指令可用性，不一致会导致按错误规格生成核。

## 操作系统支持

### 内核版本与补丁集

| 项 | 值 |
| --- | --- |
| 内核版本 | **6.18**（`firmware/Makefile:48` 的 `LINUX_VERSION`，取自 `linux-6.18.tar.xz`） |
| 补丁集 | `firmware/patches/` 下三个补丁，由 `apply-matrix-patch.sh` 依次应用 |

| 补丁 | 用途 |
| --- | --- |
| `0001-riscv-matrix-first-use-support.patch` | 矩阵扩展的 **first-use trap** 支持（新增 `asm/matrix.h`、`kernel/matrix.c`，并在 `traps.c` 的 `do_trap_insn_illegal` 中挂接） |
| `0002-riscv-pmu-sbi-legacy-default-keep-fixed-counters.patch` | PMU / SBI 兼容：保留固定计数器 |
| `0003-riscv-fix-system-csr-immediate-mask-width.patch` | 修正 system CSR 立即数掩码宽度 |

向量相关配置项 `CONFIG_RISCV_ISA_V` 与 `CONFIG_RISCV_ISA_V_DEFAULT_ENABLE` 在 `.config` 中。注意 `CONFIG_RISCV_ISA_SUPM` 是**用户态指针屏蔽扩展**（`Smnpm` / `Ssnpm`）的配置项，与矩阵无关，不要用它开启矩阵支持。

### 矩阵状态的上下文切换

内核把矩阵状态按**与向量状态同构**的方式处理，机制是 **first-use trap**：

`SR_MS` 对应 `mstatus[26:25]`，取值与 CSR 章一致（`OFF = 0x00000000`、`INITIAL = 0x02000000`、`CLEAN = 0x04000000`、`DIRTY = 0x06000000`）。`asm/matrix.h` 提供三个内联操作：

```c
static inline void riscv_m_vstate_off(struct pt_regs *regs)
{
    regs->status = (regs->status & ~SR_MS) | SR_MS_OFF;
}

static inline void riscv_m_vstate_on(struct pt_regs *regs)
{
    regs->status = (regs->status & ~SR_MS) | SR_MS_INITIAL;
}

static inline bool riscv_m_vstate_query(struct pt_regs *regs)
{
    return (regs->status & SR_MS) != 0;
}
```

流程：

1. **任务切换出去时**把 `MS` 置为 `Off`（`process.c` 中 `riscv_m_vstate_off(task_pt_regs(current))`，注释写明 "Reset matrix state for userspace first-use flow"），从而**不需要保存矩阵寄存器堆**；
2. **首次使用**时若 `MS = Off`，内核期望收到非法指令陷入，由 `riscv_m_first_use_handler` 判定该指令是否为矩阵指令：
   * 指令是 4 字节且 opcode 属于 `custom0` – `custom3`（`0x0b` / `0x2b` / `0x5b` / `0x7b`），或
   * 是 system 类且 CSR 落在 `[0x802, 0x80a]`（XMCSR 区间）或 `[0xcc0, 0xcc7]`（XMINFO 区间）；
3. 判定成立则把 `MS` 置为 `Initial` 并**重试该指令**，用户态无需显式使能。

> **实现分歧**：该 handler 假定 `MS = Off` 时执行矩阵指令会陷入，但当前 RTL 中解码侧消费 `msIsOff` 的三处检查**全部被注释**，因此 RTL 尚不产生该陷入。详见[异常与中断](../isa/exception.md#sec:xsai-exception)。

内核侧只在 CSR 层面管理 `MS` 位，**不保存 / 恢复矩阵寄存器堆内容**——这与 [Checkpoint 与切片](../verification/checkpoint.md#sec:debug-checkpoint)记录的 checkpoint 缺口是同一件事的两面。

## 运行时与内存

* 矩阵操作数必须位于物理连续内存池；池基址由运行期解析（环境变量 → 设备树 `direct_map` → 编译期默认值），不是固定值；默认布局为 6 GiB @ `0x1_0000_0000`，mega 布局为 4 GiB @ `0x3_8000_0000`，详见[内存子系统与 HBL2](../hardware/memory.md#sec:xsai-memory)；
* 分配模式（池模式 / 匿名模式）必须由外部环境决定，不能编进产物：
  * 匿名模式只用于 QEMU 用户态；
  * 若被无条件带入板上，表现为 `SIGABRT`（`rc=134`），或匿名池下算错、被进程内的条件检查拦下（`rc=255`）。
* AMU 行寻址按 `PA_base + row × stride` 计算且不逐行重查 TLB，非连续缓冲在行数较大时会静默读错。

## 启动流程

### GCPT 恢复启动

`firmware/gcpt_restore/` 是 LibCheckpointAlpha，一个过渡版本，提供两种用法：

| 用法 | 构建方式 | 效果 |
| --- | --- | --- |
| 恢复 checkpoint | `make clean && make` | 恢复时覆盖 `0x80000000` 起 `sizeof(gcpt.bin)` 的区域 |
| 链接下一级 bootloader | `make clean && make GCPT_PAYLOAD_PATH=/path/to/bbl.bin` | `gcpt.bin` 可直接启动 |

链接顺序：LibCheckpointAlpha 可链接 riscv-pk 或 OpenSBI 作为下一级 bootloader。

**启动位置决定行为**：

* `gcpt.bin` 加载到 **flash** 时，无论是否链接了 payload，都跳到 `0x80000000` 或从 flash 镜像恢复 checkpoint；
* `gcpt.bin` 加载到 **内存**时，链接了 payload 则跳到 `0x80100000`，否则从内存镜像恢复 checkpoint。

支持的 ISA 字符串为 `rv64gcbkhv`。

**限制**（与矩阵相关，须一并考虑）：

* checkpoint 载荷**不包含矩阵寄存器堆与矩阵 CSR**，只有 `mstatus.MS` 位随 `mstatus` 恢复；
* 因此矩阵切片的采样点必须让矩阵单元处于静止态，且恢复后不得假设矩阵配置寄存器与采样点一致。

完整流程与验收标准见 [Checkpoint 与切片](../verification/checkpoint.md#sec:debug-checkpoint)。
