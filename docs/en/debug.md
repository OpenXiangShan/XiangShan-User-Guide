---
file_authors_:
- ChengGuanghui <wissycgh@gmail.com>
---

# Debug Module {#sec:debug}

This chapter is the design document for the Kunminghu debug module. The
Kunminghu debug module is compatible with the RISC-V Debug V0.13 Specification.
The external debug interface supports JTAG. The debug interface serves as a
communication channel between software and the processor. Users can obtain the
state of the CPU, including register and memory contents, as well as information
from other on-chip devices, through the debug interface. It also supports
program download.

## Debug Module
如下图所示。昆明湖的 debug 工作是由调试软件（GDB）、调试代理服务程序(openocd)、调试器(debug module
wrapper)等组件一起配合完成的， 其中调试器包括 JtagDTM， DMI， DM。 调试接口在整个 CPU 调试环境中的位置如下图所示。
其中，调试软件和调试代理服务程序通过网络互联，调试代理服务程序与调试器通过 Jtag 仿真器连接， 调试器与 Jtag 仿真器的调试接口以 JTAG 模式通信。

![debug module](figs/debugmodule.svg "debug module")

调试器与hart之间的连接以及时钟域关系如下图所示：

![debug2harts](figs/debug2harts.svg "debug2harts")

当前昆明湖debug module实现的情况如下：

* 支持从第一条指令开始的调试，在 cpu 复位之后进入调试模式。
* 支持单步调试。
* 支持软断点(ebreak 指令)、硬断点（trigger）和内存断点（trigger）。
* 支持读写CSR和内存，支持 progbuf 和 sysbus 两种访存方式。

## Trigger Module
当前昆明湖 trigger module 的实现情况如下：

* 昆明湖 trigger module 当前实现的 debug 相关的 CSR 如下表所示。
* trigger 的默认配置数量是 4 (支持用户自定义配置)。
* 支持 mcontrol6 类型的指令、访存的 trigger。
* match 支持相等，大于等于，小于三种类型（向量访存当前只支持相等类型匹配）。
* 仅支持 address 匹配，不支持 data 匹配。
* 仅支持 timing = before。
* 支持一对 trigger 的 chain。
* 为了防止 trigger 的二次产生 breakpoint 的异常，支持通过 xSTATUS.xIE 控制。
* 支持H扩展的软硬件断点，watchpoint 调试手段。
* 支持原子指令的访存 trigger。

Table: 昆明湖实现的 debug 相关的 csr

| 名称                | 地址    | 读写  | 介绍                       | 复位值                 |
| ----------------- | ----- | --- | ------------------------ | ------------------- |
| Tselect           | 0x7A0 | RW  | trigger 选择寄存器            | 0X0                 |
| Tdata1(Mcontrol6) | 0x7A1 | RW  | trigger data1            | 0xF0000000000000000 |
| Tdata2            | 0x7A2 | RW  | trigger data2            | 0x0                 |
| Tinfo             | 0x7A4 | RO  | trigger info             | 0x40                |
| Dcsr              | 0x7B0 | RW  | Debug Control and Status | 0x40000003          |
| Dpc               | 0x7B1 | RW  | Debug PC                 | 0x0                 |
| Dscratch0         | 0x7B2 | RW  | Debug Scratch Register 0 | -                   |
| Dscratch1         | 0x7B3 | RW  | Debug Scratch Register 1 | -                   |

