# Performance Analysis and Tuning {#sec:sw-perf}

This chapter covers three things: measuring performance numbers correctly, classifying the bottleneck, and the optimisation directions available. The diagnostic order and the layer-by-layer breakdown are in [Performance Analysis Path](../start/path-perf.md#sec:path-perf); this chapter gives the method and the rules.

## Establish the basis first

Performance numbers in a report must state their basis explicitly; otherwise the
numbers are not comparable:

| Basis | Meaning |
| --- | --- |
| Cycles per call | Cycles for one operator call (including synchronization overhead) |
| Cycles per MAC | Divided by the MAC count, for comparing different shapes |
| End-to-end throughput | End-to-end token/s or fps |

The theoretical lower bound is estimated uniformly as `1 MAC = 2 operations` and
`theoretical time = MAC × 2 / peak TOPS`. That time assumes the compute domain
owns peak throughput with no utilisation discount and no memory or scheduling
overhead, so it is a lower bound and **not** an end-to-end guarantee. Domains
executed serially have their bounds added; domains that can run in parallel may
have a shorter critical path; domains sharing on-chip storage, DMA, unpacking or
scheduling resources may end up slower than the sum.

Vector work, softmax, RoPE, masking, residuals and data movement are not suited
to estimating with TOPS and should be listed separately by scale.

## Measurement requirements

* Cycles, host wall-clock frequency and end-to-end tokens/s are three different
  quantities: record them separately.
* Separate prefill from decode, and cold start from steady state — they rank
  hotspots differently.
* Disable progress / debug logging for performance runs; use at least one warm-up
  and three measurements, and take the median.
* Any change to quantisation granularity, accumulation order or an approximation
  requires operator-level error checks and a real-model accuracy regression.

## Benchmark

Load analysis groups by **compute domain** rather than listing every operator,
because different precisions run against different peak throughputs:

| Compute domain | Typical operators | Peak basis |
| --- | --- | --- |
| Low precision (INT8 × INT2 and similar) | quantised LLM attention / MLP projection | INT8 peak (TOPS) |
| BF16 matrix | patch conv, QK^T / AV, projector, action head | BF16 peak (TOPS) |

Analysing a load on that basis gives four columns per compute domain:

| Compute domain | MAC | Equivalent operations | Peak | Undiscounted theoretical time |
| --- | --- | --- | --- | --- |
| low precision | count it | `MAC × 2` | that precision's peak TOPS | `operations / peak` |
| BF16 matrix | count it | `MAC × 2` | that precision's peak TOPS | `operations / peak` |

The value of this is being able to judge, **before running anything**, whether a
load is worth putting on the matrix unit, which compute domain the bottleneck
falls in, and what the theoretical ceiling is. The low-precision share of MACs is
worth tracking on its own: it determines how much of the work can run at the
low-precision peak.

## Profiling tools

### From counter patterns to bottleneck class to candidate strategies

Diagnosis is a two-stage mapping:

```text
measured counter combination ──compare against the table──▶ bottleneck class ──rule lookup──▶ candidate optimisations (ranked by expected gain)
```

The first stage is **grouping by counter pattern**: predefine a few counter signatures for
each bottleneck class and match the measurement against it. A minimal usable
minimal table:

| Bottleneck class | Counter signature | Root-cause direction |
| --- | --- | --- |
| Memory bound (external) | high memory bandwidth utilisation, low main execution unit utilisation, memory stalls dominate | cut traffic: fusion / tiling / quantisation / prefetch |
| Memory bound (on-chip) | high cache hit rate but many bank conflicts, on-chip bandwidth saturated | change access pattern: padding, reordering, vectorised loads |
| Compute bound (pipe not full) | moderate pipe utilisation, tiles too small, launch overhead dominates | larger tiles, fusion to cut kernel count, raise occupancy |
| Compute bound (pipe full) | pipe close to saturation | at the precision ceiling; only raising the roof helps: quantisation, lower-precision instructions |
| Special function unit bound | SFU (exp, divide) saturated while the pipe idles | offload the SFU, replace with low-precision fits, rewrite the algorithm |
| Exposed latency | many pipeline bubbles, stalls dominated by long-latency dependencies, low occupancy | double buffering, software pipelining, more parallelism |
| Dequantisation overhead | high dequant instruction share, pipe crowded out by scalar / integer instructions | pre-decompress weights, fuse dequant into the GEMM epilogue |
| Load imbalance | large per-core time variance, long-tail kernels | balanced routing, grouped GEMM, dynamic scheduling |

The second stage is a **rule lookup**: each bottleneck class carries a set of
candidate strategies with applicability conditions and a ranking by expected
gain. That library is an asset worth accumulating over time.

**Choosing the top-k counter events**: you cannot collect everything in one pass
(many counters are mutually exclusive and require replay rounds).

1. Cover the key nodes of the causal chain: bandwidth utilisation, cache hit
   rates at each level, main execution unit utilisation, and the stall reason
   breakdown. These four groups are the skeleton and must always be collected;
2. Add events targeted at the hotspot type: dequant instruction counts for
   quantised GEMM, KV load traffic and SFU utilisation for attention, per-kernel
   time variance for MoE;
3. Converge iteratively: a first coarse pass identifies the class, a second pass
   drills into the root-cause direction.

For the counters available on XSAI see
[Performance Monitor](../hardware/pmu.md#sec:xsai-pmu); the CUTE L0–L3 attribution tree
and `TMA-toolkit` usage are documented in the same chapter.

### The split to make first

`prefill` and `decode` are **two different bottlenecks**, and the same operator
needs different prescriptions in each:

| | prefill | decode |
| --- | --- | --- |
| Character | compute intensive, high arithmetic intensity | memory intensive, low arithmetic intensity (weights / KV read in full each step) |
| GEMM | usually compute-bound | usually memory-bound (unless a large continuous batch) |
| attention | bottleneck in the QK^T computation | bottleneck in KV cache load bandwidth |
| Main prescriptions | operator fusion, tile / pipeline tuning, higher pipe utilisation | KV quantisation and compression, GQA / MLA, prefetching, larger effective batch, speculative decoding |

Hotspot ranking must therefore be done **per stage**: prefill and decode usually
rank hotspots differently, and optimisation effort should be allocated
separately.

## The optimisation landscape

Every optimisation falls into one of three classes:

1. **Raise compute density**: support more computation per memory access;
2. **Improve memory access**: use the available bandwidth and cache fully;
3. **Algorithmically equivalent replacement**: change the complexity or the IO
   pattern itself.

### The resource view

Orthogonal to the above, every operator can be examined along **compute,
communication and storage**, and this view directly orders the diagnosis.

* **Compute**: how much work is done per unit time. Low execution unit
  utilisation does **not** mean the bottleneck is compute — communication falling
  behind or storage not fitting both leave the execution unit idle waiting for
  work. Low utilisation is the terminal symptom, and all three dimensions can
  present it, so follow the causal chain to the root cause.
* **Communication**: the cost of moving data between storage levels. There are
  two kinds, with different prescriptions: **bandwidth-limited** (too much total
  traffic; cut it with fusion, tiling, quantisation) and **latency-limited** (many
  transfers or long dependency chains; hide it with prefetching, double
  buffering, software pipelining). When traffic exceeds the physical bandwidth
  limit, hiding does not help and only cutting works. Communication is a chain of
  levels, and every communication optimisation can be phrased as pushing traffic
  towards a level closer to the execution unit.
* **Storage**: capacity decides whether something is possible at all. Typical
  questions: can the tile be large enough, how many double buffers fit, can the
  KV cache hold the context and batch, can the weights stay resident. Counter
  signals: register spills, on-chip cache occupancy, occupancy capped by
  resources, KV cache swapping.

The three constrain each other and can relieve each other: spending more on-chip
storage on caching or prefetching relieves communication pressure (space for
time); recomputing instead of storing intermediate results relieves capacity
pressure (time for space); quantisation is the single most cost-effective
optimisation precisely because shrinking the data benefits storage,
communication and compute at once.

### Loop-level optimisations

Hotspot operators are nested loops, so loop transformations are the most basic
and highest-leverage class of optimisation:

| Optimisation | Principle | Counter signals | Main trade-off |
| --- | --- | --- | --- |
| Tiling | cut the loop into tiles so the working set fits on-chip, maximising reuse | low cache hit rate, high external memory traffic | tiles too large spill on-chip storage and cut occupancy; too small lowers efficiency and raises launch overhead |
| Reordering | change the nesting so the inner loop walks contiguous memory and the outer reuses loaded data | low hit rate, many uncoalesced accesses | coupled with tiling; the order changes the optimal tile shape |
| Fusion | merge loops of adjacent operators so one load serves several computations, avoiding write-back and re-read of intermediates | many kernels, high intermediate tensor traffic, launch overhead | more register / on-chip pressure can lower occupancy; granularity constrained by producer-consumer shapes |
| Splitting | split one loop into several, mapped to different resources or pipeline stages | uneven resource use inside a kernel, long dependency chains | introduces synchronisation and intermediate storage |

Operator fusion is mostly the fusion of two loops and directly raises the
compute-to-memory ratio. Whether it pays is a question of the intermediate tensor
traffic saved against the added on-chip resource pressure.

## Tuning case studies

### Dequantisation overhead in quantised GEMM

Low-precision-weight GEMM is often stopped by dequantisation overhead before it
becomes compute bound: dequant instructions crowd out the execution pipe. The
prescription is to pre-decompress the weights, or to fuse dequant into the GEMM
epilogue so the pipe is not occupied by scalar / integer instructions. The
diagnostic is the gap between the dequant instruction share and the actual pipe
utilisation.

### Poor M utilisation caused by hook-point shapes

A framework does not necessarily hand over a shape that suits the
native tile geometry. When M utilisation is clearly poor (a convolution hook
point supplying only 8 pixels at a time, for instance), leaving the work on RVV is
the better deal; the workload threshold (see
[Operator Libraries and Inference Frameworks](../software/frameworks.md#sec:sw-frameworks))
hands such tasks back to the framework's own kernels.

### Placement of synchronization points

When the matrix unit and the core run at different frequencies, the placement of
synchronization points largely determines the end-to-end gain (see
[Microarchitecture Delta](../hardware/microarchitecture.md#sec:xsai-microarchitecture)).
`mrelease` / `macquire` must both cover all exit branches and avoid synchronising
so often inside a loop that the benefit of asynchronous execution is cancelled.

## Common bottlenecks

* **Launch overhead dominates small operators**: operator fusion is needed, or a
  workload threshold hands tasks not worth the launch back to RVV;
* **Insufficient memory bandwidth utilisation**: the effective bandwidth of some
  operators is below peak;
* **Tile partitioning and buffering strategy**: when M utilisation is poor (the
  convolution case supplies only 8 pixels at a time) the task should fall
  back to the small core;
* **Clock configuration**: when the matrix unit and the core run at different
  frequencies, the placement of synchronization points largely determines the
  end-to-end gain.
