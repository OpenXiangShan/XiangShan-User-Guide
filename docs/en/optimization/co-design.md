# Software and Hardware Co-design {#sec:co-design}

This chapter is for deciding whether an optimisation belongs in software or in
hardware, for raising a hardware requirement, or for assessing what a hardware
change gains upwards.

## Check software first, then hardware

The matrix unit's peak throughput is high, but a model usually runs far below it.
Two utilisation figures have to be kept apart:

* **Matrix unit utilisation**: counts only the stretch in which the matrix unit is
  actually computing (the `ame_tile_call` function); it reflects what the hardware
  itself can reach.
* **Operator utilisation**: the whole span from operator entry to return, including
  data reshaping, quantisation and dequantisation; this is what the user actually
  gets.

The gap between them is usually almost entirely software processing: quantisation,
data packing, result scaling, handling of matrix edges that do not fill a tile, and
waiting for data to arrive. So when utilisation is low, find where the software is
spending time before discussing what the hardware should change.

## Three reasons utilisation can be low

```text
low matrix unit utilisation
   ├── compute: is the compute unit already saturated?
   ├── memory: does the data arrive in time?
   └── capacity: does the data fit in the on-chip cache?
```

Work through them one by one; a single utilisation number does not settle it.

### Memory bottlenecks: bandwidth-limited and latency-limited

| Type | Symptom | Software optimisation | What hardware can offer |
| --- | --- | --- | --- |
| Bandwidth-limited | too much data to move in total | reduce the volume: operator fusion, tiling, quantisation | higher bandwidth (HBL2), larger on-chip cache |
| Latency-limited | many accesses, or accesses depending on each other | overlap access with compute: prefetch, double buffering, software pipelining | more MSHRs, hardware prefetch, asynchronous paths |

Once the data volume exceeds the bandwidth limit, overlapping access with compute
does not help; only reducing the volume does. Before raising a hardware
requirement, establish which of the two you are facing.

## What the hardware provides

| Hardware feature | How software uses it | Chapter |
| --- | --- | --- |
| Native tile shape (M128 × N128 × K64) | read the actual value at run time and generate kernels from it | [Data Registers](../isa/registers.md#sec:xsai-registers) |
| Asynchronous execution plus synchronization registers | declare dependencies with `mrelease` / `macquire`, covering every return path of the function | [Instruction Set Extensions](../isa/instruction-set.md#sec:xsai-instruction-set) |
| 31 matrix-related HPM events | classify the bottleneck | [Performance Monitoring](../hardware/pmu.md#sec:xsai-pmu) |
| CUTE Top-down analysis (four levels) | break stall cycles down level by level to memory, compute, dependency and the concrete source | [Performance Monitoring](../hardware/pmu.md#sec:xsai-pmu) |
| HBL2 high-bandwidth read path | dedicated to matrix access, 512 B/cycle peak | [Memory Subsystem and HBL2](../hardware/memory.md#sec:xsai-memory) |
| Configurable clock domains | the matrix unit runs at the core clock or asynchronously, which changes the cost of synchronisation | [Microarchitecture Delta](../hardware/microarchitecture.md#sec:xsai-microarchitecture) |

## The analysis flow

```text
1. estimate the theoretical minimum from peak throughput (no hardware needed)
2. measure prefill and decode separately
3. look at each operator's share of total model time to judge whether it is worth optimising
4. break the operator into stages and decide whether the bottleneck is software or hardware
5. read the HPM counters to classify the bottleneck
6. use Top-down analysis to locate the concrete source
7. propose the optimisation and verify the gain
```

Steps 1–4 happen in software, steps 5–6 use hardware counters, and step 7 returns to
software. Enter step 5 only after the software processing has been optimised as far
as it goes. The method for each step is in
[Performance Analysis and Tuning](perf.md#sec:sw-perf).

### When to raise a hardware requirement

| Symptom | Conclusion |
| --- | --- |
| data reshaping, scaling and other software stages take a large share | optimise software; the hardware needs no change |
| matrix unit utilisation is high while operator utilisation is low | the problem is software processing |
| software processing is optimised and `ame_tile_call` still dominates | hardware change is worth considering |
| bandwidth-limited, and operator fusion and tiling are already used fully | raise a bandwidth or cache capacity requirement |
| latency-limited | do software pipelining first; hardware can evaluate prefetch or more MSHRs |
| the on-chip cache is too small to open larger tiles | raise a cache capacity requirement, or change the algorithm to reduce the data volume |

## Classes of optimisation

| Class | Principle | Typical means |
| --- | --- | --- |
| Raise compute density | more compute per memory access | tiling, register blocking, operator fusion |
| Improve memory access | use the bandwidth and cache fully | data reshaping, padding and alignment, prefetch, double buffering |
| Switch to an equivalent algorithm | less compute or less traffic | quantisation, sparsity, recomputation |

**Quantisation usually pays the most**: smaller data reduces cache footprint and
traffic, and the low-precision peak is higher. It does change the computed result,
though, so the accuracy has to be re-verified on a real model; see
[Performance Analysis Path](../start/path-perf.md#sec:path-perf) for the
requirements.
