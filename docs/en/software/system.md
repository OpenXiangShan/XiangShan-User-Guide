# System Software and Runtime {#sec:sw-system}

The matrix capability has to be discovered by firmware and the operating system before software can use it. This chapter covers how the device tree describes it, what the kernel and runtime each do, and the boundaries of context switching and restore.

## Device tree and capability discovery

* Matrix capabilities are described through the device-tree `riscv,isa-extensions` entries (such as `zame`, `zammai8i32`) and the `xmisa` CSR; `riscv,matrix-isa-caps` is a proposed property that the current implementation does not use;
* Firmware is responsible for filling in the capability description, and the operating system and runtime decide from it whether to enable the matrix path;
* The reported capabilities must match the actual RTL configuration; otherwise software generates kernels against the wrong tile shape.

### Complete device-tree property list

The `/cpus/cpu@0` node of the generated `xiangshan_ai.dts`
(`firmware/nemu_board/dts/build/xiangshan_ai.dts:28-40`) contains:

| Property | Value / meaning |
| --- | --- |
| `reg` | `0x00` |
| `riscv,isa` | `rv64imafdcv` (the base ISA string) |
| `riscv,isa-base` | `rv64i` |
| `riscv,isa-extensions` | the extension list, below |
| `riscv,cbom-block-size` / `cbop-block-size` / `cboz-block-size` | all `0x40` (the Zicbom / Zicbop / Zicboz block size) |
| `interrupt-controller` | a child node with `compatible = "riscv,cpu-intc"` and `#interrupt-cells = <0x01>` |
| `timebase-frequency` | set by `DTSGen.py`'s `--timebase-freq`, **10 MHz by default** |

The full `riscv,isa-extensions` value:

```text
i m a f d c v supm zame zammai8i32 zawrs zba zbb zbs zcb zcmop zfa zfhmin
zicbop zicbom zicboz zicntr zicond zicsr zihpm zihintpause zihintntl zimop
zkt zvbb zvfhmin zvkt
```

The matrix-related entries are **`zame`** (Attached Matrix Extension) and
**`zammai8i32`** (i8 × i8 → i32 matrix multiply-accumulate).

**The capability discovery convention**: multi-letter extensions do not occupy a
`misa` bit; they are reported through `riscv,isa-extensions` as a **list of
lowercase extension-name strings**, and software checks for strings such as
`"zames"` or `"zame"` to decide whether an extension is present
(`riscv-matrix-spec/spec/program_model.adoc:360`).

**What is reported must match the actual RTL configuration** — software uses the
reported content to decide the tile shape and which instructions are
available, and a mismatch leads to kernels generated to the wrong specification.

## Operating system support

### Kernel version and patch set

| Item | Value |
| --- | --- |
| Kernel version | **6.18** (`LINUX_VERSION` in `firmware/Makefile:48`, from `linux-6.18.tar.xz`) |
| Patch set | three patches under `firmware/patches/`, applied in order by `apply-matrix-patch.sh` |

| Patch | Purpose |
| --- | --- |
| `0001-riscv-matrix-first-use-support.patch` | **first-use trap** support for the matrix extension (adds `asm/matrix.h` and `kernel/matrix.c`, and hooks into `do_trap_insn_illegal` in `traps.c`) |
| `0002-riscv-pmu-sbi-legacy-default-keep-fixed-counters.patch` | PMU / SBI compatibility: keep the fixed counters |
| `0003-riscv-fix-system-csr-immediate-mask-width.patch` | fixes the system CSR immediate mask width |

The vector-related items `CONFIG_RISCV_ISA_V` and
`CONFIG_RISCV_ISA_V_DEFAULT_ENABLE` are present in `.config`. Note that
`CONFIG_RISCV_ISA_SUPM` configures the **userspace pointer-masking** extension
(`Smnpm` / `Ssnpm`) and has nothing to do with the matrix extension; do not use it
to enable matrix support.

### Matrix state across context switches

The kernel handles matrix state **isomorphically to vector state**, using a
**first-use trap**:

`SR_MS` corresponds to `mstatus[26:25]` with the same values as the CSR chapter
(`OFF = 0x00000000`, `INITIAL = 0x02000000`, `CLEAN = 0x04000000`,
`DIRTY = 0x06000000`). `asm/matrix.h` provides three inline operations:

```c
static inline void riscv_m_vstate_off(struct pt_regs *regs)
{
    regs->status = (regs->status & ~SR_MS) | SR_MS_OFF;
}

static inline void riscv_m_vstate_on(struct pt_regs *regs)
{
    regs->status = (regs->status & ~SR_MS) | SR_MS_INITIAL;
}

static inline bool riscv_m_vstate_query(struct pt_regs *regs)
{
    return (regs->status & SR_MS) != 0;
}
```

The flow:

1. **Switching a task out** sets `MS` to `Off` (`riscv_m_vstate_off(task_pt_regs(current))`
   in `process.c`, commented "Reset matrix state for userspace first-use flow"), so
   the **matrix register file does not have to be saved**;
2. **on first use**, with `MS = Off`, the kernel expects an illegal-instruction
   trap and `riscv_m_first_use_handler` decides whether the instruction is a matrix
   one:
   * the instruction is 4 bytes and its opcode is one of `custom0` – `custom3`
     (`0x0b` / `0x2b` / `0x5b` / `0x7b`), or
   * it is a system instruction whose CSR falls in `[0x802, 0x80a]` (the XMCSR
     range) or `[0xcc0, 0xcc7]` (the XMINFO range);
3. if so, it sets `MS` to `Initial` and **retries the instruction**, so user space
   needs no explicit enablement.

> **Implementation disagreement**: this handler assumes that a matrix instruction
> executed with `MS = Off` traps, but in the current RTL all three decode-side
> consumers of `msIsOff` are **commented out**, so the RTL does not yet produce
> that trap. See [Exceptions and Interrupts](../isa/exception.md#sec:xsai-exception).

The kernel manages only the `MS` bit at the CSR level and **does not save or
restore matrix register file contents** — the same fact, seen from the other side,
as the checkpoint gap recorded in
[Checkpoints and Slicing](../verification/checkpoint.md#sec:debug-checkpoint).

## Runtime and memory

* Matrix operands must reside in a physically contiguous memory pool (`/dev/mem` @ `0x100000000`);
* The external environment must decide the allocation mode (pool or anonymous); do not compile it into the artifact:
  * anonymous mode is only for QEMU user mode;
  * if it is carried onto the board unconditionally, the result is `SIGABRT` (`rc=134`), or a wrong result under the anonymous pool that the check intercepts (`rc=255`).
* AMU row addressing is computed as `PA_base + row × stride`; the AMU does not re-walk the TLB for every row, so a non-contiguous buffer is read incorrectly and silently when the row count is large.

## Boot flow

### GCPT restore boot

`firmware/gcpt_restore/` is LibCheckpointAlpha, a transitional version offering two
uses:

| Use | Build | Effect |
| --- | --- | --- |
| restore a checkpoint | `make clean && make` | on restore it overwrites the region from `0x80000000` for `sizeof(gcpt.bin)` |
| link a next-level bootloader | `make clean && make GCPT_PAYLOAD_PATH=/path/to/bbl.bin` | `gcpt.bin` can boot directly |

Link order: LibCheckpointAlpha can link riscv-pk or OpenSBI as the next-level
bootloader.

**Where it is loaded decides the behaviour**:

* loaded into **flash**, `gcpt.bin` either jumps to `0x80000000` or restores the
  checkpoint from the flash image, regardless of whether a payload is linked;
* loaded into **memory**, it jumps to `0x80100000` when a payload is linked and
  otherwise restores the checkpoint from the memory image.

The supported ISA string is `rv64gcbkhv`.

**Limitations** (matrix-relevant, and to be considered together):

* the checkpoint payload **contains neither the matrix register file nor the
  matrix CSRs**; only the `mstatus.MS` field is restored with `mstatus`;
* the sampling point of a matrix slice must therefore leave the matrix unit
  quiescent, and after restore the matrix configuration registers must not be
  assumed to match the sampling point.

For the full flow and its acceptance criteria see
[Checkpoints and Slicing](../verification/checkpoint.md#sec:debug-checkpoint).
