---
file_authors_:
- Zhao Hong <zhaohong@bosc.ac.cn>
---

# Interruption Controller {#sec:interruption-controller}

In {{processor_name}}, the interrupt controller includes the IMSIC external
interrupt controller and the CLINT local interrupt controller. The following is
a detailed description.

## CLINT Interrupt Controller

### Overview

CLINT provides software interrupts at the M privilege level for HART, as well as
time timer interrupts at the M privilege level and a 64-bit time counter.

### Register Mapping

Table: CLINT Register Layout

| offset address | Width | attribute |                   Description                    |
| :------------: | :---: | :-------: | :----------------------------------------------: |
|  0x0000_0000   |  4B   |    RW     | HART M Software Interrupt Configuration Register |
|  0x0000_0004   |       |           |                                                  |
|       …        |       |           |                     Reserved                     |
|  0x0000_3FFF   |       |           |                                                  |
|  0x0000_4000   |  8B   |    RW     |                MTIMECMP register                 |
|  0x0000_4008   |       |           |                                                  |
|       …        |       |           |                     Reserved                     |
|  0x0000_BFF7   |       |           |                                                  |
|  0x0000_BFF8   |  8B   |    RW     |                  MTIME Register                  |


## IMSIC Interrupt Controller

### Overview

As one of RISC-V's external interrupt controllers, IMSIC is responsible for
receiving and transmitting MSI interrupts, covering interrupt reporting at the
M, S, and VS privilege levels. The interrupt configuration for each privilege
level is implemented through the IMSIC interrupt file MMIO space, which by
default supports 7 interrupt files: M, S, and 5 VS interrupt files. It also
supports valid interrupt numbers from 1 to 255 by default.

### Register Mapping

DEVICE sends an interrupt ID to the IMSIC internal interrupt file MMIO space to
achieve MSI transmission. The RISC-V AIA SPEC clearly stipulates that in
scenarios with multiple interrupt files, the Supervisor-level can only access
all Supervisor-level and guest interrupt files and cannot access Machine-level
interrupt files. Therefore, in address arrangement, all Machine-level interrupt
files are allocated continuously and collectively, while Supervisor-level and
guest interrupt files are also allocated continuously and collectively. This
ensures that only one PMP table entry is needed to guarantee that the
Supervisor-level does not have access permissions beyond S/VS interrupt files.
In hardware implementation, the M and S/VS interrupt file register spaces have
their own base addresses. The following explains the interrupt register access
for these two privilege levels.

Table: M interrupt file

| Register    | Address Offset | Bit Width | Attribute | Reset value | Description                                                                                                                                          |
| ----------- | -------------- | --------- | --------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| setipnum_le | 0x0000         | 32        | WO        | 32'h0       | Interrupt file access register. Write data is the MSI interrupt ID, read value is 0. By default, it supports writing the highest 8-bit interrupt ID. |


Table: S/VS Interrupt File

| Register        | Address Offset | Bit Width | Attribute | Reset value | Description                                                                                                                                                                                                                                                             |
| --------------- | -------------- | --------- | --------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| setipnum_le     | 0x0000         | 32        | WO        | 32'h0       | Interrupt file access register. Write data is the MSI interrupt ID, read value is 0. By default, it supports writing the highest 8-bit interrupt ID.                                                                                                                    |
| setipnum_le_s   | 0x0000         | 32        | WO        | 32'h0       | Interrupt file access register. The written data is the MSI interrupt ID, and the read value is 0. By default, it supports writing up to an 8-bit interrupt ID. If the MSI ID exceeds 8 bits during access, the hardware automatically truncates the lower 8 bits.      |
| setipnum_le_vs1 | 0x1000         | 32        | WO        | 32'h0       | VS 1 interrupt file access register. Write data is the MSI interrupt ID, read value is 0. By default, it supports writing the highest 8-bit interrupt ID. For MSI IDs exceeding 8 bits, the hardware automatically truncates the lower 8 bits.                          |
| setipnum_le_vs2 | 0x2000         | 32        | WO        | 32'h0       | VS 2 interrupt file access register. The written data is the MSI interrupt ID, and the read value is 0. By default, it supports writing up to an 8-bit interrupt ID. If the MSI ID exceeds 8 bits during access, the hardware automatically truncates the lower 8 bits. |
| setipnum_le_vs3 | 0x3000         | 32        | WO        | 32'h0       | VS 3 interrupt file access register. Write data is the MSI interrupt ID, read value is 0. By default, it supports writing the highest 8-bit interrupt ID. For MSI IDs exceeding 8 bits, the hardware automatically truncates the lower 8 bits.                          |
| setipnum_le_vs4 | 0x4000         | 32        | WO        | 32'h0       | VS 4 interrupt file access register. The written data is the MSI interrupt ID, and the read value is 0. By default, it supports writing up to an 8-bit interrupt ID. If the MSI ID exceeds 8 bits during access, the hardware automatically truncates the lower 8 bits. |
| setipnum_le_vs5 | 0x5000         | 32        | WO        | 32'h0       | VS 5 interrupt file access register. The written data is the MSI interrupt ID, and the read value is 0. By default, it supports writing up to an 8-bit interrupt ID. If the MSI ID exceeds 8 bits during access, the hardware automatically truncates the lower 8 bits. |

## Inter-core interrupt

Inter-core communication can be achieved through inter-core interrupts, which
can be implemented in two ways.

- By configuring the CLINT software interrupt, M privilege level interrupt
  reporting can be achieved.
- By configuring the IMSIC interrupt file, interrupt reporting can be achieved
  at the M, S, and VS privilege levels.
