# Matrix Debug Support {#sec:xsai-debug}

XSAI adds no dedicated debug hardware for the matrix extension; matrix instructions
use the Kunminghu V2R2 debug mechanisms (see the "Debug" chapter of the baseline
manual). This chapter covers how matrix instructions differ from ordinary ones
while debugging, and how far differential verification and checkpoint support
matrix state.

## Commit and completion

To understand matrix debugging, first separate two moments in the life of a matrix
instruction:

| Moment | What happens |
| --- | --- |
| Commit | The instruction passes every check in the core pipeline and commits in order. After this it can no longer raise an exception |
| Completion | The matrix unit actually finishes the compute or the memory access. Completion is later than commit and its time is not deterministic |

The core hands the operation to the matrix unit only after commit, and the matrix
unit executes asynchronously. So when the processor stops at some instruction, the
matrix unit may still be executing operations that were committed earlier. That is
normal behaviour, not an error.

## Breakpoints and single-stepping

Breakpoints and single-stepping behave the same for matrix instructions as for
ordinary ones; no special handling is needed. The reason is that every exception
decision for a matrix instruction is made before commit, through the same
mechanism as ordinary instructions.

## Reading the matrix registers

Because the matrix unit executes asynchronously, the instruction a breakpoint stops
at does not tell you that earlier matrix operations have finished. To see the
result of a particular operation, first wait for it with `macquire`, then read the
matrix registers. Do not infer from the breakpoint position that the result has
been written.

## Error reporting

| Error source | How it shows up |
| --- | --- |
| Address translation errors on matrix memory access (page fault / access fault) | Raised in the core pipeline as precise exceptions; debuggable as usual |
| Errors during execution inside the matrix unit | The matrix unit raises no exception or interrupt and reports nothing back to the core |

A wrong result therefore raises no exception at all. When tracking one down, rule
out problems in the program first: reading matrix register regions that were never
written, missing synchronization, out-of-bounds access.

## Differential verification {#sec:matrix-difftest}

Differential verification compares RTL state against the reference model item by
item after each instruction commits. For the matrix extension the comparison covers:

* matrix CSRs: `mcsr`, `mxrm`, `msat`, `mfflags`, `mfrm`, `msaten`, `tlenb`,
  `trlenb`, `alenb`, `mtilem`, `mtilen`, `mtilek`, `msync`;
* the configuration registers `mcfg0` – `mcfg7`.

The reference model can run on a CPU or a GPU. See
[Differential Verification](../verification/difftest.md#sec:debug-difftest) for how
to use it.

## Checkpoints

**A checkpoint does not save the matrix registers or the matrix CSRs.** After
restoring from a checkpoint the matrix state is not recreated, so a sampling point
must be chosen where no matrix operation is in flight and nothing later depends on
the earlier contents of the matrix registers.

Sampling regions in a payload can be marked with `DISABLE_TIME_INTR`,
`NOTIFY_PROFILER` and `NOTIFY_PROFILE_EXIT`. The full slicing and restore flow is in
[Checkpoints and Slicing](../verification/checkpoint.md#sec:debug-checkpoint).
