# Performance Analysis Path {#sec:path-perf}

This chapter answers three questions: why something is slow, what to optimise, and
how much the optimisation gains. Prerequisites: the environment is up and you can
produce a payload log (see [Getting Started](quickstart.md#sec:get-started)).

The outcome is a performance report with an explicit basis, plus one validated
optimisation. The methodology, the full counter correspondence table and the
classification of optimisations are in
[Performance Analysis and Tuning](../optimization/perf.md#sec:sw-perf); this
chapter covers the order of diagnosis.

## The diagnostic order

```text
static ceiling → per stage → graph-level share → inside the operator → instruction/sync/RTL
```

The order is fixed; do not skip steps. Low utilisation is only a symptom, and
software-side causes must be ruled out before jumping into the RTL.

### Step 1: compute the static ceiling

This needs no hardware and tells you whether the work is worth doing. The
estimation method and its limits are in
[Performance Analysis and Tuning](../optimization/perf.md#sec:sw-perf). Group by
compute domain, since different precisions run against different peaks.

What comes out is a theoretical minimum: that compute domain at peak throughput,
with no memory or scheduling overhead. When several domains run serially the
minima add up, and when they share resources the real time can be longer. **It is
not an end-to-end guarantee.**

### Step 2: split by stage

`prefill` and `decode` are two different bottlenecks and must be measured
separately, since their hotspot rankings usually differ:

| | prefill | decode |
| --- | --- | --- |
| Character | compute intensive | memory intensive |
| GEMM | usually compute-bound | usually memory-bound |
| attention | bottleneck in the QK^T computation | bottleneck in KV cache load bandwidth |

Compare within one stage, or the numbers are not comparable.

### Step 3: look at the graph-level share

Compare the matrix unit's cycle count against the graph-level total to confirm it
is worth drilling into.

### Step 4: break down the stages inside the operator

This is where results usually come from. Break the matrix unit's cycles down by
stage; the typical software-side stages are:

```text
prepare_cache      activation quantisation / cache preparation
pack_a, pack_b     operand packing
ame_tile_call      the stretch that actually drives the matrix unit
scale              the quantisation scale epilogue
store              writing results back
```

**What matters is how much `ame_tile_call` takes.** The larger the other stages,
the more the bottleneck sits in software. The usual mistake here is reading the
overall utilisation figure and concluding the hardware is inadequate: that figure
includes every software stage, whereas hardware capability is what the
`ame_tile_call` stretch shows.

Always state which stretch a utilisation figure covers. Only the `ame_tile_call`
stretch reflects the hardware ceiling; the figure from operator entry to return is
what the user actually gets. Reporting the first as the second books
software-stage loss as insufficient hardware.

### Step 5: enter the RTL after the software side has converged

Before touching the RTL, rule out quantisation, layout movement, the scale
epilogue, handling of matrix edges that do not fill a tile, and waiting for data
to arrive.

## Locating the bottleneck

XSAI appends 31 matrix-related events to the baseline (19 in the backend pool, 12
in the memory-access pool). The event list, the `mhpmevent` mapping, the counter
counter correspondence table, TMA-toolkit usage and how to read the Top-down levels are in
[Performance Monitor](../hardware/pmu.md#sec:xsai-pmu) and
[Performance Analysis and Tuning](../optimization/perf.md#sec:sw-perf).

Collecting everything in one pass is impossible. Always take the four skeleton
groups — bandwidth utilisation, cache hit rates at each level, main execution unit
utilisation, and the stall reason breakdown — then add events targeted at the
hotspot type, with a coarse first pass and a finer second pass.

## Next

* [Performance Analysis and Tuning](../optimization/perf.md#sec:sw-perf): optimisation classes, measurement requirements and tuning cases
* [Performance Monitor](../hardware/pmu.md#sec:xsai-pmu): the 31 matrix events, the Top-down levels and TMA-toolkit
* [Software and Hardware Co-design](../optimization/co-design.md#sec:co-design): feeding performance information back into hardware design
