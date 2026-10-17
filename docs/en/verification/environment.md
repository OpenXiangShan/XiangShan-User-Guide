# Environment Setup {#sec:sim-environment}

This chapter brings the simulation environment up: what `xsai-env` consists of, what the first-time setup does, and how to choose among the simulation flows.

## Overview of xsai-env

`xsai-env` is the integrated development workspace for XSAI. The top-level
`Makefile` drives the build; the RTL project lives in `XSAI/`, the functional
simulators in `NEMU/` and `QEMU/`, and firmware/rootfs in `firmware/`.

```bash
git clone <xsai-env> ~/xsai-env
cd ~/xsai-env
```

## First-time setup

```bash
make deps         # install system dependencies (requires sudo)
make init         # initialize submodules and environment
make init-force   # recommended before the first heavy build
source env.sh     # or: direnv allow
```

Notes:

* `RISCV`, `RISCV_SYSROOT` and `QEMU_LD_PREFIX` are auto-detected; put machine
  specific overrides in `.envrc.local`.
* The top level intentionally does not export `CROSS_COMPILE`; firmware and
  software flows set their own toolchain prefixes.

## Generated directories

`local/`, `build/`, `log/` and `firmware/checkpoints/` are generated artifacts
and are not tracked.

## Common targets

| Target | Purpose |
| --- | --- |
| `make xsai` | Build the Verilator emulator `XSAI/build/emu` |
| `make run-emu` | Run Verilator simulation (see [Verilator Simulation](verilator.md#sec:sim-verilator)) |
| `make run-nemu` | Run NEMU |
| `make run-qemu` | Run QEMU (the workloads here need no `MODEL_IMG`) |
| `make firmware` | Build firmware and rootfs |
| `make test-smoke` | Fast environment sanity check |
| `make test` | Full environment sanity check (slower) |

Run `make help` for the complete list.

## Sanity checks

1. Start with `make help` and `make -n <target>` to confirm the command path.
   Note that `run-*` targets contain recursive `$(MAKE)`, so `-n` is not
   guaranteed to be side-effect free.
2. Use `make test-smoke` for fast validation.
3. Avoid full RTL rebuilds unless required.

## Compute resources

RTL simulation is CPU heavy. Set parallelism from the CPU and memory available on
your own machine, and avoid disturbing other work on the same host.

## See also

* Simulation: [Verilator](verilator.md#sec:sim-verilator), [VCS](vcs.md#sec:sim-vcs)
* Troubleshooting: [Troubleshooting](troubleshooting.md#sec:debug-troubleshooting)
