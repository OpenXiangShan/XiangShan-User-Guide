# Appendix A: Delta over Kunminghu V2R2 {#sec:appendix-diff}

This page is the full ledger of the delta. Everything the manual covers is one or
more of these items.

| Module | Delta | Affects | See |
| --- | --- | --- | --- |
| Matrix compute unit | matrix compute and memory-access path, transpose engine | ISA, memory access, performance | [Microarchitecture Delta](../hardware/microarchitecture.md#sec:xsai-microarchitecture) |
| Matrix control path | command issue, completion notification and commit semantics | instruction commit, exceptions | same chapter |
| Registers | matrix, configuration and synchronization registers | programming model | [Data Registers](../isa/registers.md#sec:xsai-registers) |
| CSRs and device tree | the matrix state field and how precision capability is described | firmware, operating system | [Matrix CSRs](../isa/csr.md#sec:xsai-csr), [System Software and Runtime](../software/system.md#sec:sw-system) |
| High-bandwidth L2 | HBL2 and the matrix-dedicated memory path | memory subsystem, performance | [Memory Subsystem and HBL2](../hardware/memory.md#sec:xsai-memory) |
| Instruction encoding | an `async` bit separating synchronous from asynchronous matrix instructions | compilation, synchronization | [Microarchitecture Delta](../hardware/microarchitecture.md#sec:xsai-microarchitecture) |
| Performance monitoring | matrix-related HPM events and Top-down levels | tuning | [Performance Monitoring](../hardware/pmu.md#sec:xsai-pmu) |
| Verification and debug | matrix support in difftest, checkpoint sampling | verification flow | [Differential Verification](../verification/difftest.md#sec:debug-difftest), [Checkpoints and Slicing](../verification/checkpoint.md#sec:debug-checkpoint) |
| Precision | only INT8, FP8 and BF16 combinations enabled | quantisation, accuracy verification | [Data Registers](../isa/registers.md#sec:xsai-registers) |

## Verification coverage

| Level | Coverage |
| --- | --- |
| Unit level | key CUTE points: TileLink transaction alignment and size, register file read/write timing, matrix multiply-accumulate results, the int8 × int8 → int32 and uint8 × uint8 → uint32 type combinations, boundary conditions |
| Integration level | the CUTE + L2 random-stimulus framework |
| Differential verification | full comparison of the matrix CSRs and `mcfg0` – `mcfg7`, see [Differential Verification](../verification/difftest.md#sec:debug-difftest) |
