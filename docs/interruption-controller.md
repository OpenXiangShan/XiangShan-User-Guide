---
file_authors_:
- Zhao Hong <zhaohong@bosc.ac.cn>
---

## 中断控制器

{{var_processor_name}} 中，中断控制器包括 IMSIC 外部中断控制器，CLINT 本地中断控制器，下面进行详细说明。

### CLINT 中断控制器

#### 概要介绍

CLINT 为 HART 提供 M 特权级下的软件中断，以及 M 特权级下的 time 定时中断，以及 64bit time 计时器。

#### 寄存器映射

Table: CLINT 的寄存器排布

| offset address	| Width	| attribute	| Description	| Notes |
| :---------: | :------------: | :---------: | :---------: | :---------: |
| 0x0000_0000 |	4B	| RW	| HART M 软中断	| HART M 软件中断配置寄存器(1-bit wide)。|
| 0x0000_0004 …  0x0000_3FFF  |		|       |	Reserved	|                      |
|0x0000_4000 |	8B	| RW	| HART M 态time中断阈值	| MTIMECMP 寄存器
| 0x0000_4008 … 0x0000_BFF7 |		|       |	Reserved	|                      |
| 0x0000_BFF8 | 8B  | 	RW	|  HART M 态time | 	Time 寄存器                    |


### IMSIC 中断控制器

### 概要介绍

IMSIC 作为 RISCV 的外部中断控制器之一，负责 MSI 中断的接收与传递，涵盖 M, S, VS 特权级下的中断上报 。
每种特权级下的中断配置通过 IMSIC interrupt file MMIO 空间实现，默认支持 interrupt file 数目 7 个： M, S,5 个 VS interrupt file.默认支持有效中断号：1-255.

### 寄存器映射

DEVICE 通过发送中断 ID 到 IMSIC 内部 interrupt file MMIO 空间，从而实现 MSI 的发送。
RISCV AIA SPEC明确规定，多 interrupt files 场景下, Supervisor-level 只能访问 all Supervisor-level and guest interrupt files,不能访问 Machine-level interrupt files.
因此，在地址排布上，所有的 Machine-level interrupt file 集中连续分配，Supervisor-level and guest interrupt files 集中连续分配，这样仅用一个 PMP table entry 就能保证 Supervisor-level 没有 S/VS interrupt files 以外的访问权限。
硬件实现上，M, S/VS interrupt file 寄存器空间，拥有各自的基地址。如下对两个特权级下的中断寄存器访问进行说明。

Table: M interrupt file

| reg name | reg description | offset address | data width | attribute | reset value | member description |
| :------- | :-------------- | :------------- | :--------- | :-------- | :---------- | :----------------- |
| setipnum_le | interrupt file 访问寄存器。 | 0x0000         | 32         | WO        | 32'h0       | "interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入。" |


Table: S/VS interrupt file

| reg name | reg description | offset address | data width | attribute | reset value | member description |
| :------- | :-------------- | :------------- | :--------- | :-------- | :---------- | :----------------- |
| setipnum_le     | interrupt file 访问寄存器。     | 0x0000         | 32         | WO        | 32'h0       | "interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入。"                                              |
| setipnum_le_s   | S interrupt file 访问寄存器。   | 0x0000         | 32         | WO        | 32'h0       | "interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入，MSI ID 超过8bit访问，硬件自动截断低8bit."      |
| setipnum_le_vs1 | VS1 interrupt file 访问寄存器。 | 0x1000         | 32         | WO        | 32'h0       | "VS 1 interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入，MSI ID 超过8bit访问，硬件自动截断低8bit." |
| setipnum_le_vs2 | VS2 interrupt file 访问寄存器。 | 0x2000         | 32         | WO        | 32'h0       | "VS 2 interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入，MSI ID 超过8bit访问，硬件自动截断低8bit." |
| setipnum_le_vs3 | VS3 interrupt file 访问寄存器。 | 0x3000         | 32         | WO        | 32'h0       | "VS 3 interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入，MSI ID 超过8bit访问，硬件自动截断低8bit." |
| setipnum_le_vs4 | VS4 interrupt file 访问寄存器。 | 0x4000         | 32         | WO        | 32'h0       | "VS 4 interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入，MSI ID 超过8bit访问，硬件自动截断低8bit." |
| setipnum_le_vs5 | VS5 interrupt file 访问寄存器。 | 0x5000         | 32         | WO        | 32'h0       | "VS 5 interrupt file 访问寄存器。写入数据为MSI 中断ID，读取值为0.默认支持最高8bit中断ID写入，MSI ID 超过8bit访问，硬件自动截断低8bit." |

### 核间中断

多核间通信可以通过核间中断来完成，核间中断有两种方式可以实现。

- 通过配置 CLINT 软件中断，可实现 M 特权级中断上报。
- 通过配置 IMSIC interrupt file，可实现 M, S, VS 特权级下的中断上报。
