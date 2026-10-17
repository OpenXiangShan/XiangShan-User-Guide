# Kernel Libraries and Inference Frameworks {#sec:sw-frameworks}

This chapter covers connecting the matrix unit into inference frameworks and kernel libraries: how the kernel library is layered, where each of the three frameworks can be hooked, the hardware constraints that must hold, and how to verify the result.

## Kernel library (xsai-blas)

### Layering

```text
API → Interface → Kernel (generic / rvv / ame / triton) → Platform
```

* a unified `validate` / `execute` interface;
* covering gemm, gemv, matmul, softmax, silu, rms_norm, add, div, mul and others;
* a call descriptor
  (`xsai_op_call_t`) plus an op_handler table plus a dispatcher, **so adding an
  operator now means implementing a handler**;
* the tensor interface is aligned with DLPack, so framework-side tensors pass in with zero copy.

The value is packaging hardware-specific operations behind a stable compute
interface, reducing the upper framework's dependence on instruction and SoC
details.

### Operator list

| Class | Operators | Notes |
| --- | --- | --- |
| Matrix multiply | gemm, gemv, matmul | take the matrix-unit GEMM path, subject to the [enable conditions](#sec:sw-fw-guards) |
| Normalisation | softmax, rms_norm, layernorm | typical implementations on the matrix unit |
| Activation | silu, gelu | often fused into the GEMM epilogue |
| Element-wise | add, div, mul | mostly left on the vector / scalar path |

### Adding an operator

Adding an operator means implementing one handler and
registering it in the op_handler table:

```c
/* the call descriptor carries the operator kind, shape and pointers */
xsai_op_call_t call = {
    .op      = XSAI_OP_GEMM,
    .dtype   = XSAI_DTYPE_INT8,
    .m = m, .n = n, .k = k,
    .a = a, .b = b, .c = c,
};

/* the handler checks the conditions and selects the kernel */
int rc = xsai_gemm_handler(&call);
if (rc != 0) {
    /* a failed check returns non-zero and the caller falls back */
}
```

**The handler's responsibility boundary**: check the conditions, select the kernel
implementation, and fall back when needed; it does not convert quantisation
formats, which belongs to the framework epilogue.

## General method for integrating the matrix unit

Follow these five steps, in this order, to integrate the matrix unit into any
inference framework; the order cannot be swapped.

1. **Probe establishes the spec**: read the native tile geometry of the current
   hardware configuration from the CSR (native M128 × N128 × K64), and generate
   kernels only from the probe result. A tile shape that does not match the hardware
   always produces wrong results.
2. **Find the framework's native replacement point**: prefer the function table where
   "replacing the implementation replaces the kernel"; next the arch-layer
   implementation; and only then a drop-in at the call site.
3. **Single translation unit**: all matrix instructions live in one `.c` file
   compiled with the `zames` march, and other files reach them only through the
   header.
4. **Add condition checks and a fallback path**: three conditions, namely capability, shape and workload;
   if any one of them is not satisfied, let the upper layer fall back to the
   framework's own kernel, and never return wrong data.
5. **Differential verification first, then staged bring-up on the board**:
   byte-identical output comes first, QEMU verifies arithmetic only, and a
   board-level conclusion is the only authoritative one.

### Hard constraints

| Constraint | Content |
| --- | --- |
| tile shape | Native M128 × N128 × K64 (written `128x64x128` in M-K-N order in design documents); take the actual value from the probe, never hard-code it |
| bf16 K parameter | `msettilek` counts **elements** (32 for bf16, 64 for i8), while the tile **row width** `TRLEN` is **64 bytes**. Note the assembly form `mla tr0, (base), stride` has **no length operand**; `stride` is in bytes |
| C accumulator | **Depends on the input type**: the integer path i8 × i8 → **int32**, the float paths (bf16 / fp16 / tf32) → **fp32**; low-precision inputs do not change the accumulator width |
| Operand pool | Must be physically contiguous (`/dev/mem` @ `0x100000000`); AMU row addressing does not walk the TLB, so non-contiguous memory is read incorrectly without any error |
| Base register | The MSC base is pinned to `s11` and kept live until `macquire`; every tile uses `msyncregreset` |
| Synchronization | `macquire` carries matrix results outward, `mfence` carries non-matrix accesses inward; `mrelease` / `macquire` must cover all exit branches |

### Enable conditions {#sec:sw-fw-guards}
| Guard | Criterion | When not satisfied |
| --- | --- | --- |
| Spec available | The probe returns trustworthy geometry | The whole matrix path is disabled |
| Shape | K ≤ upper bound (8192 elements by default), `real_count` within the legal range | Fall back to the framework's own kernel |
| Workload | `oc × K ≥ 16384` (adjustable through an environment variable) | Fall back to the framework's own kernel |

Why the workload condition is necessary: the convolution case only hands over
8 pixels at a time, so with `tile_m = 128` the M utilisation is constantly 6%;
occupying an almost empty tile is worthwhile only when `oc × K` is large enough.
For small layers the framework's own RVV kernel is faster.

## Framework replacement points

![Replacement points in the three frameworks](../figs/framework-seam.svg "Replacement points in the three frameworks")

| Framework | Seam | Note |
| --- | --- | --- |
| MNN | core functions table (`MNNPackedMatMul` and others) | "Swapping the table swaps the kernel", with the widest coverage; the LLM paths `CPUMatMul`, `CPUAttention` and `BatchMatMul` all go through the same table |
| NCNN | arch-layer implementation (registry + `Convolution_riscv::forward`) | There is no function table, so do not do a drop-in at the call site (each variant must be inserted separately and does its own packing); riscv int8 convolution was missing to begin with, so writing it from scratch is cleaner |
| ggml | `ggml-cpu/arch/riscv/ame/ame-matmul.c` | Reference implementation; kernel selection requires `M ≥ 64` and `N ≥ 64`, so decode (M=1) does not take tiles and only prefill benefits |

### The matrix switch (AME on/off)

"Byte-identical output with the matrix switch on and off" is the top criterion used
repeatedly in this chapter and later ones, but **the three frameworks have three
different switch mechanisms**; there is no unified switch:

| Framework | Switch | Mechanism |
| --- | --- | --- |
| MNN | environment variable `XSAI_MNN_AME`, value must be `1` | evaluated at run time; read by the bf16, LLM and int8 paths alike |
| NCNN | compile-time macro `NCNN_XSAI_AME` **plus** run-time environment variables `XSAI_NCNN_AME` (int8) / `XSAI_NCNN_AME_BF16` (bf16) | **both are required**: the macro gates the code path, the variables select at run time, and the variable value must be **exactly `1`** |
| ggml | buffer type `--buft RISCV_AME` | run-time backend selection, **not an environment variable** |

ggml additionally has a set of fine-grained environment variables (`GGML_AME_*`,
such as `GGML_AME_PACKED_Q8` and `GGML_AME_FLASH_ATTN`) that disable individual
optimisations; keep them unchanged when running a differential comparison.

**Do not judge "did it really take the matrix path" from the backend name in the
framework log alone.** In the ggml case AME is the `RISCV_AME`
path under the ggml CPU backend, so a `CPU` value in the `be` column does not mean
AME was unused — check `[AME_PROFILE]`, `[GGML_XSAI_OP_PROFILE]` and the AME
dispatch logs instead.

## llama.cpp / GGML

* Integrated through the matrix backend, with operator diff tests and per-layer
  sampling on the model side;
* Kernel selection requires `M ≥ 64` and `N ≥ 64`: decode goes through
  vec-dot/GEMV, and only prefill uses the matrix unit;
* Mind K-dimension alignment: when K is not a multiple of 128, padding or tail
  handling is required (this has caused deviations in the relevant operators
  before).

### Analysing operator performance

To decide whether the bottleneck is hardware or software, break the matrix unit's
cycles down **by stage** instead of looking only at total utilisation. The first
step is to separate two bases:

| Basis | Formula | Meaning |
| --- | --- | --- |
| whole operator | `logical ops / AME total cycles / peak logical ops per cycle` | end to end, including every software stage |
| macro-call path | `logical ops / ame_tile_call cycles / peak` | only the stretch where the matrix unit is called |

**The two must be read separately.** Low whole-operator utilisation does not mean
the hardware is inadequate — the gap can come almost entirely from software-side
stages: quantisation, data packing, the scale epilogue, edge tiles, or
insufficient synchronised supply. Once cycles are broken down by stage, the share
taken by `ame_tile_call` (the stage that actually drives the matrix unit) against
the rest tells you directly whether to optimise software or hardware, and where
the ceiling on the gain is.

For stage names, the available counters and the attribution tree see
[Performance Monitor](../hardware/pmu.md#sec:xsai-pmu).

Accumulating in INT32 across K64 needs an overflow proof:
`K × 127 × 127 ≤ INT32_MAX`, which for K=8192 gives 132,128,768 and holds; a
larger K must be proved again. It changes the quantisation granularity and
accumulation order, so a real-model accuracy regression is mandatory.

## Edge frameworks

* **MNN**: the int8 pack convention is `UNIT=4(oc)` / `SRC_UNIT=16(ic)` /
  `DST_XUNIT=8(px)`; bf16 layers keep `bytes=4` and only the matmul operands use
  `matmulBytes=2`; the `[l][eP]` layout of `CPUMatMul` (transpose plus in-place
  lowp) is naturally compatible with the layout the bf16 kernel expects, so do
  not add an extra conversion layer; on riscv LLMs go through fp32 by default,
  so `Precision_Low_BF16` must be set explicitly.
* **NCNN**: cross-compilation must switch off the host ISA options (`NCNN_SSE2`
  / `AVX` / `AVX2` / `AVXVNNI` / `AVX512` / `XOP` / `FMA=OFF`) and use a
  toolchain file; the tests are **silent on success** (`rc=0` with no output),
  so pass/fail relies on the return code plus a call counter; `onnx2ncnn`
  mishandles dynamic shapes (it writes NaN into the bin header and emits an
  unregistered Shape layer), so first fold
  `Shape→Gather→Unsqueeze→Concat→Reshape` into constants at the ONNX level, and
  after folding verify with ONNX Runtime that argmax is unchanged before
  converting.
* **fp16 weight models**: just convert them to the bf16 backend (the ggml
  `F16_BF16` idea); there is no need to write a separate kernel for fp16.

## Principles for handling quantization formats

The matrix kernel does GEMM only (int8 → int32 with exact accumulation); the
scale table, zero-point compensation, requant/dequant, clamp and fused
activation all copy the epilogue of the framework's reference implementation.
This way the output is bit-identical with the framework reference, and format
differences are covered by construction. **The replacement point is GEMM rather than the
operator**, so do not reimplement the quantization format inside the kernel.

| Dimension | Variant | Handling |
| --- | --- | --- |
| scale granularity | per-tensor / per-output-channel | per-oc is the most common; take the tail table by oc, and the read path is exactly the same as per-tensor |
| Input zero-point | symmetric / asymmetric | MNN compensates with `srcSum × weightBias`: first compute the row sums of A, then add that correction term in the epilogue |
| Output type | requant→int8 / dequant→fp32 | Both epilogue branches must be implemented (NCNN decides requant with `int8_scale_term > 100`; division by zero must be checked) |
| Saturation / clamping | int8 `[-127,127]` / fp32 `fp32minmax` | Copy the reference implementation |
| Fused activation | Yes | Reuse the framework's activation parameters; do not approximate them yourself |

**Unsupported formats fall back directly, with no
approximation**: weights that are not 1 byte per element (4-bit / 6-bit /
mixed-precision compressed weights), packed layouts (`elempack > 1` requires
unpacking first, or making A's packing pack-aware), out-of-range
shapes, and insufficient workload.

bf16 and fp16 differ in **precision** rather than in quantization format: bf16
takes the high 16 bits of fp32, accumulates in fp32, and writes C as fp32 or
truncates it to the bf16 grid according to the framework contract. The switches
for bf16 and int8 must be kept separate, because bf16 changes floating-point
precision and a shared switch would make the official fp32 tests fail on
tolerance.

## Verification criteria

```plain
framework's own tests (operator level) → QEMU user mode (network level, arithmetic criteria only) → NEMU → board-level measurement (authoritative)
```

* **Prefer the framework's own tests; do not build a second suite**: for MNN use
  `run_test.out <test> 0 <precision>` (3 means `Low_BF16`); for NCNN every
  operator has its own executable and `rc=0` means it passes; for ggml use
  `test-backend-ops` and `test-op`.
* Ranking of evidence strength: (1) the same model produces **byte-identical**
  output with the matrix switch on and off (the hardest evidence, independent
  of precision); (2) the framework's own tests pass in both modes, and failures
  appear only with the switch on; (3) a self-built reference implementation is
  compared element by element in both modes (byte-identical for int8, a
  two-tier tolerance for bf16); (4) argmax or top-5 is compared against an
  external ground truth (ONNX Runtime or a host framework).
* **The quantization calibration method is unrelated to matrix adaptation**:
  whether int8 calibration uses percentile or KL changes the argmax, and this is not an error introduced by the adaptation;
  whether the adaptation is correct is judged only by byte-identical output with
  the vector switch on and off.
* A self-built differential tool only fills the gaps that the framework tests
  do not cover (a particular shape, tail block or deep-K combination), or is
  used when element-by-element byte comparison is required.
