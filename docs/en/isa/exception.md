# Matrix Exceptions and Interrupts {#sec:xsai-exception}

This chapter covers the exception and interrupt behaviour the matrix extension
adds. For the general RISC-V exception mechanism see the baseline manual; here
only the differences between matrix and ordinary instructions. Read
[Instruction Set Extensions](instruction-set.md#sec:xsai-instruction-set) and
[Matrix CSRs](csr.md#sec:xsai-csr) first.

## Exception classes

**Only three kinds of matrix instruction raise exceptions:**

| Instruction class | Instructions | Possible exceptions |
| --- | --- | --- |
| Configuration | `msetcfg` / `mgetcfg` | illegal instruction |
| Matrix multiply-accumulate | `mmacc` | illegal instruction |
| Matrix memory access | matrix load / store | illegal instruction plus memory-access exceptions (page fault / access fault and similar) |

The following raise no exception at all in hardware: `msettilem/n/k` (including
their immediate forms), `mzero` and `mrelease`.

### When an instruction is illegal

**`msetcfg`**: `table_sel != 0`, or `type_code` not in the legal type table.

**`mmacc`**: illegal if any of the following holds —

- the destination or source matrix register number is illegal (`md`, `ms1`, `ms2`
  with the top bit out of range);
- the `mcfg` entry of some operand is unsupported;
- the type triple is not in the supported combination table;
- `mtilem` or `mtilen` exceeds `ROWNUM`, `mtilek` exceeds the element limit for the
  A type, or `mtilen` exceeds the element limit for the C type.

**Matrix memory access**: an illegal register number, or (in non-whole-register
form) a tile dimension over the limit. The whole-register form is exempt from the
tile dimension check. Memory-access exceptions come from the TLB (page fault,
guest page fault, access fault) and the PMP check.

### Misaligned exceptions are not raised today

Matrix memory access currently raises no misaligned exception: the address
alignment check is hard-wired to always pass and is marked as still to be
implemented. Do not design software on the assumption that a misaligned exception
will be raised.

## Exceptions are precise

Matrix exceptions satisfy the definition of precise exceptions:

1. the exception is written into the ROB entry along with the exception vector at
   write-back, not reported asynchronously;
2. the ROB triggers the trap and the redirect only when the faulting instruction
   becomes the head;
3. the faulting instruction itself is flushed and does not commit.

Before the trap every older instruction has committed and every younger one is
dropped, so `mepc` points exactly at the trapping instruction.

### How asynchronous execution stays isolated from exceptions

A matrix instruction's write-back is a zero-latency architectural event; the real
compute and memory side effects are sent to the matrix unit only after commit.
Three things follow:

- **a matrix instruction dropped by an exception or a flush never reaches the
  matrix unit** — it is discarded before commit;
- the write-back produced on the exception path explicitly blocks dispatch to the
  matrix unit;
- matrix operations issue in program order, so there is no "completion order
  differs from program order" ambiguity around exceptions.

In one line: **exceptions are never handled on the asynchronous side.** Every
exception decision is made in the core pipeline before commit; the asynchronous
side only executes operations that have committed and been checked.

### The matrix unit raises no exceptions internally

The matrix unit has no exception, interrupt or trap port at all. There is no error
or cancel channel between the core and the matrix unit.

### Replay

Only matrix load / store instructions replay, through a dedicated matrix
memory-access replay queue. Compute-type matrix instructions (`mmacc`, `mzero`,
`msettilex`, `mrelease`) do not replay.

### Serializing instructions

The following instructions are serializing and cannot be speculated past:

| Instruction | Behaviour |
| --- | --- |
| `msetcfg` | no speculation + blocks later issue + flushes the pipeline on commit |
| `minit` | no speculation + blocks later issue |
| `msyncregreset` | no speculation |
| `macquire` | no speculation + blocks later issue |
| `mfence` | no speculation + blocks later issue |

`msetcfg` triggers a pipeline redirect on commit, so a matrix configuration change
cannot be speculated past.

## Exception register contents

Matrix exceptions have no exception register field of their own and take the
general path:

- matrix write-back shares the same exception merging mechanism as CSR, load /
  store and vector write-back;
- `mepc`, `mcause` and `mtval` come entirely from the faulting instruction's own ROB
  entry; there is no matrix-specific field;
- TLB exceptions on matrix memory access reuse the general tval path.

The exception codes and register contents for matrix exceptions are therefore the
general RISC-V conventions plus the classes in the table above; no new exception
codes are defined for matrix.

Neither a matrix-specific `mtval` convention nor the exact conditions under which
matrix memory access raises `hardwareError` could be established from the current
RTL and material.

## Cleaning up state on the exception path

Matrix speculative state is cleaned up by the general mechanism, with no dedicated
rules:

| State | How it is cleaned up |
| --- | --- |
| matrix register renaming | same structure as integer / floating-point / vector: snapshot rollback or a walk that rebuilds from architectural state |
| MCFG (the result of `msetcfg`) | split into architectural and speculative state; the speculative part is rebuilt from architectural state after a redirect |
| illegal `msetcfg` | gated out; the architectural MCFG state is not updated |
| matrix memory-access queue | cancelled by ROB number with the pointer rolled back |

**There is no mechanism to "undo matrix side effects"**, for a simple reason:
instructions are dispatched only after commit, and uncommitted instructions produce
no side effects at all, so nothing needs undoing.

Anything uncommitted is dropped by the general mechanism; committed matrix side
effects cannot be undone and need no undoing.

## Interrupts

The overflow interrupt of the matrix performance counters, `LCOFIP`, uses interrupt
vector 13 (12 is taken by `SGEI`). It is raised only by HPM counter overflow and has
no dedicated line to the matrix unit, but matrix performance events are part of the
backend event pool, so matrix activity can trigger it indirectly. See
[Performance Monitoring](../hardware/pmu.md#sec:xsai-pmu).

Matrix state itself has no dedicated interrupt; the interrupt number table contains
no matrix entry.

## The `MS` state field

`mstatus.MS` sits at **bits `[26:25]`**, resets to `Off`, and is encoded as
`Off = 0`, `Initial = 1`, `Clean = 2`, `Dirty = 3`. `mstatus.SD` (bit 63) reads as 1
whenever `FS`, `VS` or `MS` is `Dirty`.

**There is no `msstatus` register**: matrix state exists only as `mstatus.MS` (and
`vsstatus.MS` in virtual mode); `sstatus` and `vsstatus` are alias paths.

### What `MS = Off` actually does

With `MS = Off`, accessing the six CSRs `mcsr`, `mxrm`, `msat`, `mfflags`, `mfrm`
and `msaten` raises an illegal-instruction exception.

There is also an **implementation divergence that is not yet closed**:

- the kernel patch implements a **first-use trap** (modelled on the equivalent
  vector mechanism): with `MS = Off`, executing a matrix instruction is expected to
  raise an illegal-instruction exception, and the handler then sets `MS` to
  `Initial` and retries;
- in the RTL the relevant decode-side checks **are currently all commented out**, so
  the current RTL does not raise an illegal instruction at decode time for this
  reason.

In other words: **the specification and the kernel expect this check, but the RTL
does not enable it yet.** Until the two agree, do not rely on "a matrix instruction
traps when `MS = Off`", and do not rely on the opposite either. Trust the actual
behaviour of the RTL revision you are using and re-confirm it across versions.

Another boundary: **in non-virtual mode `mstatus.MS` is not set to `Dirty`
automatically by hardware** — that logic is commented out in the RTL and only the
`vsstatus.MS` branch in virtual mode is live. In non-virtual mode software therefore
has to set it explicitly by writing `mstatus` / `sstatus`.

The instructions that dirty it are: `mla`, `mlc`, `mzero`, `mmacc` when they write
matrix; the read-only `msa` / `msc` do **not** dirty it.

### Toggling `MS` flushes the pipeline

When `MS` in `mstatus`, `sstatus` (alias) or `vsstatus` toggles between `Off` and
non-`Off`, the pipeline is flushed. That is the consistency point for switching
matrix context.

## Consistency with checkpoint / restore

**The current checkpoint / restore chain does not cover matrix state**, and this is
a known limitation that must be stated plainly:

| Item | Covered by checkpoint / restore |
| --- | --- |
| matrix register file (`tr0` – `tr3`, `acc0` – `acc3`) | **no** — the checkpoint payload has no such section |
| matrix CSRs (`mcsr` and the rest of the configuration bits) | **no** — the restore firmware's list contains no matrix CSR |
| the `mstatus.MS` bit | **yes** — restored along with `mstatus` |
| `mtilem` / `mtilen` / `mtilek` / `msync` | **no** |

Vector registers have a dedicated mirror section; the matrix register file has none
on either side. This is an asymmetry in the current implementation.

The practical requirements that follow:

- **the sampling point must leave the matrix unit quiescent.** An operation that
  committed but has not completed in the matrix unit would be lost on the restore
  side, producing architecturally invisible state divergence;
- use the `macquire` / `mrelease` / `msyncregreset` token mechanism when explicit
  synchronization is needed;
- after restoring, do not assume `mxrm` / `mfrm` / `msaten` / `msat` / `mfflags`
  match the sampling point;
- matrix slice analysis must record "matrix state is not restored from the
  checkpoint" as a known premise.

## Signal constants

The simulation signal constants used with checkpoints are defined in
`firmware/LibCheckpoint/include/gcpt_trap.h`:

| Constant | Value | Meaning |
| --- | --- | --- |
| `GOOD_TRAP` | `0x0` | clean exit, usually also the RTL simulation end point |
| `DISABLE_TIME_INTR` | `0x100` | disable the timer interrupt |
| `NOTIFY_PROFILER` | `0x101` | mark the start of the analysis region |
| `NOTIFY_PROFILE_EXIT` | `0x102` | mark the end of the analysis region |

These signals travel through `nemu_signal` using a custom instruction with
`opcode 0x6B`; they do not go through any interrupt or exception mechanism and are
a simulator-only side channel. See
[Checkpoints and Slicing](../verification/checkpoint.md#sec:debug-checkpoint).
