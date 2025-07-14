---
file_authors_:
- pengxiao <384756158@qq.com>
- yimingyan <1650150317@qq.com>
---

# Memory Subsystem {#sec:memory-subsystem}

## L1 Instruction Cache

### Overview

The main features of the L1 instruction cache are as follows:

* The instruction cache size is configurable, supporting 16K/32K/64K.
* 4-way set-associative, cache line size of 64B
* Support refresh
* Uses the PLRU replacement algorithm
* Supports providing two consecutive cache lines
* Supports instruction prefetching.
* Configurable MSHR management for fetch and prefetch requests.
* Supports way lookup.
* Supports ECC Check
* Supports checking address translation errors and physical memory protection
  errors

### Way lookup queue.

To improve cache hit rates and access speed, {{processor_name}} implements a Way
Lookup Queue (WayLookUp) for the high-speed instruction cache. The Way Lookup
Queue is a first-in-first-out structure that temporarily stores cache hit
information and results returned by the Instruction Translation Lookaside Buffer
(ITLB), while monitoring cache lines written to SRAM by MSHR to update hit
information. Users can configure `nWayLookupSize` to adjust the depth of the Way
Lookup Queue, which also limits the maximum prefetch distance through
backpressure.

### MSHR manages fetch and prefetch requests

MSHR (Miss Status Holding Register) is a cache management structure used to
track and handle cache miss events. When requested data is not found in the
cache, MSHR records the miss status and manages subsequent data requests. In
{{processor_name}}, both fetch and prefetch requests are managed via MSHR, with
all MSHRs sharing a set of data registers to reduce area. Users can configure
the fetch quantity register `nFetchMshr` and prefetch quantity register
`nPrefetchMshr` to adjust the number of MSHR registers for fetching and
prefetching, respectively.

### ECC verification

{{processor_name}} supports ECC verification for the instruction cache. Users
can configure `DataCodeUnit` to adjust the verification unit size, measured in
bits. Each 64 bits of data corresponds to 1 parity bit.

### Branch Prediction Unit

Predictors within the Branch Prediction Unit (BPU) include the micro-FTB (uFTB),
Fetch Target Buffer (FTB), conditional branch predictor (TAGE-SC), indirect
branch predictor (ITTAGE), and return address predictor (RAS).

* uFTB is responsible for quickly predicting whether conditional branches will
  jump.
* The FTB is responsible for maintaining the starting address, ending address,
  branch instruction PC addresses, branch instruction types, and basic direction
  results of prediction blocks.
* TAGE-SC is the main predictor for conditional branch instructions.
* ITTAGE is responsible for predicting indirect jump instructions.
* RAS is responsible for predicting the jump address of return-type indirect
  jump instructions.

### Branch Target Buffer

To enhance the fetch efficiency of the instruction fetch unit during consecutive
jumps, {{processor_name}} uses the branch target buffer (uFTB) at the first
level of the branch prediction unit to provide bubble-free basic predictions for
the processor. Its main functions are as follows:

* Cache FTB entries to generate single-cycle prediction results. The uFTB
  maintains a small cache of FTB entries. Upon receiving the PC, it reads the
  corresponding FTB entry within one cycle and generates a first-stage
  prediction result from the FTB entry.
* Maintains a two-bit saturating counter to provide basic conditional branch
  outcomes. Each entry in the uFTB's FTB cache line maintains a corresponding
  two-bit saturating counter, with its direction prediction results reflected in
  the uFTB's prediction output.
* Update the FTB cache and two-bit saturation counters based on update requests.

Branch instructions predicted by uFTB include:

* BEQ, BNE, BLT, BLTU, BGE, BGEU, C.BEQZ, C.BNEZ.
* JAL, JALR, C.J, C.JAL, C.JR, C.JALR

### Conditional branch predictor

{{processor_name}} uses TAGE-SC as the main predictor for conditional branches.
TAGE-SC can be viewed as two functionally independent components: the prediction
part (TAGE) and the verification part (SC).

* The Tagged Geometric History Length Predictor (TAGE) leverages multiple
  prediction tables with varying history lengths to exploit extremely long
  branch history information. TAGE's function is to predict whether a branch
  instruction will be taken. It consists of a base prediction table and multiple
  history tables. Branch prediction is first attempted using the history tables;
  if no prediction is available, the base prediction table's result is used.
* SC (Statistical Corrector) is a statistical corrector. It references TAGE's
  prediction results and statistical biases to adjust the final prediction
  outcome.

In the {{processor_name}}, since each prediction block can have up to 2 branch
instructions, TAGE predicts up to 2 conditional branch instructions
simultaneously per prediction. When accessing various history tables of TAGE,
the starting address of the prediction block is used as the PC, and two
prediction results are fetched simultaneously, both based on the same global
history for prediction.

Branch instructions predicted by TAGE-SC include:

* BEQ, BNE, BLT, BLTU, BGE, BGEU, C.BEQZ, C.BNEZ.

### Fetch Target Buffer.

The Fetch Target Buffer (FTB) temporarily stores FTB entries, providing more
accurate branch instruction locations, types, target addresses, and other
critical branch prediction block information for advanced predictors such as
TAGE, ITTAGE, SC, and RAS. It also offers basic direction prediction for
always-taken branch instructions. The FTB module includes an FTBBank module
responsible for the actual storage of FTB entries. Within the module, a
multi-port SRAM is used as memory, configured with a 4-way set-associative
structure, totaling 2048 entries. Each entry can store up to 2 branches,
allowing a maximum of 4096 branches to be stored.

FTB predicts branch instructions including:

* BEQ, BNE, BLT, BLTU, BGE, BGEU, C.BEQZ, C.BNEZ.
* JAL, JALR, C.J, C.JAL, C.JR, C.JALR

### Indirect branch predictor

{{processor_name}} uses ITTAGE to predict the target addresses of indirect
branches. Each entry in ITTAGE adds a predicted jump address to the TAGE entry,
with the final output being the selected predicted jump address rather than the
jump direction. Since each FTB entry stores at most one indirect jump
instruction, the ITTAGE predictor can predict the target address of at most one
indirect jump instruction per cycle.

ITTAGE predicts branch instructions including:

* JALR: Source register is X1, excluding X5
* C.JALR: Excludes source register X5.
* C.JR: Source register is X1, excluding X5.

### Return address predictor

The Return Address Stack (RAS) is used for fast and accurate prediction of
return addresses at the end of function calls. When a prediction block is
predicted by the RAS's front-end predictor as a function call instruction, the
RAS pushes the address of the subsequent instruction onto the stack; when a
prediction block is predicted as a function return instruction, the RAS pops the
stack. To minimize data pollution caused by mispredictions during execution,
{{processor_name}} employs a persistent stack-based return address predictor.
The RAS is divided into two parts: the commit stack and the speculative stack.
The speculative stack utilizes the prediction results from the branch prediction
unit for predictions and pushes data into the commit stack based on feedback
from the backend.

* Function call instructions include: JAL, JALR, C.JALR.
* Function return instructions include: JALR, C.JR, C.JALR.

## L1 Data Cache.

### Overview

The main features of the L1 data cache are as follows:

* Data cache size is 64KB
* 8-way set-associative, with a cache line size of 64B.
* Virtual Index, Physical Tag (VIPT)
* Supports up to 3 parallel 64/128-bit read operations
* Supports up to one 512-bit read operation.
* Supports up to one 512-bit write operation.
* The write strategy adopts a write-back and write-allocate mode.
* Supports requesting missing data from L2 Cache and refilling.
* Supports processing Probe requests and writing back replaced data blocks.
* Supports handling atomic requests
* Supports Random, LRU, and PLRU replacement algorithms, with PLRU as the
  default
* Supports handling cache aliasing issues in coordination with L2 Cache.
* Supports SMS, Stride, and Stream hardware prefetching.

### L1 DCache coherence

The L1 data cache uses the TileLink protocol to maintain coherence among
multiple processor core data caches. This protocol requires privilege escalation
and de-escalation when responding to memory access operations and defines four
states for cache lines in the data cache, which are:

* Nothing: A node currently without a cached data copy has no read or write
  permissions.
* Trunk: A clean data copy with write permissions.
* Dirty: A writable dirty data copy
* Branch: A read-only data cache copy

### Exclusive access.

The L1 data cache supports LR/SC instructions and AMO instructions. Users can
employ LR/SC instructions to construct atomic locks and other synchronization
primitives for synchronization between different processes on the same core or
across different cores. Alternatively, AMO instructions can be used directly for
simple atomic operations.

MemBlock has two states: s_normal and s_atomics. When executing atomic
instructions, the state is set to s_atomics, and the execution flow enters the
atomic instruction processing unit for exclusive access. For LR/SC instruction
pairs, the L1 data cache registers a reservation set during LR instruction
execution and exclusively holds it for a certain period (default 64 clock
cycles). During this exclusive period, the DCache blocks accesses from other
cores to prevent deadlocks in multi-core scenarios with LR/SC instruction loops.
For AMO instructions, the L1 data cache checks for cache hits to determine if
the AMO request needs to enter the MissQueue. If the current AMO request misses
the cache, the request information is written to the MissQueue. If the AMO
request hits, the data result is read, the AMO instruction operation is
performed, and a response is returned to the atomic instruction processing unit.
Once MemBlock detects the atomic instruction processing unit has completed
execution, it reverts to s_normal to continue execution.

### Replacement and writeback

L1 data cache adopts write-back and write-allocate policies, with configurable
replacement strategies (Random, LRU, PLRU), defaulting to PLRU. Selected
replacement blocks are placed into the write-back queue, and a Release request
is issued to L2 Cache.

## L2 Cache

### Overview

The main features of the L2 cache are as follows:

* Cache size is 1MB
* 8-way set-associative, with a cache line size of 64B.
* The L2 Cache has a strict inclusion relationship with the L1 DCache and a
  non-strict inclusion relationship with the L1 ICache and PTW.
* Physical address indexing, physical address tagging (PIPT)
* Maximum access width of 64B per access
* The write strategy adopts a write-back and write-allocate mode.
* Adopts DRRIP replacement algorithm
* Supports instruction prefetching, TLB prefetching, and data prefetching
  mechanisms
* Supports Best-Offset Prefetch (BOP).
* Adopts a non-blocking pipeline structure

### Cache coherence.

The {{processor_name}} L2 cache employs a MESI-like protocol to maintain
coherence among multiple processor core data caches, including the following 5
cache states:

* Invalid: Indicates the cache line is not present in this data cache
* BRANCH: Indicates the cache line may reside in multiple data caches, with this
  copy having read permissions
* TRUNK Clean: Indicates that the cache line is only present in this core's data
  cache. The copy is clean and lacks read/write permissions, but the upstream
  data cache has both read and write permissions.
* TRUNK Dirty: Indicates the cache line resides only in this core's data cache,
  is a dirty block with no read/write permissions, while the upstream data cache
  has read and write permissions.
* TIP Clean: Indicates the cache line resides only in this core's data cache, is
  a clean block with read/write permissions, while upstream data either has read
  permissions or no permissions at all
* TIP Dirty: Indicates the cache line resides only in this core's data cache,
  the copy is dirty with read-write permissions, while upstream data either has
  read permissions or no permissions at all.

Other flags that may affect bus transactions:

* `clients`: Flags whether L1 DCache has a data copy, used to assist in
  determining if L1 DCache has a readable copy in BRANCH or TIP state.
* `alias`: Alias bit, used for hardware handling of L1 DCache (VIPT) aliasing
  issues, valid only when L1 DCache has a data copy, recording the portion of
  the virtual address index in L1 DCache that exceeds the physical page offset
  for the current physical address.
* `prefetch`: Indicates whether the data copy is a prefetch block.

### Organization structure

The {{processor_name}} L2 Cache adopts a sliced pipeline structure, defaulting
to 4 slices. Access addresses are distributed across 4 different slices based on
PA[7:6], allowing parallel processing of multiple accesses to improve
efficiency.

