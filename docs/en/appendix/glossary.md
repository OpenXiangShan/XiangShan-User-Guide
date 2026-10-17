# Appendix B: Glossary {#sec:appendix-glossary}

## Hardware units

| Abbreviation | Full name | Notes |
| --- | --- | --- |
| AME | Attached Matrix Extension | the attached matrix extension |
| AMU | — | matrix memory-access and command management unit |
| CUTE | — | the matrix compute unit |
| MTE | Matrix Tensor Engine | the matrix multiply-accumulate path, an outer-product dataflow over the PE array |
| FPE | Floating Point Engine | the basic arithmetic unit inside MTE |
| ADC / BDC | A / B Data Controller | operand read-out for the A / B paths |
| AML / BML / CML | A / B / C Memory Loader | the A / B / C matrix movement paths |
| LocalMMU | — | the matrix unit's outward data-side interface, reaching LLC and the memory hierarchy |
| TaskController | — | matrix task scheduling and issue |
| HBL2 | High Bandwidth L2 | the high-bandwidth L2, reworked from `CoupledL2` |
| PMU / HPM | Hardware Performance Monitor | the hardware performance monitoring unit |
| LCOFIP | Local Counter Overflow Interrupt Pending | performance counter overflow interrupt, vector **13** (12 is `SGEI`) |

## Registers and programming model

| Term | Notes |
| --- | --- |
| `tr0` – `tr3` | A / B tile registers |
| `acc0` – `acc3` | C accumulator registers |
| `mcfg0` – `mcfg7` | configuration registers paired one-to-one with the matrix registers; a 3-bit selector picks both |
| `sync0` – `sync15` | ZMASYNC synchronization registers (`sync16` – `sync31` are reserved encodings) |
| `mtilem` / `mtilen` / `mtilek` | the M / N / K dimensions of the current tile; `mtilek` is the shared reduction dimension |
| `TLEN` / `TRLEN` | tile register length and row width; `ROWNUM = TLEN / TRLEN` |
| `ALEN` / `ARLEN` | accumulator length and row width |
| raw `mcfg` | the raw value of `mcfg`, produced by software for `msetcfg` and read back unchanged by `mgetcfg` |
| `type_code` / `table_sel` | the two fields in the low 8 bits of `mcfg`: type selection and encoding-table selection |
| whole-register transfer | moving a full register (`mla.whole` and similar) without interpreting the element type; the stride position is fixed to `zero` |
| `minit` | marks the matrix register contents as discardable |
| `msyncregreset` | resets a synchronization register; call it before using each tile |
| `mrelease` / `macquire` | advance and wait on synchronization state; `macquire syncN, rs1` waits for `syncN >= x[rs1]` |
| `mfence` | makes non-matrix memory accesses visible to later matrix accesses |
| MSC base register | the address operand register of the `msc` store instruction; pin it (for example to `s11`) and keep it alive until `macquire` |
| `MS` state field | the matrix state field in `mstatus` / `sstatus` / `vsstatus`, folded into the `SD` dirty-state aggregation |

## Performance

| Term | Notes |
| --- | --- |
| MFU | Model FLOPs Utilisation; this manual distinguishes matrix unit utilisation from operator utilisation, and they must not be mixed |
| Roofline | a performance upper-bound model with arithmetic intensity and bandwidth as its axes |
| prefill / decode | the two phases of large-model inference; their bottleneck structure differs, so they must be measured separately |
| Top-down analysis | breaking stall cycles down level by level to the main cause, the subclass and the concrete source |
| `consistency.json` | a TMA-toolkit output used to check that the counts at each level agree |
| epilogue | the scale, zero-point, requant, clamp and activation work after GEMM, which must match the framework's reference implementation |
| per-oc | per-output-channel scale granularity, the most common kind |

## Verification and debugging

| Term | Notes |
| --- | --- |
| difftest | differential verification, comparing against a reference model step by step |
| checkpoint / GCPT | a program state snapshot, and the restore program (`gcpt.bin`) linked into the image to restore architectural state |
| SimPoint | a clustering method for selecting representative slices |
| `GOOD_TRAP` | marks the end of a payload run, usually also the end of RTL simulation |
| UB | Undefined Behaviour |

## Software stack

| Term | Notes |
| --- | --- |
| `elempack` | NCNN's packing level; above 1 requires unpacking first, or a packing-aware path |
| PGO | Profile-Guided Optimisation; a simulator build option, with its gain described in [Functional Simulators](../software/simulators.md#sec:sw-simulators) |
| GSIM | a class of RTL simulation backend, alongside Verilator |
| tail packet | the last packet with fewer pixels than `DST_XUNIT`, laid out compactly |
