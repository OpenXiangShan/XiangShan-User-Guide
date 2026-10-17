# Performance Monitoring and Top-down Analysis {#sec:xsai-pmu}

This chapter documents the performance monitoring capabilities XSAI adds on top
of the baseline HPM. For the general baseline mechanisms see the
_XiangShan Open-Source Processor User Guide_ (Performance Monitoring Unit
chapter).

## HPM capabilities at a glance

| Item | XSAI |
| --- | --- |
| Performance event counters | 29 (`mhpmcounter3` – `mhpmcounter31`) |
| Performance event selectors | 29 (`mhpmevent3` – `mhpmevent31`) |
| Events combinable per selector | up to 4 (event index + combination method + sampling privilege) |
| Total definable events | up to 2^10 |
| Overflow interrupt | `LCOFIP`, interrupt vector **13**, enabled and handled like an ordinary private interrupt |
| Extensions | the RISC-V privileged-spec HPM plus `sstc` and `sscofpmf` |

Counted quantities include clock cycles (`mcycle`), retired instructions
(`minstret`), the hardware timer (`time`) and the performance events configured
in each selector.

Why the overflow interrupt is vector 13: vector 12 is taken by `SGEI`, so `LCOFIP` takes 13.

The overflow interrupt is raised only by HPM counter overflow and has **no dedicated line** to the matrix unit; matrix performance events are folded into the backend event pool, however, so matrix activity can trigger it indirectly.


## Overall design

Performance events are defined **inside each submodule** and assembled by
`generatePerfEvent` into `io_perf`, which is exported to four main modules:
Frontend, Backend, MemBlock and CoupledL2.

Those four modules fetch the submodule event outputs through `get_perf` and each
instantiates `PFEvent` as a copy of the CSR's `mhpmevent`, feeding the selector
data together with the submodule event outputs into `HPerfMonitor`, which
computes the increment applied to the counters. The CSR gathers the increments
from the four top-level modules and accumulates them into `mhpmcounter3` –
`mhpmcounter31`.

CoupledL2 is the exception: its performance events go **straight into the CSR**,
where the instantiated `HPerfMonitor` processes them and accumulates the result
into `mhpmcounter27` – `mhpmcounter31`.

| Submodule | Responsibility |
| --- | --- |
| `HPerfMonitor` | Counter organisation module. Distributes the selector information to the corresponding `HPerfCounter`, copies all performance event counts into every `HPerfCounter`, and collects all counter outputs |
| `HPerfCounter` | Single counter module. Selects the events required by the selector information and combines them according to its counting mode |
| `PFEvent` | Copy of the `mhpmevent` register. Collects CSR writes and keeps `mhpmevent` in sync |

![HPM data flow](../figs/hpm-flow.svg "HPM data flow")

## Event pools and the `mhpmevent` mapping

`mhpmevent` registers are grouped into **event pools**, and each pool shares one
event index table:

| Event pool | Selector range |
| --- | --- |
| Frontend | `mhpmevent3` – `mhpmevent10` |
| Backend | `mhpmevent11` – `mhpmevent18` |
| Memory access | `mhpmevent19` – `mhpmevent26` |
| Cache | `mhpmevent27` – `mhpmevent31` |

XSAI **keeps the frontend and cache pools unchanged** and appends
matrix-related events only to the **backend and memory-access pools**. Matrix
events therefore have two numbering series: the backend-pool indices and the
memory-access-pool indices are independent of each other.

## Matrix-related events

### Backend event pool (`mhpmevent11` – `mhpmevent18`)

19 appended events covering matrix rename / scheduling and the CUTE task
lifecycle.

| Index | Event | Meaning |
| --- | --- | --- |
| 95 | `rename_stall_cycle_mx` | cycles rename stalls because the matrix free list cannot allocate |
| 96 | `me_freelist_1_4_valid` | matrix free list occupancy in the 1/4 bracket |
| 97 | `me_freelist_2_4_valid` | matrix free list occupancy in the 2/4 bracket |
| 98 | `me_freelist_3_4_valid` | matrix free list occupancy in the 3/4 bracket |
| 99 | `me_freelist_4_4_valid` | matrix free list occupancy in the 4/4 bracket |
| 100 | `IssueQueueMsetmtilexriwmfMrelease_full` | matrix integer issue queue full |
| 101 | `issueQueue_enq_fire_cnt` | matrix floating-point / arithmetic issue queue enqueues |
| 102 | `IssueQueueMsetmtilexrmfwmf_full` | matrix floating-point / move issue queue full |
| 103 | `IssueQueueMmaMarith_full` | matrix compute / arithmetic issue queue full |
| 104 | `IssueQueueMls_full` | matrix memory-access issue queue full |
| 105 | `amu_active_cycle` | cycles CUTE spends in the owned-work / active state |
| 106 | `amu_retire` | CUTE task retires |
| 107 | `amu_comp_done` | CUTE computation completions |
| 108 | `amu_release_done` | CUTE release completions |
| 109 | `amu_mte_active` | MTE busy cycles |
| 110 | `amu_mma_nonfp` | non-floating-point MMA completions |
| 111 | `amu_mma_fp16` | FP16 MMA completions |
| 112 | `amu_mma_bf16` | BF16 MMA completions |
| 113 | `amu_mma_tf32` | TF32 MMA completions |

### Memory-access event pool (`mhpmevent19` – `mhpmevent26`)

12 appended events covering the matrix move path and LocalMMU traffic.

| Index | Event | Meaning |
| --- | --- | --- |
| 145 | `amu_load_a_done` | A-matrix load completions |
| 146 | `amu_load_b_done` | B-matrix load completions |
| 147 | `amu_load_c_done` | C-matrix load completions |
| 148 | `amu_store_done` | C-matrix store completions |
| 149 | `amu_aml_active` | AML busy cycles |
| 150 | `amu_bml_active` | BML busy cycles |
| 151 | `amu_cml_load_active` | CML load busy cycles |
| 152 | `amu_cml_store_active` | CML store busy cycles |
| 153 | `amu_mem_rd_req` | read requests LocalMMU issues outwards |
| 154 | `amu_mem_wr_req` | write requests LocalMMU issues outwards |
| 155 | `amu_mem_rd_32B` | read traffic LocalMMU issues outwards, in 32 B units |
| 156 | `amu_mem_wr_32B` | write traffic LocalMMU issues outwards, in 32 B units |

The indices above are the values **inside each event pool**, written into the
`EVENT0` – `EVENT3` fields of an `mhpmevent`. Setting `EVENT0` of `mhpmevent19`
to 153, for instance, counts LocalMMU read requests.

### Example

Counting MTE busy cycles and LocalMMU read requests over one interval:

```asm
# backend pool: EVENT0 of mhpmevent11 = 109 (amu_mte_active)
# memory pool:  EVENT0 of mhpmevent19 = 153 (amu_mem_rd_req)
csrw mhpmevent11, <value encoding 109 in its field>
csrw mhpmevent19, <value encoding 153 in its field>
csrw mcountinhibit, 0        # let all counters count
...                          # run the workload
csrr t0, mhpmcounter11       # MTE busy cycles
csrr t1, mhpmcounter19       # LocalMMU read requests
```

## Top-down performance analysis

XSAI implements three levels of Top-down performance events, which let
you drill from a high-level classification down to the bottleneck. `IssueBW` is
the issue width; on Kunminghu it is currently **6**.

| Level 1 | Level 2 | Level 3 | Meaning |
| --- | --- | --- | --- |
| Retiring | — | — | instruction commit effects |
| FrontEnd Bound | — | — | frontend effects |
| — | Fetch Latency Bound | — | fetch latency effects |
| — | Fetch Bandwidth Bound | — | fetch bandwidth effects |
| Bad Speculation | — | — | misprediction effects |
| — | Branch Misspredict | — | effects of mispredicted branches |
| — | Machine Clears | — | effects of machine clears |
| BackEnd Bound | — | — | backend effects |
| — | Core Bound | — | core effects |
| — | Memory Bound | — | memory-access effects |
| — | — | L1 / L2 / L3 Bound | effects at each cache level |
| — | — | Mem Bound | external memory effects |
| — | — | Store Bound | store-instruction effects |

Key event mappings: `IF_FETCH_BUBBLE` maps to `Front_Bubble`,
`IF_FETCH_BUBBLE_EQ_MAX` to `Fetch_Latency_Bound`, and `INST_RETIRED` to
`rob_commitInstr`. To count the effect of frontend fetch latency, for example,
set `EVENT0` of `mhpmevent3` to 22 and read `mhpmcounter3` afterwards.

## CUTE Top-down attribution tree

For the matrix unit the question is not throughput itself but **where the stalls
land**. The convention is defined in
`tools/TMA-toolkit/presets/cute/default.yaml` and the tree has four levels.

### L0: baseline

| Counter | Meaning |
| --- | --- |
| `CUTE_L0_TC_HeadValidSlot` | slots in which the head task is valid |
| `CUTE_L0_TC_IssueFire` | slots that actually issued |
| `CUTE_L0_TC_Stall` | derived: `HeadValidSlot - IssueFire` |

L0 defines the gap between "opportunities to advance" and "actual advances",
that is, total stall.

### L1: main cause (mutually exclusive classes)

The three **mutually exclusive** buckets `CUTE_L1_TC_Stall_Memory`,
`CUTE_L1_TC_Stall_Compute` and `CUTE_L1_TC_Stall_Dependency` answer whether the
unit is mainly blocked on memory, compute or dependency. The accompanying gate
counters are `CUTE_L1_TC_Need_{AML,BML,CML,ADC,BDC,CDC}` and
`CUTE_L1_TC_Block_{AML,BML,CML,ADC,BDC,CDC}`.

### L2: Dependency subclasses

| Class | Counters |
| --- | --- |
| Dependency | `CUTE_L2_SB_Block_Dep_SrcNotReady`, `_DestBusy`, `_DestHasConsumers`, `_CMLStoreConsumer` |
| Resource | `CUTE_L2_SB_Block_Res_AMLBusy`, `_BMLBusy`, `_CMLLoadBusy`, `_CMLStoreBusy`, `_ComputeBusy` |

When L1 identifies Dependency as the main cause, L2 separates a **data
dependency** from a **busy functional unit**.

### L3: source

`SrcNotReady` and `DestBusy` are each split into four sources:
`CUTE_L3_SB_Dep_{SrcNotReady,DestBusy}_By_{AML,BML,CML,Compute}`, answering which
producer side the dependency comes from.

### Bucket types and consistency checks

Three kinds of bucket must be distinguished before reading a report, otherwise a
sub-item larger than its parent looks like a bug:

* **Mutually exclusive buckets**: one stall cycle lands in exactly one bucket, so
  the total closes (the L1 main classes);
* **Non-exclusive buckets**: one cycle may match several conditions, which is
  useful for observing signals, and the sum may exceed the parent (inside the
  Compute domain, for instance, `ADC/BDC/CDC` can be hit simultaneously);
* **Residual buckets**: `parent − sum of explicit children`, carrying the part
  that has not been drilled into yet, such as `CUTE_L2_Memory_Remain`.

`consistency.json` automatically checks mathematical and semantic relations
(such as `L1_sum_eq_l0_stall`, `l2_sum_eq_l1_dependency` and `block <= need`
gates). A **failing** check means the convention does not close or the
classifications overlap, in which case fix the convention before reading the
conclusions.

### Derived items

The default convention defines the aggregates `CUTE_L1_TC_Stall_Sum`,
`CUTE_L2_Memory_Remain`, `CUTE_L2_SB_Block_Sum` and
`CUTE_L3_SB_Dep_*_By_Memory`.

## Using TMA-toolkit

The observation convention lives in a YAML preset rather than in the RTL, so a
new analysis need should be met by adding or adjusting a preset instead of
hand-piling `XSPerfAccumulate` into the RTL.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
make -C tools/TMA-toolkit sync                       # prepare the dependency environment
make -C tools/TMA-toolkit list-presets               # list available presets

make -C tools/TMA-toolkit apply-dry PRESET=cute/default   # preview anchors, change nothing
make -C tools/TMA-toolkit apply     PRESET=cute/default   # instrument

make run-emu PAYLOAD=<payload>                       # run the simulation

make -C tools/TMA-toolkit report        PRESET=cute/default LOG=log/emu-error.log
make -C tools/TMA-toolkit report-strict PRESET=cute/default LOG=log/emu-error.log
```

`report` is fault-tolerant and always returns 0, which suits day-to-day use;
`report-strict` returns non-zero when a consistency check fails, which suits
gates. The artefacts are `values.csv`, `combined.png`, `report.md` and
`consistency.json`.

The common presets are `cute/default` (the mutually exclusive L1 convention) and
`cute/legacy_v1` (the historical non-exclusive convention, for version
comparison).

### Reading order

Always the same three steps: read the L1 shares to find the main cause, read the
next level under that cause to locate the subclass, then read `consistency.json`
to confirm the convention closes.

## Structured tracing

* Module-level event printing can be enabled through a compile-time debug
  parameter (`CuteDebugParams`); there is no unified structured tracing format
  yet;
* How tracing relates to waveforms and HPM: waveforms give timing detail, HPM
  gives statistical conventions, and `ChiselDB`-style tracing gives intermediate
  state.

## Recommended analysis flow

1. Collect a kernel-level performance table (cycles, IPC, effective bandwidth,
   arithmetic intensity, fraction of peak);
2. Use HPM or the Top-down attribution tree to classify the bottleneck (memory
   access / compute / scheduling / dependency);
3. Use structured tracing or waveforms to localise the specific module and
   moment.
