---
file_authors_:
- Tang Haojin <tanghaojin@outlook.com>
---

# Processor Profile {#sec:processor}

## Block Diagram

The block diagram of the structure of {{processor_name}} is shown in
[@fig:kmh-multicore].

![Microarchitecture structure of
{{processor_name}}](figs/kmh-multicore.svg){#fig:kmh-multicore}

## Core Subsystem

The core subsystems of {{processor_name}} mainly include: the instruction fetch
unit (IFU), instruction decode unit (IDU), rename unit, out-of-order dispatch
and issue unit, integer execution unit (IntExu), floating-point execution unit
(FPExu), vector execution unit (VecExu), memory unit (LSU), reorder buffer
(ROB), memory management unit (MMU), physical memory protection unit (PMP/PMA),
and level-2 cache (L2 Cache).

### Instruction Fetch Unit

The instruction fetch unit retrieves instructions from memory and performs
preliminary processing, handling up to 32 bytes of instructions per cycle. To
enhance fetch efficiency, {{processor_name}} incorporates structures such as
ICache, FDIP, and BPU, featuring low power consumption, high branch prediction
accuracy, and high instruction prefetch accuracy.

### Instruction Decode Unit

The instruction decode unit receives instructions from the fetch unit and
decodes them. It can process up to six simple instructions per cycle and
supports instruction fusion technology. For complex instructions such as most
vector operation instructions, the decode unit splits them into multiple
micro-operations for subsequent execution units to handle.

### Rename Unit

The rename unit maps logical registers in decoded instructions to physical
registers. To further expand the out-of-order scheduling window, it also
implements ROB compression. Additionally, the rename unit eliminates move
instructions by bypassing operands, removing their execution time.

### Out-of-Order Scheduling Unit

The out-of-order scheduling unit is divided into the dispatch unit and the issue
unit. The dispatch unit assigns instructions to different execution queues based
on their type. The issue unit is responsible for issuing instructions to
execution units based on their readiness and reading register file values after
issuance.

### Execution Unit

The execution unit comprises the integer execution unit, floating-point
execution unit, and vector execution unit.

The integer execution unit includes the Arithmetic Logic Unit (ALU),
Multiplication Unit (MUL), Division Unit (DIV), Branch Jump Unit (BJU), and
Control Status Unit (CSR). The ALU performs 64-bit integer operations. The MUL
handles integer multiplication. The DIV unit employs a radix-16 SRT algorithm,
with execution cycles varying based on operands. The BJU calculates jump
addresses in a single cycle and determines branch prediction accuracy. The CSR
processes control status register read/write instructions and optimizes
pipelining for certain CSR read operations.

The floating-point execution unit consists of the floating-point arithmetic
logic unit (FALU), floating-point multiply-accumulate unit (FMA), floating-point
division unit (FDIV), and floating-point conversion unit (FCVT). The FALU
handles addition, subtraction, comparison, sign injection, classification, etc.
The FMA handles standard multiplication, fused multiply-accumulate, etc. The
FDIV handles floating-point division, etc. The FCVT handles floating-point
conversion, etc.

The vector execution unit is broadly divided into the vector integer execution
unit and the vector floating-point execution unit, with the integer and
floating-point units further subdivided into arithmetic logic units,
multiply-accumulate units, floating-point units, and conversion units, among
others.

### Memory Unit

The memory unit supports the issuance and execution of up to three integer load
instructions, two integer store instructions, and two vector memory
microinstructions per cycle, and enables non-blocking access to the DCache. It
supports byte, half-word, word, double-word, and quad-word store/load
instructions, as well as sign and zero extension for byte and half-word load
instructions. Memory instructions can be pipelined, allowing a single memory
pipeline to achieve a data throughput of one access per cycle. Various
prefetching techniques are supported to reduce DCache miss rates and improve
memory efficiency. In the event of a DCache miss, parallel bus access is
supported.

### Reorder Buffer

The reorder buffer (ROB) is responsible for out-of-order writeback and in-order
retirement of instructions. By supporting parallel writeback and fast retirement
of instructions, it enhances retirement efficiency. Through the rename alias
buffer (RAB), it decouples instruction commit from register commit, further
improving retirement efficiency while reducing ROB overhead. The ROB can retire
up to eight instructions per cycle and supports precise exceptions.

### Memory Management Unit

The Memory Management Unit (MMU) supports Sv39 and Sv48, converting 39-bit or
48-bit virtual addresses into 48-bit physical addresses. It also supports the H
extension, two-stage address translation, Sv39x4 and Sv48x4, as well as the PBMT
extension.

For specific content, refer to [@sec:memory-model] [Memory
Model](memory-model.md).

### Physical Memory Protection Unit

The physical memory protection unit includes physical memory protection (PMP)
and physical memory attributes (PMA). PMP implementation follows the RISC-V
manual and supports 16 entries by default.

The PMA implementation adopts a PMP-like approach, utilizing two reserved bits
in the PMP Configure register for atomic and cacheable attributes, indicating
support for atomic operations and cacheability, respectively. By default, it
supports 16 entries.

The minimum granularity for PMP and PMA is 4KB, hence NA4 mode is not supported.

For specific content, refer to [@sec:memory-model] [Memory
Model](memory-model.md).

### Level-2 Cache

The L2 cache adopts a banked pipeline architecture, capable of processing 64
cacheable address space memory requests per cycle in parallel (including
requests from DCache, ICache, PTW, prefetch requests, snoop requests, etc.). By
default, the L2 Cache is 1MB in size, divided into 4 banks with an 8-way
set-associative organization and an inclusive policy.

The L2 cache external interface supports CHI Issue B and CHI Issue E.b, with
cross-clock and cross-voltage domain handling.

For interface details, refer to [@sec:bus-interface] [Bus
Interface](bus-interface.md).

## Multicore Subsystem

The multicore subsystem of {{processor_name}} includes the interrupt controller,
timer, and debug system.

### Interrupt Controller

The interrupt controller consists of the incoming message signal interrupt
controller (IMSIC) and the core-local interrupt controller (CLINT). IMSIC
supports seven interrupt files (M + S + 5 VS) by default and 254 valid interrupt
numbers. CLINT handles software interrupts and timer interrupts.

For specific content, refer to [@sec:interruption-controller] [Interrupt
Controller](interruption-controller.md).

### Timer

The timer reuses the mtime register from CLINT and broadcasts the timer value to
various core subsystems to support functions such as reading the time register
and the Sstc extension.

For specific content, refer to [@sec:interruption-controller] [Interrupt
Controller](interruption-controller.md).

### Debug System

The Kunminghu Debug System complies with the RISC-V Debug V0.13 standard and
supports JTAG as the external debug interface. It enables debugging of different
core subsystems through a shared JTAG interface.

For details, refer to [@sec:debug] [Debug](debug.md).
