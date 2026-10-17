# Matrix Data Registers {#sec:xsai-registers}

This chapter describes the matrix-related registers added by XSAI. Scalar and
vector registers are identical to Kunminghu V2R2.

## Matrix registers

| Type | Name | Purpose |
| --- | --- | --- |
| A / B tile | `tr0` – `tr3` | Operands of the matrix multiply-accumulate |
| C / acc tile | `acc0` – `acc3` | Accumulation and results |

On the integer path the `acc` accumulator is int32 (i8 × i8 → i32); on the
floating-point (bf16) path it is fp32. Low-precision inputs do not change the
accumulator width.

## Native tile shape

The native shape of the matrix unit is **M128 × N128 × K64**, fixed by the
hardware configuration. Software must not assume it.

Do not hard-code the shape; read the actual value through the CSRs at start-up —
see [Matrix CSRs](csr.md#sec:xsai-csr). A wrong shape raises no error, it just
computes wrong results: a whole layer failing on real hardware while the same
payload is correct in QEMU is usually this cause.

| Probe | Value | Meaning |
| --- | --- | --- |
| `tlenb` | 8192 B | length of one tile register |
| `trlenb` | 64 B | tile row width |
| `alenb` | 65536 B | length of one accumulator |

`ROWNUM = tlenb / trlenb = 128` is the limit on M and N. Design documents write the
shape in M-K-N order as `128x64x128`, which is the same shape as the M-N-K order
here.

Register capacity: one AB register (`tr0` – `tr3`) is 8 KiB and one accumulator
(`acc0` – `acc3`) is 64 KiB.


If the tile shape and the hardware do not match, the result is guaranteed to
be wrong; a whole layer failing on the board while QEMU is fully correct is
usually this case.

## Configuration registers

* `mcfg0` – `mcfg7`: written by `msetcfg` and read back by `mgetcfg`. The full
  bit fields are:

| Bits | Field | Meaning |
| --- | --- | --- |
| `[3:0]` | `type_code` | selects a data type inside the chosen type table (encodings in [Instruction Set Extensions](instruction-set.md#sec:xsai-instruction-set)) |
| `[7:4]` | `table_sel` | selects the type encoding table |
| `[XLEN-1:8]` | uninterpreted payload | stored by `msetcfg` and read back unchanged by `mgetcfg`; the matrix execution semantics do not interpret these bits |

The three selector bits choose the matrix register and its associated `mcfg`
together: `000` – `011` map to `tr0` – `tr3` / `mcfg0` – `mcfg3`, and `100` –
`111` map to `acc0` – `acc3` / `mcfg4` – `mcfg7`. The tile shape comes from
`mtilem` / `mtilen` / `mtilek`; transpose and whole-register modes are encoded in
the memory access instructions.

### Shape and type parameters

* `msettilem` / `msettilen` / `msettilek`: set the M, N and K dimensions of the
  tile.
* On the bf16 path `msettilek` counts in **elements** (`msettilek=32`), whereas
  the length operand of `mla` / `mlb` counts in **bytes** (corresponding to
  64 bytes).
* K must be aligned to the tile K limit: 64 elements for i8 and 32 elements for
  bf16. The calling side (for example the ggml path) requires K to be a multiple
  of 32; shorter K needs padding or tail handling.

### Illegal and legacy configurations

The following forms are not accepted on the ZAMES path and indicate an error:

| Form | Problem | Correct form |
| --- | --- | --- |
| `msettype mtype0, a0` | ZAMES does not use the old `mtype` configuration syntax | `msetcfg mcfg0, a0` |
| `mzero1r acc0` | the user-visible syntax is `mzero` | `mzero acc0` |
| `mla.whole tr0, (a0)` | the current toolchain requires the third operand explicitly; omitting it is rejected by the assembler | `mla.whole tr0, (a0), zero` |
| `macquire a0, sync0` | that is the legacy Xuantie-0.6 order | `macquire sync0, a0` |
| `tok0` | the old token spelling is no longer user-visible syntax | `sync0` |
| `sync16` | `sync16` – `sync31` are reserved encodings | `sync0` – `sync15` |

`type_code = 1111` is reserved. Software must not rely on an unenabled type;
confirm with the type probe or by writing and reading back `mcfg` before use.

## Synchronization registers

* `sync0` – `sync(N−1)`: synchronization and dependency tracking for asynchronous
  matrix operations. **The specification and the implementation differ here, so
  confirm before use**:
    * assembly specification: the user-visible range is `sync0` – `sync15`, and
      `sync16` – `sync31` are reserved encodings that assemblers and disassemblers
      should reject;
    * the implementation may provide **32** synchronization registers, and the
      actual count is reported by the read-only `msync` CSR (RTL address
      `0xcc7`);
    * so assume neither that all 32 are always usable nor that only 16 exist.
      Read `msync` with the probe and follow that value.
* Call `msyncregreset syncN` before each tile is used; the producer advances the
  register with `mrelease syncN` and the consumer waits for `syncN >= x[rs1]` with
  `macquire syncN, rs1`.
* `minit`: marks the data in the matrix registers as discardable, reducing
  context-switch cost.

For the full synchronization semantics see
[Instruction Set Extensions](instruction-set.md#sec:xsai-instruction-set).
Note that relying directly on CSR mechanisms such as `mcsr` and
`mstatus` / `sstatus.MS` on the ZAMES path is currently not advised.

## Layout and alignment constraints

* The operand buffer must be physically contiguous: the AMU computes row
  addresses as `PA_base + row × stride` and does not re-walk the TLB for every
  row, so a non-contiguous buffer is silently misread once the row count is
  large. **The base is resolved at runtime**: the pool base is resolved at runtime (environment → device tree `direct_map` → compile-time fallback), not a fixed value; the default layout is 6 GiB at `0x1_0000_0000` and the mega layout 4 GiB at `0x3_8000_0000`, see [Memory Subsystem and HBL2](../hardware/memory.md#sec:xsai-memory). Note that
  `0x2_8000_0000` is the top of RAM in the default layout, that is the pool's
  **end** address, not its base. `/dev/mem` is one way to obtain such a buffer,
  not the only one;
* Transposed memory access follows row-major / column-major conventions,
  controlled by the stride of the memory access instruction;
* When comparing dumps in differential verification, exclude the padding
  introduced by 16 B alignment (uninitialised memory) and compare only the valid
  elements; otherwise false failures appear.

![Matrix registers and their configuration register selection](../figs/register-map.svg "Matrix registers and their configuration register selection")

### Context switching

The matrix architectural state comprises `tr0` – `tr3`, `acc0` – `acc3` and their
associated `mcfg0` – `mcfg7`. Saving and restoring uses whole-register transfers,
which move a complete register and do not interpret the data according to the
current element type or active tile shape:

```plain
msa.whole tr0, (save_tr0), zero 
msc.whole acc0, (save_acc0), zero 

mla.whole tr0, (save_tr0), zero 
mlc.whole acc0, (save_acc0), zero 
```

`minit` marks the matrix state as discardable, so a context switched out after
`minit` need not be saved in full.
