# 矩阵 CSR {#sec:xsai-csr}

本章只列出相对昆明湖 V2R2 新增或语义有变化的 CSR 内容。读本章前需要读过[数据寄存器](registers.md#sec:xsai-registers)与[指令集扩展](instruction-set.md#sec:xsai-instruction-set)。

## 矩阵相关 CSR

昆明湖 V2R2 基线没有矩阵状态、矩阵 tile 状态或矩阵脏状态的体系化定义。香炉峰新增了一组矩阵 CSR 与架构可见状态。

**RTL 与 QEMU 的地址定义当前不一致**，取用前必须确认自己面向哪一侧：

| CSR（汇编可见名） | RTL 地址 | QEMU 地址 | 类别 | 含义 |
| --- | --- | --- | --- | --- |
| `mcsr` | `0x802` | `0x802` | 读写 | 矩阵控制状态 |
| `mxrm` | `0x806` | `0x806` | 读写 | 矩阵舍入模式 |
| `msat` | `0x807` | `0x807` | 读写 | 矩阵饱和标志 |
| `mfflags` | `0x808` | `0x808` | 读写 | 矩阵浮点标志 |
| `mfrm` | `0x809` | `0x809` | 读写 | 矩阵浮点舍入模式 |
| `msaten` | `0x80A` | — | 读写 | 矩阵状态使能 |
| `xmisa` | **不存在** | `0xcc0` | 只读常量 | 矩阵 ISA 能力描述 |
| `tlenb` | `0xcc1` | `0xcc1` | 只读常量 | tile 寄存器长度（bytes），即 `TLEN / 8` |
| `trlenb` | `0xcc2` | `0xcc2` | 只读常量 | tile 行宽（bytes），即 `TRLEN / 8` |
| `alenb` | `0xcc3` | `0xcc3` | 只读常量 | 累加器长度（bytes），即 `ALEN / 8` |
| `mtilem` | **`0xcc4`** | `0xcc5` | 读写 | 当前 M 维 tile 形状 |
| `mtilen` | **`0xcc5`** | `0xcc6` | 读写 | 当前 N 维 tile 形状 |
| `mtilek` | **`0xcc6`** | `0xcc7` | 读写 | 当前 K 维 tile 形状 |
| `msync` | **`0xcc7`** | 未定义 | 只读 | sync 寄存器数量 |

**三处差异必须注意**：

1. **命名有两套**：RTL Scala 符号不带 `x` 前缀（`mxrm` / `msat` / `mfflags` / `mfrm` / `msaten` / `tlenb`…），而规范文档与 QEMU 宏用 `x` 前缀（`xmxrm`、`CSR_XTLENB`…）。两者指同一组 CSR，写文档或代码时需要统一。
2. `mtilem` / `mtilen` / `mtilek` 在 RTL 中是 `0xcc4` – `0xcc6`，在 QEMU 中是 `0xcc5` – `0xcc7`，整体错开一位；且 `0xcc7` 在 RTL 是 `msync`、在 QEMU 是 `mtilek`，**同一地址两侧含义不同**。
3. `xmisa`（`0xcc0`）只存在于 QEMU，RTL 的矩阵 CSR 从 `0xcc1` 起，无 `0xcc0`。

因此不能假设 RTL 与 QEMU 对这些 CSR 的行为一致；涉及 `mtile*` / `msync` / 名称前缀的用例应在两侧分别验证。

固件探针按裸地址读取前三个长度 CSR：

```c
__asm__ volatile("csrr %0, 0xcc1" : "=r"(tlenb));   /* tlenb  */
__asm__ volatile("csrr %0, 0xcc2" : "=r"(trlenb));  /* trlenb */
__asm__ volatile("csrr %0, 0xcc3" : "=r"(alenb));   /* alenb  */
```

### 访问权限

矩阵 CSR 分属两个自定义地址区间：

| 区间 | 名称 | 归属 |
| --- | --- | --- |
| `[0x800, 0x8ff]` | XMCSR | 非特权自定义 CSR（读写），如 `mcsr`、`mxrm`、`msat` |
| `[0xcc0, 0xcff]` | XMINFO | 非特权自定义 CSR（只读），如 `xmisa`、`tlenb`、`mtile*` |

**不要从寄存器名的 `m` 前缀推断权限级**：`mcsr` / `mxrm` / `msat` 虽以 `m` 开头，仍属非特权自定义区间，非 M 模式下的可访问性由 `mstateen0.C` 等状态使能控制，而不是"因为是 M 模式 CSR 而无条件禁止"。

## 尺寸探针 {#sec:matrix-probe}

软件在启用矩阵路径前，应通过 CSR 读取当前 hart 的原生 tile 尺寸，并按读到的值生成核：**配置寄存器里的形状参数只在原生尺寸范围内才保证正确**，探针结果是唯一的来源。

三个长度 CSR 读出后，行数按 `rows = tlenb / trlenb` 得出，即 M 与 N 的上限。原生尺寸是 M128 × N128 × K64，但**不要按这个数字写死，也不要假设所有 hart 都相同**——三个长度 CSR 是唯一可靠的来源，用错尺寸不会报错，只会算错。期望值与 tile 参数怎么用见[数据寄存器](registers.md#sec:xsai-registers)。

## 精度能力描述

矩阵精度能力不在 CSR 位图中表达，改由设备树描述输入 / 输出类型组合：当前实现使用 `riscv,isa-extensions` 条目配合 `xmisa` CSR。矩阵相关的两项是：

| 字符串 | 含义 |
| --- | --- |
| `zame` | Attached Matrix Extension |
| `zammai8i32` | i8 × i8 → i32 的矩阵乘加 |

固件在生成设备树时按 `XSAI_EXTRA_ISA_EXTENSIONS` 追加扩展名：

```make
XSAI_EXTRA_ISA_EXTENSIONS ?= zame zammai8i32
```

完整 `riscv,isa-extensions` 串见[系统软件与运行时](../software/system.md#sec:sw-system)。

### 解析示例

多字母扩展不占 `misa` 位，而是作为小写扩展名字符串列表上报，在按 NUL 分隔的列表中做字符串匹配：

```c
/* 设备树属性以 NUL 分隔的字符串序列给出 */
static bool dt_has_extension(const char *list, size_t len, const char *want)
{
    for (const char *p = list; p < list + len; p += strlen(p) + 1) {
        if (strcmp(p, want) == 0)
            return true;
    }
    return false;
}

/* 用法 */
if (!dt_has_extension(isa_ext, isa_ext_len, "zame"))
    return -ENODEV;                 /* 无矩阵扩展，整条矩阵路径关闭 */
```

**不要用 `RISCV_ISA_EXT_SUPM`（`CONFIG_RISCV_ISA_SUPM`）检测矩阵能力**：它对应用户态指针屏蔽扩展，与矩阵无关；用它做判断会在只有指针屏蔽的机器上误开矩阵路径。矩阵能力应结合[尺寸探针](#sec:matrix-probe)的 CSR 读取判定。

**注意能力串与 tile 尺寸是两件事**：能力串只说明"有矩阵扩展"，具体的原生尺寸仍须由长度 CSR 探针读取。

## 扩展使能与状态

`mstatus`、`sstatus`、`vsstatus` 中新增 **`MS` 状态域**表达 matrix state。`MS` 被纳入 `SD` 脏状态聚合语义，与既有的浮点 / 向量状态并列进入架构级脏状态管理框架。`MS` 状态域的编码与 first-use trap 行为见[异常与中断](exception.md#sec:xsai-exception)。

### 保存与恢复

矩阵架构状态与保存方式：

| 状态 | 保存方式 |
| --- | --- |
| `tr0` – `tr3`、`acc0` – `acc3` | whole-register 传输（`msa.whole` / `mla.whole`），按完整寄存器搬运，不解释 element type |
| `mcfg0` – `mcfg7` | `msetcfg` / `mgetcfg` 读写；恢复时需重建 raw 值 |
| `mcsr` 及其余配置位（`mxrm` / `msat` / `mfflags` / `mfrm` / `msaten`） | 普通 CSR 读写 |
| `mstatus.MS` | 随 `mstatus` 保存；`MS` 为 `Off` 时矩阵寄存器内容可丢弃，可不做完整保存 |

**内核的实际做法是不保存**：任务切换出去时把 `MS` 置为 `Off`，依赖 first-use trap 在下次使用时重新使能，从而免去矩阵寄存器堆的保存开销。详见[系统软件与运行时](../software/system.md#sec:sw-system)。

## 与操作系统 / 固件的接口

| 环节 | 约定 |
| --- | --- |
| 能力上报 | 设备树 `riscv,isa-extensions` 由 `XSAI_EXTRA_ISA_EXTENSIONS` 生成，**必须与 RTL 实际配置一致** |
| 自定义 CSR 放行 | OpenSBI 置 `mstateen0.C` / `sstateen0.C`，否则非 M 模式访问矩阵 CSR 被拒 |
| 内核补丁 | 由 `firmware/patches/apply-matrix-patch.sh` 应用，其中 `0001` 提供矩阵 first-use trap |
| checkpoint 恢复 | `gcpt_restore` 的恢复清单**不含任何矩阵 CSR**；只有 `mstatus.MS` 位随 `mstatus` 恢复 |

操作系统侧注意事项：

* 矩阵状态按与向量同构的方式管理，用 first-use trap 免去保存；内核只在 CSR 层面维护 `MS` 位；
* 内核判定矩阵 CSR 的区间包含 `0xcc0`，但当前 RTL 并无 `0xcc0` 这一 CSR（见上表的地址差异）；以实际 hart 行为为准。
