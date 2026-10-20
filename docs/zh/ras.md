# ECC、总线错误与 RNMI {#sec:ras}

本章说明软件可见的 ECC 检查、总线错误、BEU 事件和可恢复 NMI（RNMI）处理。

## ECC 检查范围

| 保护对象 | 默认方式 | 检出错误后的软件可见行为 |
| --- | --- | --- |
| L1 ICache Meta/Data | parity | 向 BEU 报告、失效并从 L2 重取；重取收到总线错误时产生 Instruction Access Fault |
| L1 DCache Tag/Data | SECDED | 根据访问路径报告或传播；普通 Load 的精确本地错误路径由 `EnableAccurateLoadError` 控制且默认关闭 |
| L2 Tag/Data | SECDED | 可上报 BEU，也可通过 denied/corrupt 产生 Load 或 Instruction Access Fault、Hardware Error |
| L2 TLB Page Cache l0/l1 | 可选 SECDED，默认关闭 | 开启后错误项失效、返回 miss 并重新 Page Walk |

parity 可以检测奇数个比特错误，但无法检出偶数个比特错误。SECDED 编码具有单比特纠错能力，但当前缓存数据读路径没有将纠正后的数据接回输出。

## 同步异常

对于 CHI 读数据返回，单独出现一种错误时，普通数据 Load 的同步异常如下：

| 错误 | TL denied | TL corrupt | 数据 Load 结果 |
| --- | --- | --- | --- |
| Poison 非零 | 0 | 1 | Hardware Error（19） |
| DataCheck 校验失败 | 0 | 1 | 当前代码对有效错误响应设有断言 |
| RespErr=DERR | 0 | 1 | Hardware Error（19） |
| RespErr=NDERR | 1 | 1 | Load Access Fault（5） |

NC 和 MMIO Load 均按 denied 优先、`corrupt && !denied` 次之的规则分类。取指收到下级 corrupt 时产生 Instruction Access Fault（1）。预取、已取消或冲刷的请求不保证对应架构同步异常。

这些读返回错误通过 TL denied/corrupt 影响请求。接入 BEU 的后级路径会形成对应事件，例如 Uncache Store 将写完成失败形成 U_ECC。

DataCheck 是 CHI 链路数据校验，与缓存 SRAM 的本地 ECC 不同。当前实现将 DataCheck 校验失败并入 corrupt。代码对有效响应带有 DataCheck 错误的情况设有断言；L2 本地 BEU 上报条件由 Directory/DataStorage 的检查结果形成。

MMIO Store 的 CHI 写完成响应与读数据不同：DERR 和 NDERR 均转为 denied，返回 `AccessAck` 且 corrupt 为 0，最终产生 Store Access Fault（7）。NC Store 在提交后发送，失败形成 U_ECC 事件，不能追溯为原 Store 的普通精确异常。

同步异常按普通异常的原因选择、优先级和委托机制处理。MMIO Store 的写完成错误可同时形成 Store Access Fault 和 U_ECC 事件。

## BEU 寄存器

BEU 默认基址为 `0x38010000`，各寄存器间隔 8 字节。

| 偏移 | 名称 | 复位值 | 软件含义 |
| --- | --- | --- | --- |
| `0x00` | `cause` | 0 | 一份事件源编号记录 |
| `0x08` | `value` | 未定义 | 一份错误地址记录 |
| `0x10` | `enable` | 低四位 `0xF` | 事件更新 `cause`/`value` 的资格掩码 |
| `0x18` | `global_interrupt` | 0 | 与 `accrued` 相与后输出到 PLIC |
| `0x20` | `accrued` | 0 | 按事件源累积的事件位 |
| `0x28` | `local_interrupt` | 0 | 与 `accrued` 相与后输出本地 NMI31 |

| 编号 | 名称 | 来源 |
| --- | --- | --- |
| 0 | I_ECC | ICache 本地检查错误 |
| 1 | D_ECC | DCache 选中的本地错误报告 |
| 2 | U_ECC | Uncache Store 返回的 denied/corrupt |
| 3 | L2_ECC | L2 本地检查错误 |

`enable` 只影响 `cause`/`value` 的捕获，不直接控制 `accrued` 或中断输出。本地中断条件为 `(accrued & local_interrupt) != 0`，全局中断条件为 `(accrued & global_interrupt) != 0`；两种中断掩码的复位值均为 0。

`cause` 和 `value` 只有一份记录，`accrued` 没有错误计数和逐事件地址队列。同周期多个源按实现中的源处理顺序依次获得捕获机会，后处理的记录会覆盖先处理的记录。I_ECC 的编号也是 0，而硬件仅在 `cause == 0` 时接受新记录，因此 `cause == 0` 不能表示没有错误，I_ECC 地址也可能被后续记录覆盖。软件应保存 `cause`、`value` 和 `accrued`，并结合错误源处理。`accrued` 当前是普通读写寄存器，不能按 W1C 处理。

## RNMI {#sec:ras-rnmi}

当前 NMI31 输入是外部 NMI31 与 BEU 本地中断的按位或结果，NMI43 来自另一条外部输入。两者同时待处理时，NMI43 的优先级高于 NMI31。NMI 的接收不依赖普通 `mstatus.MIE` 和 `mie` 使能路径，但受 `mnstatus.NMIE`、调试和单步状态约束。

RNMI 进入时切换到 M 模式，保存 `mnepc`、`mncause`、`mnstatus.MNPP/MNPV`，并清零 `NMIE`。当前入口复用 `mtvec`：Direct 模式从 BASE 进入，Vectored 模式从 BASE + 4 × cause 进入。返回使用 `mnret`，恢复保存状态并重新置位 `NMIE`。`NMIE` 复位值为 0；RNMI 处理期间再次发生非调试陷入会进入 critical-error 处理，不能按普通可嵌套异常处理。

软件处理 RNMI 时应检查 `mncause` 和 BEU 记录。`mnepc` 是被中断位置，不是 ECC 错误访问的精确地址；`value` 的粒度也取决于事件源。处理程序应处理持续错误源和已累积事件后再执行 `mnret`，否则返回后可能再次进入 RNMI。

## 错误注入

ICache 和 DCache 提供 MMIO 错误注入接口，用于测试本地检错路径。ICache 注入使用目标物理地址，`istatus` 为 2 表示完成、为 7 表示失败；终态读取后清零，因此必须从同一次读取快照中同时解析 `istatus` 和 `ierror`。DCache 注入支持 Tag/Data、bank、延迟注入和持续注入，具体寄存器见设计文档中的 DCache 错误处理章节。
