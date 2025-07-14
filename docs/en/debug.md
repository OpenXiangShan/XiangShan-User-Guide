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
As illustrated below. The debug work of Kunming Lake is accomplished through the
collaboration of components such as debug software (GDB), debug agent service
(openocd), and debugger (debug module wrapper). The debugger includes JtagDTM,
DMI, and DM. The position of the debug interface within the entire CPU debugging
environment is shown in the following diagram. Here, the debug software and
debug agent service are interconnected via a network, the debug agent service
connects with the debugger through a Jtag emulator, and the debugger
communicates with the Jtag emulator's debug interface in JTAG mode.

![debug module](figs/debugmodule.svg "debug module")

The connection between the debugger and hart, as well as the clock domain
relationship, is shown in the following diagram:

![debug2harts](figs/debug2harts.svg "debug2harts")

The current implementation status of the Kunming Lake debug module is as
follows:

* Supports debugging from the first instruction, entering debug mode after CPU
  reset.
* Supports single-step debugging.
* Supports software breakpoints (ebreak instruction), hardware breakpoints
  (trigger), and memory breakpoints (trigger).
* Supports reading/writing CSRs and memory, with two access methods: progbuf and
  sysbus.

## Trigger Module
The current implementation status of Kunming Lake's trigger module is as
follows:

* The debug-related CSRs currently implemented in the Kunming Lake trigger
  module are shown in the table below.
* The default configuration count for triggers is 4 (supports user
  customization).
* Supports mcontrol6 type instructions and memory access triggers.
* Match supports three types: equal, greater than or equal, and less than
  (vector memory access currently only supports equal type matching).
* Only supports address matching, not data matching.
* Only supports timing = before.
* Supports chaining for one pair of triggers.
* To prevent the secondary generation of breakpoint exceptions by triggers,
  support is provided via xSTATUS.xIE control.
* Supports H-extension software and hardware breakpoints, and watchpoint
  debugging methods.
* Supports memory triggers for atomic instructions.

Table: Debug-related csr implemented in Kunming Lake

| Name              | Address | Read/Write | Introduction             | Reset value         |
| ----------------- | ------- | ---------- | ------------------------ | ------------------- |
| Tselect           | 0x7A0   | RW         | Trigger select register  | 0X0                 |
| Tdata1(Mcontrol6) | 0x7A1   | RW         | Trigger data1            | 0xF0000000000000000 |
| Tdata2            | 0x7A2   | RW         | trigger data2            | 0x0                 |
| Tinfo             | 0x7A4   | RO         | Trigger info             | 0x40                |
| Dcsr              | 0x7B0   | RW         | Debug Control and Status | 0x40000003          |
| Dpc               | 0x7B1   | RW         | Debug PC                 | 0x0                 |
| Dscratch0         | 0x7B2   | RW         | 调试暂存寄存器0                 | -                   |
| Dscratch1         | 0x7B3   | RW         | Debug Scratch Register 1 | -                   |

