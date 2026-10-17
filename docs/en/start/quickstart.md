# Getting Started in 15 Minutes {#sec:get-started}

This chapter brings the `xsai-env` environment up on a Linux workstation and runs
a first payload. You need a RISC-V cross toolchain and `direnv` beforehand, for
example on Ubuntu / Debian:

```bash
sudo apt install gcc-riscv64-linux-gnu g++-riscv64-linux-gnu gfortran-riscv64-linux-gnu binutils-riscv64-linux-gnu
```

## 1. Get the workbench

`xsai-env` is the integration workbench for XSAI software and hardware work: it
puts the RTL, simulators, firmware, rootfs, toolchain and test flows under one
top-level `Makefile`. Issue everyday commands from the repository root rather
than looking inside each submodule.

```bash
git clone https://github.com/OpenXiangShan/xsai-env
cd xsai-env
sudo make deps        # install system dependencies (Ubuntu / Debian)
direnv allow
make init-force
```

Initialisation pulls all submodules recursively and sets `XS_PROJECT_ROOT`,
`NOOP_HOME` (the RTL), `NEMU_HOME`, `QEMU_HOME` and `AM_HOME`.

**Some submodules cannot be cloned anonymously yet**: repositories such as
`llvm-project-ame` and `riscv-matrix-extension-spec` are still being prepared for
open sourcing. A message like the one below is expected and can be ignored — the
software and simulation flows are unaffected:

```text
Skipping submodule 'NutShell'
Cloning into 'riscv-matrix-spec'...
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed for 'https://github.com/OurCompArchGroup/riscv-matrix-extension-spec.git/'
Failed to clone 'riscv-matrix-spec'
make: *** [Makefile:180: init-force] Error
```

The compiler does not have to be built from source; use the prebuilt package, see
[Obtaining the AME LLVM](../sdk/layout.md#sec:sdk-layout):

```bash
wget https://github.com/OurCompArchGroup/llvm-release/releases/download/20260708/llvm-20260708-proposal-14.tar.gz
tar -xf llvm-20260708-proposal-14.tar.gz
```

Machine-specific overrides (toolchain paths, LLVM path, proxies and so on) live in
`.envrc.local`, which is not tracked by version control. Copy the template and
adjust it for your machine:

```bash
cp .envrc.local.example .envrc.local
```

## 2. Run the self-check first

```bash
make test-smoke      # checks the scripts and Makefile entry points
```

Only continue once the self-check passes. `make test` is the full environment
self-check (it builds NEMU and NutShell and runs microbench) and is much slower
than `test-smoke`, so run it when you want to confirm the whole chain.

## 3. Build what you need

There is no need to build everything; pick by goal:

```bash
make llvm      # local AME LLVM toolchain (a prebuilt package also works, see above)
make nemu      # NEMU
make qemu      # QEMU
make xsai      # same as make emu-verilator: build the Verilator RTL simulation
make firmware  # chains the Linux kernel, riscv-rootfs, OpenSBI and so on
```

The Verilator simulation from `make xsai` serves functional re-verification before
submitting; for pure software iteration prefer QEMU or NEMU.

## 4. Run your first payload

Bring the software up on the fast paths first, then move to the slow ones:

```bash
make run-qemu                                  # fastest: software and boot path
make run-nemu                                  # next fastest, and the golden-model layer
make run-emu  PAYLOAD=<payload.bin>            # RTL simulation
```

`make run-emu` requires an explicit `PAYLOAD`. The simulation criteria strings
include `HIT GOOD TRAP` (clean exit), `EXIT at pc`, `EXCEEDING CYCLE` and
`ABORT`.

To build a checkpoint for slice-based analysis:

```bash
make run-qemu
make run-nemu
make ckpt                                      # creates a checkpoint
make run-nemu PAYLOAD=<checkpoint.zstd>
make run-emu  PAYLOAD=<checkpoint.zstd>
```

To derive checkpoints from the SimPoint clustering result you must use
`make ckpt PHASE=checkpoint`; a plain `make ckpt` runs `PHASE=all`, which skips
profiling and clustering and emits a single slice. See
[Checkpoints and Slicing](../verification/checkpoint.md#sec:debug-checkpoint).

## 5. Confirm the environment works

| Check | Expectation |
| --- | --- |
| Initialisation | all submodules checked out, environment variables set |
| `make test-smoke` | returns 0 |
| first QEMU payload | exits cleanly |
| first RTL payload | `HIT GOOD TRAP` |

The environment is up at this point. Pick a path by goal:

* adapt operators or frameworks → [Framework Adaptation Path](path-framework.md#sec:path-framework)
* do performance analysis → [Performance Analysis Path](path-perf.md#sec:path-perf)
* understand how software and hardware work together → [Software and Hardware Co-design](../optimization/co-design.md#sec:co-design)
* for directories and build targets → [SDK Composition and Directory Layout](../sdk/layout.md#sec:sdk-layout) and [Build System and make Targets](../sdk/build.md#sec:sdk-build)

## Common pitfalls

* Do not look for commands inside submodules; the everyday entry points all live
  in the top-level `Makefile`.
* Some submodules are still being prepared for open sourcing; a failed clone does
  not mean your configuration is wrong.
* The timebase is not one value across flows: RTL uses the core-generated DTS
  (1 MHz), while `firmware/nemu_board/dts/build/xiangshan_ai.dtb` comes from the
  firmware flow's DTSGen (10 MHz by default). A DTB must not be moved between the
  two flows; see [Troubleshooting](../verification/troubleshooting.md#sec:debug-troubleshooting).
* RTL simulation is a heavy load. Set parallelism from the CPU and memory
  available on your own machine, and avoid disturbing other work on the same host.
