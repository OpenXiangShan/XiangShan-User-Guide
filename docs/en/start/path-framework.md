# Framework Adaptation Path {#sec:path-framework}

This chapter is for connecting the matrix unit into an inference framework or
operator library (MNN / NCNN / ggml / in-house). Prerequisites: the environment is
up (see [Getting Started](quickstart.md#sec:get-started)) and you have read
[Instruction Set Extensions](../isa/instruction-set.md#sec:xsai-instruction-set)
for the ZAMES programming model.

Work through the steps below in order; each step's output is the next step's
input. The specifications and constraints live in
[Operator Libraries and Inference Frameworks](../software/frameworks.md#sec:sw-frameworks);
this chapter covers the order and the wiring.

## 1. Read the hardware tile shape

The native tile shape of the matrix unit is fixed by the hardware configuration,
native shape is M128 × N128 × K64. Read the actual value through the CSR probe and
generate kernels from what you read; do not hard-code it.

A wrong shape does not raise an error, it just computes wrong results: a whole
layer failing on the board while the same payload is fully correct in QEMU is
usually this case. See [Data Registers](../isa/registers.md#sec:xsai-registers)
for how to read it.

> Design documents write the shape in M-K-N order as `128x64x128`; that is the same
> shape as the M-N-K order used here.

## 2. Find the framework's native replacement point

Priority, highest first:

| Priority | Replacement point | Example |
| --- | --- | --- |
| 1 | a function table where swapping the implementation swaps the kernel | MNN's core functions table |
| 2 | the arch-layer layer implementation | NCNN's registry |
| 3 | replacing at each call site | last resort; each variant must be patched separately |

The exact locations in the three frameworks are in
[Framework replacement points](../software/frameworks.md#sec:sw-frameworks).

## 3. Keep the matrix instructions in one translation unit

Put all matrix instructions in a single translation unit and have every other file
call it through a header. The matrix constraints (pinning registers, covering
synchronization) then have to be upheld in exactly one place, and you avoid
adjusting compiler options file by file.

Matrix instructions need the compiler to enable the corresponding extensions. The
actual value is:

```text
-march=rv64gcv_zames_zmasync_zvl128b
```

MNN / NCNN / ggml are all CMake projects. The practice is to apply the flag only to
the one source file that holds the matrix instructions:

```cmake
# MNN: source/backend/cpu/CMakeLists.txt
set_source_files_properties(${CMAKE_CURRENT_LIST_DIR}/compute/ame_xsa.c
    PROPERTIES COMPILE_OPTIONS "-march=rv64gcv_zames_zmasync_zvl128b")
```

The glue file that allocates the operand pool additionally receives the pool's
compile-time parameters:

```cmake
set(XSAI_RESERVED_PHYS_BASE_ADDR "0x100000000ULL" CACHE STRING "AME pool compile-time physical base")
set(XSAI_RESERVED_MEMORY_SIZE   "(6L*1024L*1024L*1024L)" CACHE STRING "AME pool compile-time size")  # 6 GiB, matching mk/memory.mk and the DTB
set_source_files_properties(${CMAKE_CURRENT_LIST_DIR}/ame/xsai_alloc.c
    PROPERTIES COMPILE_OPTIONS
    "-DRESERVED_PHYS_BASE_ADDR=${XSAI_RESERVED_PHYS_BASE_ADDR};-DRESERVED_MEMORY_SIZE=${XSAI_RESERVED_MEMORY_SIZE}")
```

On the NCNN side the corresponding switch is the CMake macro `NCNN_XSAI_AME=1`,
with the environment variable `XSAI_NCNN_AME` selecting it at runtime.

The remaining files link normally without the flag, which is what makes the
single-translation-unit approach viable.

## 4. Add a fallback path

The matrix path is enabled only when the conditions hold: the hardware shape is
trustworthy, the shape is within the limits, and the workload is large enough.
When any of them fails, the upper layer must take the framework's own kernel
rather than return a wrong intermediate result.

The criteria and what happens when they are unmet are in
[Enable conditions](../software/frameworks.md#sec:sw-fw-guards).

The two easiest mistakes:

* `mrelease` / `macquire` not covering all exit branches → intermittent failures
  that do not reproduce reliably;
* the base register reclaimed by the compiler → the same intermittent failures.

Neither is a tolerance problem that is "sometimes fine"; both mean the
synchronization protocol is broken and must be fixed.

## 5. Verify and take it to the board

Run the framework's own operator tests first, then move up the ladder. The
criteria and how much to trust each level are in
[Verification basis](../software/frameworks.md#sec:sw-frameworks); the methodology
is in [Differential Verification](../verification/difftest.md#sec:debug-difftest).

## After the operator works

Working is not the same as fast. When performance is below expectation, start with
the [Performance Analysis Path](path-perf.md#sec:path-perf) and look at the software
stages first rather than suspecting the RTL.
