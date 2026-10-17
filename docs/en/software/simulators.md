# Functional Simulators {#sec:sw-simulators}

Functional simulators run software end to end without RTL and provide
operator-level and network-level differential verification.

## NEMU

* The matrix extension has been merged upstream and supports matrix instructions
  and matrix register state;
* When it serves as the reference model for differential verification, it
  compares matrix registers by hash (see
  [Differential Verification](../verification/difftest.md#sec:debug-difftest));
* It comes with its own performance statistics: with AVX-512 enabled it speeds up
  markedly over interpreted execution; the exact factor depends on the host and the
  workload, so measure it on your own machine.

## QEMU

* User mode (`qemu-riscv64`): runs operator-level tests and the single-operator
  tests shipped with frameworks, and iterates fastest;
* System mode: runs the full boot flow and Linux user programs;
* Several people keep patching the same QEMU branch (`9.0.0_matrix-v0.12` as
  recorded in `.gitmodules`), so
  remember to synchronize before merging.

**What QEMU covers on the matrix path**: QEMU models arithmetic semantics and
does not cover hardware geometry constraints (tile spec, physically contiguous
pool, row addressing), so passing in QEMU does not imply that the result is
correct on the board. QEMU conclusions must be labelled "arithmetic criteria
only", and only re-verification on the board is authoritative.

## gem5

* Used for design exploration and performance evaluation; quote a specific
  comparison report for any deviation figure;
* Suitable for architecture parameter sweeps, not for deciding functional
  correctness.

## Division of labour with RTL simulation

![Verification ladder](../figs/verify-ladder.svg "Verification ladder")

| Tool | Speed | Scope of criteria | Use case |
| --- | --- | --- | --- |
| QEMU (user mode) | Fastest | Arithmetic only | Single operators, fast network-level iteration |
| NEMU | Fast | Instruction semantics + register state | Reference model for differential verification |
| gem5 | Medium | Performance magnitude | Architecture parameter exploration |
| Verilator / VCS | Slow | Full functionality | Re-verification before submission, waveform debugging |

## Choosing a backend

### Matching backend to configuration

| Condition | Choice | Reason |
| --- | --- | --- |
| ZhuJiang LLC | **Verilator** | the current GSIM does not support the stateful `GENERIC_RAM_*` and `ResetGenInnerS2` external modules that ZhuJiang needs |
| OpenLLC | GSIM or Verilator | either works |

**Do not substitute stateless stubs for missing modules and then draw
correctness or performance conclusions.**

### Performance guidance

* **PGO is worth enabling**: both Verilator and GSIM support
  `-O3 -fprofile-use`. PGO does not replace `-O3`, it adds to it; training on the
  same workload gives the best result, and a different workload needs retraining;
* **the Verilator thread count must be measured per configuration**: more threads
  is not better. Beyond the count of physical performance cores, slower workers
  stretch each synchronisation and barrier wait and the run gets slower. **The
  optimum varies by configuration and does not extrapolate**, so try 2 / 4 / 6 / 8
  on the configuration you actually use;
* **build resources**: both backends need substantial build time and memory, and
  GSIM's peak memory is markedly higher than Verilator's, so factor the build
  machine and its cache into the choice.

### Computing simulation frequency

Simulation frequency is `guest cycles / host time`. Different configurations have
different startup and shutdown paths and therefore different total cycles, so
**compare frequency across configurations rather than total wall time**. Run
simulations serially to avoid interference between them.

## Version correspondence

| Component | Version / note |
| --- | --- |
| NEMU | submodule pinned at `v2026.07.r12` (see [Submodules and Version Management](../sdk/submodules.md#sec:sdk-submodules)) |
| QEMU | branch `9.0.0_matrix-v0.12` |
| GSIM | measured at revision `50b371c`; does not yet support the stateful external modules ZhuJiang needs |
| Verilator / VCS | see [Verilator Simulation](../verification/verilator.md#sec:sim-verilator) and [VCS Simulation and Test Framework](../verification/vcs.md#sec:sim-vcs) |
