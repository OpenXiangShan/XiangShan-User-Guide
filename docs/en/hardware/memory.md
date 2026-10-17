# Memory Subsystem and HBL2 {#sec:xsai-memory}

This chapter covers the high-bandwidth L2 (HBL2) and the matrix memory access
path XSAI added over Kunminghu V2R2; the general memory model is described in the
baseline manual.

## What HBL2 is for

HBL2 upgrades Kunminghu's `CoupledL2` while keeping all of its original
functionality, with little impact on general-purpose computing. The motivation is
the memory bandwidth demanded by large-model inference. The native `CoupledL2`
has three structural limitations:

1. structural blockage created by the cache microarchitecture;
2. redundant overhead from maintaining cache coherence;
3. traditional replacement / prefetch algorithms failing in large-model
   scenarios.

## Bandwidth and capacity

Matrix memory access takes a dedicated read path, with a peak read bandwidth of
**512 B/cycle** — about 1.25 TB/s at 2.5 GHz. That figure is for the hit case:
replacement and prefetch are not yet improved, so effective bandwidth with misses
is lower.

Both matrix configurations have the same L2 capacity, 2 MiB.

## Matrix memory access interface

HBL2 adds three flag fields and one return path for matrix accesses:

* request-side flags: `MatrixKey`, `AmeChannelKey` and `AmeIndexKey`, with the
  corresponding matrix request flags added inside the L2;
* return-side interface: `matrixDataOut`, carrying matrix read data back.

The two matrix request types are handled as follows:

| Request | Handling |
| --- | --- |
| Matrix Get | handled like an Acquire; on a miss it acquires downwards for B permission |
| Matrix Put | the classic coherence scheme: on a hit it writes directly; on a miss it enters the MSHR and acquires downwards for T permission |

Matrix data is currently handled coherently.

Responses to matrix requests and to ordinary requests were once accounted for
separately, which let the two drift out of step; they are now handled uniformly.
The detailed timing of that accounting is outside the scope of this manual.

## Matrix memory access path

Matrix accesses are driven by three move paths, all reaching the storage
hierarchy through the `LocalMMU` and `CUTE2TL`:

| Path | Responsibility |
| --- | --- |
| AML (AMemoryLoader) | A-matrix moves |
| BML (BMemoryLoader) | B-matrix moves |
| CML (CMemoryLoader) | C-matrix load and store |

![Matrix memory access path](../figs/memory-path.svg "Matrix memory access path")

The `LocalMMU` is the only externally visible data-side interface and reaches the
LLC and the memory hierarchy uniformly. The matrix unit exposes just two
top-level interfaces: `io.ctrl2top` (control side, to `TaskController`) and
`io.mmu2llc` (data side, to `LocalMMU`).

### Key parameters

| Parameter | Definition | Constraint |
| --- | --- | --- |
| `outsideDataWidth` | LocalMMU data return width | a power of two, commonly 512 bit |
| `outsideDataWidthByte` | `outsideDataWidth / 8` | must be less than or equal to `Tensor_K` |
| `ABMatrixRegNBanks` | AB MatrixReg bank count | equals `Matrix_MN` |
| `ABMatrixRegEntryByteSize` | single-bank entry width | `OOORouter` requires 32 B |
| `Trans_Load_Size` | `outsideDataWidthByte / ABMatrixRegNBanks`, also the triangle pipeline lane count | only 8 or 16, and a power of two |
| `ReduceGroupSize` | `Tensor_K / ReduceWidthByte` | the parameter layer requires 2 |
| `MMUAddrWidth` | memory request address width | defaults to 64 |

### Two sub-paths

| Submodule | Responsibility |
| --- | --- |
| `TransAlignPipe` | non-uniform alignment pipeline for the transpose path; one instance per bank |
| `OOORouter` | out-of-order router and write reduction tree; requires a 32 B single-bank entry |

The transpose path bypasses the non-transpose path's fill table (whose depth is
`AMemoryLoaderReadFromMemoryFIFODepth`).

## The operand pool

### The pool location is resolved at runtime, not a fixed address

The matrix operand buffer must reside in a **physically contiguous memory pool**,
but its base address is **not the hardcoded `0x100000000`**. `xsai_alloc.c`
resolves it in the following order, **first hit wins**:

| Order | Source | Variable / path |
| ---: | --- | --- |
| 1 | environment | `XSAI_AME_RESERVED_BASE` / `XSAI_AME_RESERVED_SIZE` (hex or decimal) |
| 2 | device tree | `/proc/device-tree/reserved-memory/direct_map@<addr>/reg` |
| 3 | compile-time fallback | `RESERVED_PHYS_BASE_ADDR` (legacy path, **logged loudly when hit**) |
| 4 | none of the above | a hard failure with an actionable message |

### The two standard memory layouts

| Image | Total RAM | Pool size | Pool base |
| --- | --- | --- | --- |
| appliance | 8 GB | 6 GB | `0x1_0000_0000` |
| ruyi / mega | 16 GB | 4 GB | `0x3_8000_0000` |

**Why not a compile-time constant alone**: one binary must serve both layouts. Pin
it to the wrong one and **ordinary kernel RAM gets mapped as the AMU pool, so the
first AME store faults** — an OpenSBI trap with the machine dead, a failure that
has been reproduced.

The CMake default follows the appliance layout (base `0x100000000`, pool **6 GiB**,
matching `XSAI_DIRECT_MAP_MEM_SIZE` in `mk/memory.mk` and the `direct_map` node in
the device tree). Building the mega variant requires passing explicitly:

```bash
cmake ... -DXSAI_RESERVED_PHYS_BASE_ADDR=0x380000000ULL \
          -DXSAI_RESERVED_MEMORY_SIZE='(4096L*1024L*1024L)'
```

### Allocation mode

The allocation mode must be decided by the external environment and **must not be
compiled into the artifact**, or the same binary stops working when moved:

| Variable | Value | Meaning |
| --- | --- | --- |
| `XSAI_ALLOC_MODE` | `malloc` | aligned malloc/free, no pool |
| | `anon` | anonymous mmap pool even when `RESERVED_PHYS_BASE_ADDR` is defined (host testing only) |
| `XSAI_ALLOC_POOL_SIZE_MB` | number | overrides the anonymous pool size (host testing) |

Anonymous mode is for QEMU user mode or host testing only. Carried onto the board
unconditionally it shows up as `SIGABRT` (`rc=134`), or as a wrong result under the
anonymous pool that the in-process check catches (`rc=255`).

### Why addressing depends on the pool being contiguous

Only when the pool is genuinely backed by physically contiguous memory (huge pages
or `RESERVED_PHYS_BASE_ADDR`) can the AMU use "single TLB base plus physical
offset" addressing:

```text
PA = TLB(pool_base) + (ptr - pool_base)
```

That is what makes the **no per-row TLB re-walk** property possible, and it is why
row addresses are computed as `PA_base + row × stride`: a non-contiguous buffer is
**silently misread** once the row count is large (63 rows, or 127 and above) rather
than reporting an error.

## Visibility and memory ordering

* Ordering constraints between matrix accesses and other memory accesses are
  given by the synchronization instructions and CSR semantics;
* Use `macquire` for matrix results becoming visible to vector / scalar code, and
  `mfence` for non-matrix accesses becoming visible to the matrix engine; the two
  directions differ;
* `mrelease` / `macquire` must cover all exit branches; otherwise intermittent
  errors occur that are hard to reproduce reliably;
* The behaviour is undefined when synchronization is missing.

