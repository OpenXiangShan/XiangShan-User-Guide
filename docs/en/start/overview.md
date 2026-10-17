# XSAI AI Software and Hardware Overview {#sec:xsai-overview}

XSAI is a RISC-V processor for AI inference built on top of
XiangShan Kunminghu V2R2. It keeps the CPU programming model and adds the AME
matrix extension, the matrix control path and a high-bandwidth L2 (HBL2).

This manual documents only the delta over Kunminghu V2R2; for everything shared
with the baseline, see the _XiangShan Open-Source Processor User Guide_. The
item-by-item delta is in [Appendix A](../appendix/diff.md#sec:appendix-diff).

## Relation to Kunminghu V2R2

* Baseline: XiangShan Kunminghu V2R2
* Delta: AME matrix extension, matrix control path, high-bandwidth L2 (HBL2),
  asynchronous matrix execution
* Software-visible changes: new instructions and CSRs, device-tree capability
  description, matrix access alignment and transpose constraints, asynchronous
  synchronization semantics
* Debug-visible changes: matrix register support in difftest, matrix-related
  performance counters, checkpoint sampling

## The stack

XSAI's capabilities reach a model only through the compiler, the kernel library and
the inference framework. The figure shows the layers of the stack, and the table
maps each layer to the chapters that cover it.

![XSAI AI software and hardware stack](../figs/stack-full.svg "XSAI AI software and hardware stack")

| Layer | Contents | See |
| --- | --- | --- |
| Models and applications | On-device language, vision and speech models | — |
| Inference frameworks | llama.cpp / ggml, MNN, NCNN | [Kernel Libraries and Inference Frameworks](../software/frameworks.md#sec:sw-frameworks) |
| Kernel libraries | GEMM, attention, quantisation and dequantisation kernels | [Kernel Libraries and Inference Frameworks](../software/frameworks.md#sec:sw-frameworks) |
| Compiler and runtime | LLVM backend, operator DSL, system software | [Compiler and Operator DSL](../software/compiler.md#sec:sw-compiler), [System Software and Runtime](../software/system.md#sec:sw-system) |
| XSAI processor | Scalar cores + matrix compute unit + high-bandwidth L2 | [Microarchitecture Delta](../hardware/microarchitecture.md#sec:xsai-microarchitecture) |
| Memory and storage | HBL2, DDR main memory | [Memory Subsystem and HBL2](../hardware/memory.md#sec:xsai-memory) |

## Hardware delta over Kunminghu V2R2

![Delta over Kunminghu V2R2](../figs/delta-overview.svg "Delta over Kunminghu V2R2")

Kunminghu V2R2 provides the scalar cores, the out-of-order pipeline, the cache
hierarchy and the vector unit. XSAI adds the matrix compute unit (CUTE), the matrix
control path and the high-bandwidth L2.

## Ecosystem collaboration

XSAI and RuyiAI collaborate on the XSAI software ecosystem in three areas: on the
framework side, the matrix backend for llama.cpp / ggml, MNN and NCNN; on the
kernel side, the operators in xsai-blas; on the compiler side, the LLVM backend
path that turns Triton and TileLang operator descriptions into matrix instructions.

The work is described in [Kernel Libraries and Inference Frameworks](../software/frameworks.md#sec:sw-frameworks)
and [Compiler and Operator DSL](../software/compiler.md#sec:sw-compiler). Where an
upper-layer framework behaves differently from the instructions or memory
constraints this manual documents, the manual is the reference.
