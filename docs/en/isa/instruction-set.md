# Instruction Set Extensions {#sec:xsai-instruction-set}

This chapter documents the instruction set delta of XSAI over Kunminghu V2R2.
For the baseline extension list see the _XiangShan Open-Source Processor User
Guide_ (Instruction Set chapter).

## Extensions and versions

| Extension | Description | Specification |
| --- | --- | --- |
| ZAMES | Matrix compute extension (configuration, matrix multiply-accumulate, matrix memory access) | Zames draft v0.6 (simplified v0.1); the current implementation matches proposal-12 |
| ZMASYNC | Synchronization companion extension of ZAMES | as above |
| Low-precision convert | `vfncvtmxfp.f.f.w`, `vfncvtxx8.f.a.w`, ... | see the multi-precision proposals |

The canonical spelling is **`ZMASYNC`**; the lowercase `zamesync` seen in older
discussions means the same extension.

In the LLVM tools the extensions are enabled through `-mattr`:

```bash
llvm-mc -triple=riscv64 -mattr=+zames input.s
llvm-mc -triple=riscv64 -mattr=+zmasync input.s
llc -mtriple=riscv64 -mattr=+zames input.ll
```

| Feature | Meaning |
| --- | --- |
| `+zames` | simplified matrix configuration instructions, matrix load/store, `mzero` and `mmacc` |
| `+zmasync` | synchronization companion extension of ZAMES providing the sync-register instructions; it depends on `+zames` in its feature definition |
| legacy `+zame,+matrix-xuantie-0.6` | the old Xuantie-0.6 instruction path, **about to be removed: do not use it**, and do not mix it with the user-visible ZAMES syntax |

In the programming model `+zmasync` is the asynchronous synchronization
extension, not a stand-alone matrix compute ISA.

## User-visible registers

| Kind | Name | Purpose |
| --- | --- | --- |
| A / B tile registers | `tr0` – `tr3` | hold the A / B input matrix tiles |
| C accumulator registers | `acc0` – `acc3` | hold the C output or accumulation tiles |
| Configuration selectors | `mcfg0` – `mcfg7` | used by `msetcfg` / `mgetcfg` |
| Sync registers | `sync0` – `sync15` | ZMASYNC synchronization registers |
| Scalar registers | RISC-V GPRs | addresses, strides, tile shapes, compare values, raw `mcfg` values |

Three constraints must be observed:

* the old `tok0` – `tok15` spellings are no longer user-visible assembly syntax;
* `sync16` – `sync31` are reserved encodings, which assemblers and disassemblers
  should reject;
* do not treat CSRs as an ordinary programming interface: the `mcsr` and
  `mstatus` / `sstatus.MS` mechanisms should not be relied on directly on the
  ZAMES path yet.

LLVM IR internal type names may still show `target("riscv.ame.token")`; that is an
IR type name, not an assembly register name.

### Matrix registers and their configuration registers

ZAMES uses a 3-bit matrix register selector, and the selector chooses **both** the
matrix register and its associated `mcfg`:

| Selector | Matrix register | Configuration register |
| --- | --- | --- |
| `000` | `tr0` | `mcfg0` |
| `001` | `tr1` | `mcfg1` |
| `010` | `tr2` | `mcfg2` |
| `011` | `tr3` | `mcfg3` |
| `100` | `acc0` | `mcfg4` |
| `101` | `acc1` | `mcfg5` |
| `110` | `acc2` | `mcfg6` |
| `111` | `acc3` | `mcfg7` |

Size model: `tr0` – `tr3` are `TLEN` bits wide with a row width of `TRLEN` and
`ROWNUM = TLEN / TRLEN` rows; `acc0` – `acc3` are `ALEN` bits wide with a row
width of `ARLEN` and the same `ROWNUM` rows.

## Tile shape convention

ZAMES describes the active tile shape of one matrix operation with three separate
values, `mtilem`, `mtilek` and `mtilen`:

| Matrix | Typical shape | Related instructions |
| --- | --- | --- |
| A | `mtilem × mtilek` | `mla` / `msa` |
| B | `mtilen × mtilek` | `mlb` / `msb` |
| C | `mtilem × mtilen` | `mlc` / `msc` / `mmacc` |

> Note that `mtilek` is the **shared** reduction dimension. When team documents
> write the native geometry as `128x64x128`, the order is therefore M-K-N; in the
> M-N-K notation used here that is **128 × 128 × 64**. The two are the same
> geometry written in a different order.

## Configuration and control instructions

| Instruction | Example | Meaning |
| --- | --- | --- |
| `minit` | `minit` | initialise the matrix state so that matrix register contents may be treated as discardable |
| `msettilemi` | `msettilemi 16` | set `mtilem` from an immediate |
| `msettilem` | `msettilem a0` | set `mtilem` from a GPR |
| `msettileni` | `msettileni 16` | set `mtilen` from an immediate |
| `msettilen` | `msettilen a1` | set `mtilen` from a GPR |
| `msettileki` | `msettileki 64` | set `mtilek` from an immediate |
| `msettilek` | `msettilek a2` | set `mtilek` from a GPR |
| `msetcfg` | `msetcfg mcfg0, a0` | set the raw `mcfg` associated with one matrix register |
| `mgetcfg` | `mgetcfg a0, mcfg0` | read one raw `mcfg` |
| `mzero` | `mzero acc0` | clear a tile or accumulator register without changing its `mcfg` |

`mcfg` encoding: the low 8 bits select the type, with `[3:0]` as `type_code`
(choosing a data type inside the selected type table) and `[7:4]` as `table_sel`
(choosing the type encoding table); `[XLEN-1:8]` is an uninterpreted payload that
`msetcfg` stores and `mgetcfg` reads back unchanged, and the current matrix
execution semantics do not interpret those bits.

Do not use the old name `msettype mtype0, a0` on the ZAMES path.

## Data types

`type_code` encoding with `table_sel = 0`:

| `type_code` | Type | `type_code` | Type |
| --- | --- | --- | --- |
| `0000` | `int4` | `1000` | `fp8e4m3` |
| `0001` | `uint4` | `1001` | `fp16` |
| `0010` | `int8` | `1010` | `bf16` |
| `0011` | `uint8` | `1011` | `tf32` |
| `0100` | `int32` | `1100` | `fp32` |
| `0101` | `nvfp4` | `1101` | `fp2pack4` |
| `0110` | `mxfp4` | `1110` | `fp2pack5` |
| `0111` | `fp8e5m2` | `1111` | reserved |

That is 15 named types. Both current XSAI MatrixConfigs enable only
**int8 → int32, fp8 → fp32 and bf16 → fp32**. For block scaling, the XSAI version
of `MatrixTE` takes no `ScaleA` / `ScaleB` input and does not support MXFP / NVFP
arithmetic, so although `mxfp4` and `nvfp4` appear in the type table they are
unusable. Software must not rely on an unenabled type; confirm with the type
probe or by writing and reading back `mcfg` before use.

## Matrix multiply-accumulate

| Family | Input precision | Output precision | Notes |
| --- | --- | --- | --- |
| `mmacc` integer | i8 × i8 | i32 | 4-bit (int4 / uint4) needs pack / unpack first and is not enabled |
| `mmacc` floating point | bf16 × bf16 | fp32 | the current v13 / min-v6 configuration enables bf16 → fp32 |
| Low precision | fp8 e4m3 / e5m2 | fp32 | the current configuration enables fp8 → fp32; the fp4 families are not enabled |

`mmacc acc0, tr1, tr0` accumulates the product of A and B into the active C region
of `acc0`. The operand constraints are:

* `md` must be `acc0` – `acc3`;
* `ms2` and `ms1` must be `tr0` – `tr3`;
* the common form puts B in `ms2` and A in `ms1`: `mmacc acc0, tr1, tr0`.

`msettilek` counts **elements** (32 for bf16, 64 for i8) and the tile **row
width** `TRLEN` is **64 bytes**; the `stride` operand of `mla` / `mlb` is in
bytes. The
bf16 and int8 switches must be separate: bf16 changes the floating-point
precision, and sharing a switch makes the official fp32 tests fail on tolerance.

## Matrix memory access

The memory operand format is `op matrix_reg, (base_gpr), stride_gpr`, where
`base_gpr` is the base address of the tile's top-left element and `stride_gpr` is
the matrix row stride **in bytes**. The target or source must be `tr0` – `tr3` for
A / B and `acc0` – `acc3` for C.

| Class | Instructions |
| --- | --- |
| load | `mla`, `mlb`, `mlc` |
| store | `msa`, `msb`, `msc` |
| transposed load | `mlat`, `mlbt`, `mlct` |
| transposed store | `msat`, `msbt`, `msct` |
| whole-register load | `mla.whole`, `mlb.whole`, `mlc.whole` |
| whole-register store | `msa.whole`, `msb.whole`, `msc.whole` |

```plain
mla tr0, (a0), a1      # load A tile
mlb tr1, (a2), a3      # load B tile
mlc acc0, (a4), a5     # load C tile

msat tr0, (a0), a1     # transposed store A tile
```

### Whole-register transfer

A whole-register transfer saves or restores one **complete** architectural matrix
register; it does not interpret the data according to the current element type or
active tile shape, and it fixes the stride position to `x0`:

```plain
msa.whole tr0, (save_tr0), zero       # save complete matrix register state
msc.whole acc0, (save_acc0), zero 

mla.whole tr0, (save_tr0), zero       # restore complete matrix register state
mlc.whole acc0, (save_acc0), zero 
```

**The current toolchain requires the third operand to be written explicitly and
fixed to `zero`**: a two-operand form such as `msa.whole tr0, (a0)` is rejected by
the assembler (`too few operands`). Writing a non-`zero` third register is
accepted, but that is an ordinary transfer **with stride**, not the whole-register
form, and its semantics differ.

### Address translation and alignment constraints

The current implementation performs address translation and access-protection
checks **on the base address only**. Software must ensure the entire matrix access
range lies in a physically contiguous region with uniform permissions that PMP
allows; a tile access range that runs into unmapped, non-contiguous or
PMP-disallowed physical regions is not supported.

Three practical constraints follow:

* the operand buffer must be physically contiguous (see
  [Memory Subsystem and HBL2](../hardware/memory.md#sec:xsai-memory));
* row addresses are computed as `PA_base + row × stride`, with no per-row TLB
  re-walk;
* a tail packet (`real_count < DST_XUNIT`) is laid out compactly and must not be
  handled with a fixed stride.

Alignment on the transpose path is handled by one `TransAlignPipe` (non-uniform
alignment pipeline) and one `OOORouter` (out-of-order router with a write
reduction tree) per bank.

## Synchronization and memory ordering

ZMASYNC uses `sync0` – `sync15`:

| Instruction | Example | Meaning |
| --- | --- | --- |
| `msyncregreset` | `msyncregreset sync0` | reset the sync register |
| `mrelease` | `mrelease sync0` | release; typically increments the synchronization state once the asynchronous matrix work has completed or its store is visible |
| `macquire` | `macquire sync0, a0` | wait until `sync0 >= x[a0]` |
| `mfence` | `mfence` | make non-matrix memory data visible to subsequent matrix-engine memory operations |

Mind the operand order:

```plain
macquire sync0, a0      # the ZMASYNC path
```

The legacy Xuantie-0.6 `macquire` order is `macquire a0, sync0`; **do not mix the
two paths**.

Minimal example:

```plain
mfence                 # first push inputs prepared off the matrix engine to it
msyncregreset sync0    # reset the count of this sync register
# ... issue matrix load / mmacc / store here ...
mrelease sync0         # increment, waiting for the matrix store to become visible
li a0, 1
macquire sync0, a0     # block until sync0 >= 1; results are now consumable
```

The threshold register must be initialised first: with `a0` equal to 0 the
`macquire` falls through immediately, which erases the completion condition above.

### Ordering semantics

* Matrix instructions execute asynchronously: commit order and completion order
  may differ;
* use `macquire` for matrix results becoming visible to vector / scalar code, and
  `mfence` for non-matrix accesses becoming visible to the matrix engine; the two
  directions differ;
* `mrelease` / `macquire` must cover **all** exit branches, otherwise
  intermittent errors occur that are hard to reproduce reliably;
* call `msyncregreset` before each tile is used;
* the MSC base address register must be pinned (for example `s11`) and kept alive
  before `macquire`; if the compiler reclaims that register, the errors are
  intermittent;
* reading a matrix register region that was never written is undefined behaviour;
  do not rely on its contents.

## Synchronous GEMM example

A minimal synchronous GEMM-style flow (the register names and configuration
values are illustrative; a real program must generate raw `mcfg`, base addresses
and strides for its data type, layout and tile size):

```plain
# llvm-mc -triple=riscv64 -mattr=+zames,+zmasync

minit

# a0 = M, a1 = K, a2 = N
msettilem a0
msettilek a1
msettilen a2

# t0/t1/t2 = raw mcfg values for A/B/C
msetcfg mcfg0, t0      # tr0 configuration for A
msetcfg mcfg1, t1      # tr1 configuration for B
msetcfg mcfg4, t2      # acc0 configuration for C

# A / B are ready on the CPU side: make them visible to the matrix engine first
mfence

# a3 = A base, a4 = B base, a5 = C base
# a6/a7/t3 = row strides in bytes
mla tr0, (a3), a6      # A[M,K]
mlb tr1, (a4), a7      # B[N,K]
mzero acc0             # initialize C accumulator to zero

msyncregreset sync0    # reset the sync count before each work item

mmacc acc0, tr1, tr0   # C += A x B

msc acc0, (a5), t3     # store C[M,N]

mrelease sync0         # increment, waiting for the store to become visible
li t4, 1
macquire sync0, t4     # block until sync0 >= 1; C is now consumable by the CPU
```

**Do not consume C right after `msc`**: `mmacc` and `msc` are non-blocking
commits, and a commit is not a completion; store results are also not guaranteed to
be visible to subsequent scalar or vector loads immediately. Only after `macquire`
succeeds may CPU-side code read C.

To accumulate into an existing C, replace `mzero acc0` with `mlc acc0, (a5), t3`.

The standard call order is: `minit` → set `mtilem` / `mtilek` / `mtilen` →
`msetcfg` for A / B / C → load A / B / C or `mzero` to initialise C → `mmacc` →
`msc` → `mrelease` / `macquire` to establish the completion condition.

## Low-precision convert instructions

* Defined in the custom opcode space, supporting scale factors and mask encodings;
* the representative instructions are `vfncvtmxfp.f.f.w` (convert to an MXFP
  format) and `vfncvtxx8.f.a.w`.

The direction above is settled, but **this release does not commit to these two
conversion instructions**: none of the RTL, NEMU, QEMU, LLVM or ISA specification
pinned by this release contains a definition of them, so this manual neither gives
an encoding nor promises availability.

Use whatever instruction forms and encodings your own toolchain actually supports,
and do not infer an encoding from this manual.

One related but **different** matter: `mxfp4` / `nvfp4` in the `mcfg` type table
are **matrix multiply-accumulate input types**, unusable in XSAI because its
MatrixTE has no block-scaling path, whereas this section is about the **target
formats of conversion instructions**. Do not conflate the two (see the precision
roadmap table in [Microarchitecture Delta](../hardware/microarchitecture.md#sec:xsai-microarchitecture)).
