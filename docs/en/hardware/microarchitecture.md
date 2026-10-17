# Microarchitecture Delta {#sec:xsai-microarchitecture}

XSAI adds a matrix coprocessor on top of Kunminghu V2R2. The scalar cores,
pipeline width, branch prediction and cache hierarchy are unchanged; this chapter
covers only what is new.

## Matrix compute unit (CUTE)

CUTE sits next to the scalar core. The core executes ZAMES / ZMASYNC instructions
and hands tasks to CUTE through the in-core control interface; when the work is
done, CUTE notifies the scalar side through the synchronization registers. XSAI
does not use RoCC here — it uses the in-core matrix control interface.

CUTE is organised into four subsystems:

![The four subsystems of CUTE](../figs/cute-subsystems.svg "The four subsystems of CUTE")

| Subsystem | Main components | Responsibility |
| --- | --- | --- |
| Control | TaskController | Accept instructions, decompose tasks, schedule execution |
| Storage | AB / C MatrixReg, MemoryLoader, LocalMMU | Data movement, buffering and address translation |
| Compute | MatrixTE, FReducePE, AfterOps | Matrix multiply-accumulate and post-processing |
| Interface | In-core AMU control interface, TileLink bus interface | Talking to the scalar core and the system bus |

## Compute pipeline

CUTE is organised as Load → Compute → Store, with two sets of MatrixReg used
alternately: while one tile is being computed, the next tile's data is already
loading in parallel.

![Load / Compute / Store with double buffering](../figs/load-compute-store.svg "Load / Compute / Store with double buffering")

* **Load**: MemoryLoader fetches from L2 / LLC / DDR through LocalMMU and writes
  into the AB / C MatrixReg;
* **Compute**: MatrixTE is an outer-product dataflow over the PE array, with
  backpressure;
* **Store**: results are written back to memory.

No software intervention is needed while the pipeline runs. The synchronization
mechanism is in "Synchronization and memory ordering" in
[Instruction Set Extensions](../isa/instruction-set.md#sec:xsai-instruction-set).

## Size of the matrix unit

The native tile shape and register capacities are in
[Data Registers](../isa/registers.md#sec:xsai-registers); L2 capacity and memory
access bandwidth are in [Memory Subsystem and HBL2](memory.md#sec:xsai-memory).
Software reads the shape through the probe and must not hard-code it.

## The async bit in the instruction encoding

Matrix instructions carry an `async` bit that distinguishes synchronous from
asynchronous matrix instructions. **This is an instruction-encoding bit and has
nothing to do with hardware clock domains** — do not read it as a clock-domain
flag. For the asynchronous execution semantics see "Synchronization and memory
ordering" in [Instruction Set Extensions](../isa/instruction-set.md#sec:xsai-instruction-set).

## Data supply

HBL2 is the high-bandwidth L2 added to improve data supply for the matrix unit;
matrix memory access takes a dedicated read path. Capacity, bandwidth and the
access interface are in [Memory Subsystem and HBL2](memory.md#sec:xsai-memory).
