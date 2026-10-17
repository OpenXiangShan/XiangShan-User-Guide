# Checkpoints and Slicing {#sec:debug-checkpoint}

Running a full payload on the RTL is expensive, so slicing extracts the region of
interest and runs it alone. This chapter covers how to slice, how checkpoints are
produced, and which state is not part of them.

## Working up the ladder

Rule out software problems on the fast paths first, then move to the RTL:

```bash
make run-qemu                                  # fastest: software and boot path
make run-nemu                                  # next fastest, the golden-model layer
make ckpt                                      # build a checkpoint
make run-nemu PAYLOAD=<checkpoint.zstd>        # verify the checkpoint on NEMU
make run-emu  PAYLOAD=<checkpoint.zstd>        # finally run it on the RTL
```

## Marking the region of interest

The payload declares the region itself and the outer scripts pick the slicing flow
accordingly:

| Signal | Meaning |
| --- | --- |
| `DISABLE_TIME_INTR` | prepare for sampling: disable the timer interrupt |
| `NOTIFY_PROFILER` | enter the region of interest |
| `NOTIFY_PROFILE_EXIT` | leave the region of interest |
| `GOOD_TRAP` | clean exit |

The minimal skeleton emits one signal before and one after the region of interest.

Deriving checkpoints from the SimPoint clustering result requires
`make ckpt PHASE=checkpoint`, which is the step after `make profile` and
`make cluster`. A plain `make ckpt` runs `PHASE=all`, skips profiling and
clustering, and emits a single slice that does not follow the clustering.

## Checkpoints do not include matrix state

**The current checkpoint and restore chain does not cover matrix state.** Matrix
slice analysis must treat this as a premise:

| Item | Restored from the checkpoint |
| --- | --- |
| matrix register file (`tr0` – `tr3`, `acc0` – `acc3`) | **no**, there is no such section in the payload |
| matrix CSRs (`mcsr` and the remaining configuration bits) | **no**, the restore firmware's list contains no matrix CSR |
| the `mstatus.MS` bit | **yes**, restored along with `mstatus` |
| `mtilem` / `mtilen` / `mtilek` / `msync` | **no** |

For comparison, vector registers do have a dedicated mirror section. The matrix
register file has none on either side.

The practical requirements that follow:

* **the sampling point must leave the matrix unit quiescent.** An operation that
  committed but has not completed inside the matrix unit, if lost on the restore
  side, produces architecturally invisible state divergence — and the payload
  carries no "matrix unit idle" marker;
* use `macquire` / `mrelease` / `msyncregreset` when explicit synchronization is
  needed;
* after restoring, do not assume `mxrm` / `mfrm` / `msaten` / `msat` / `mfflags`
  match the sampling point.

For the full state semantics see
[Matrix Exceptions and Interrupts](../isa/exception.md#sec:xsai-exception).

## System-level scenarios

A large model can be packaged into `gcpt.bin` and reused between the functional
simulator and the RTL, avoiding repeated weight loading. Payloads that need a Linux
environment can use an image with an operating system, together with the checkpoint
restore flow.

## Two gotchas

* QEMU and the RTL assume different `timebase-frequency` values, so a DTB cannot be
  carried between them — see [Troubleshooting](troubleshooting.md#sec:debug-troubleshooting);
* finer slices iterate faster, but confirm the cache state at the slice start
  matches the full run, or the performance conclusion shifts.
