# SDK Layout and Directory Structure {#sec:sdk-layout}

`xsai-env` puts the RTL, simulators, firmware, rootfs, toolchain and verification
flows under one top-level `Makefile`. This chapter covers where each part lives,
what it is responsible for, and the environment variables and toolchain it needs.
For first-time setup see [Getting Started](../start/quickstart.md#sec:get-started);
for build targets see [Build System and make Targets](build.md#sec:sdk-build).

![SDK components](../figs/sdk-layout.svg "SDK components")

## Three ground rules

* **The repository root is the entry point.** Setup, build and run commands are all
  issued from the root; do not run them inside individual submodules.
* **This is not a flat repository.** Each subsystem keeps its own sources,
  toolchain assumptions and verification path, with its version pinned as a
  submodule — see [Submodules and Version Management](submodules.md#sec:sdk-submodules).
* **Generated artifacts are not committed.** `local/`, `build/`, `log/` and
  `firmware/checkpoints/` are output directories.

## Directory responsibilities

| Directory | Contents and responsibility |
| --- | --- |
| `Makefile`, `scripts/`, `mk/`, `env.sh`, `.envrc*`, `docs/` | top-level orchestration, shared environment, repository conventions, integration docs |
| `XSAI/` | RTL sources, generated Verilog, emulator build, DUT-side difftest; the matrix core lives in `XSAI/CUTE/` |
| `NEMU/` | ISA reference model, the reference `.so` for difftest, profiling and checkpoint support |
| `qemu/` | Linux and user-mode simulation, QEMU machine support, the profiling plugin used by the checkpoint flow |
| `firmware/` | Linux, rootfs, OpenSBI, DTB, GCPT boot payloads and the board bring-up flow |
| `nexus-am/` | bare-metal runtime and libraries, the bare-metal programs and tests used by NEMU and RTL flows |
| `llvm-project-ame/` | AME-enabled LLVM/Clang, disassembly and low-level code generation |
| `DSL/` | high-level compiler front ends such as Triton, TileLang and TVM |
| `software/` | inference frameworks and workloads, see below |
| `firmware/riscv-rootfs/apps/`, `nexus-am/apps/` | Linux-side and bare-metal applications, including benchmarks and demos |
| `DRAMsim3/` | DRAM simulator |
| `NutShell/` | reference processor used by some verification flows |
| `riscv-matrix-spec/` | the matrix extension specification |
| `tests/`, `tools/` | top-level coordination points and developer tooling, including TMA-toolkit, packaging and reporting scripts |

`DSL/`, `software/`, `tests/` and `tools/` are top-level namespaces. How much they
contain today says nothing about how important they are — much of the real testing
and tooling still lives in the component repositories.

## Inference frameworks

MNN, ncnn, llama.cpp and `tools/TMA-toolkit` are top-level submodules whose versions
are pinned by the gitlink and `VERSIONS`:

| Component | Path | Where the XSAI port lives |
| --- | --- | --- |
| MNN | `software/MNN` | `source/backend/cpu/ame/`, `ame_xsa.c`, `Int8GemmKernelXSAI.cpp` |
| ncnn | `software/ncnn` | `src/layer/riscv/convolution_bf16_xsai.h`, `convolution_int8_xsai.h` |
| llama.cpp | `software/llama.cpp` | the ggml path, see [Kernel Libraries and Inference Frameworks](../software/frameworks.md#sec:sw-frameworks) |
| TMA-toolkit | `tools/TMA-toolkit` | used with [Performance Monitoring](../hardware/pmu.md#sec:xsai-pmu) |

`make software-init` initialises these three framework submodules plus
`firmware/riscv-rootfs`; `make test-ai-software` runs the software-stack verification.

## Environment variables

Both `env.sh` and `.envrc.base` fill the shared environment through
`scripts/env-common.sh`:

| Variable | Meaning |
| --- | --- |
| `XS_PROJECT_ROOT` | repository root |
| `NEMU_HOME` / `QEMU_HOME` | `./NEMU` / `./qemu` |
| `AM_HOME` / `NOOP_HOME` | `./nexus-am` / `./XSAI` |
| `LLVM_HOME` | defaults to `./local/llvm` |
| `RISCV_LINUX_HOME` / `RISCV_ROOTFS_HOME` | `./firmware/riscv-linux` / `./firmware/riscv-rootfs` |
| `RISCV` | resolved from an explicit variable, a known shared install, `/opt/riscv`, or `PATH`; on success `$RISCV/bin` is prepended to `PATH` |
| `RISCV_SYSROOT` / `QEMU_LD_PREFIX` | the first is derived from the selected toolchain; the second defaults to the detected RISC-V sysroot |
| `CROSS_COMPILE` | **deliberately not exported at the top level**; the firmware and software flows set their own prefix |

Machine-specific overrides go in `.envrc.local` (copy `.envrc.local.example`, it is
not tracked). For installing direnv see <https://direnv.net/docs/installation.html>.

The `run-user` flow needs `QEMU_LD_PREFIX` set explicitly, otherwise it reports
`Could not open '/lib/ld-linux-riscv64-lp64d.so.1'`.

During initialisation, submodules are taken from the local cache
`local/git-cache/submodules`, so later initialisations and git worktrees reuse the
same objects instead of cloning everything again. Set `GIT_SUBMODULE_CACHE` to share
across checkouts, and `GIT_SUBMODULE_SOURCE_ROOTS` to seed a missing cache from
existing checkouts.

## Toolchain requirements

| Item | Requirement |
| --- | --- |
| Cross compiler | `riscv64-unknown-linux-gnu-gcc` on `PATH`, with `RISCV` pointing at the toolchain root |
| Firmware self-check | `make -C firmware check-env`, which checks the compiler exists and prints its version |
| Full environment self-check | `make test`, which needs a compiler supporting `-march=rv64gcbkvh`, otherwise it reports `No supported RISC-V compiler found!` and exits |
| System dependencies | `make deps` (Ubuntu / Debian, needs sudo) |

The QEMU build clears the host-side cross-compilation variables before `configure`
to avoid contamination.

### Obtaining the AME LLVM

The AME matrix instructions need an LLVM/Clang with the extension support. **Prefer
the prebuilt package**; there is no need to build from source:

| Item | Notes |
| --- | --- |
| Download | <https://github.com/OurCompArchGroup/llvm-release/tags> |
| Artifact | each tag carries an `llvm-<date>[-proposal-N].tar.gz`, about 1.2 GB, usable once unpacked |
| Current tags | `20260708` (`llvm-20260708-proposal-14.tar.gz`) and `20260528` (`llvm-20260528.tar.gz`) |
| Building from source | `make llvm`, output in `local/llvm`; the sources are in `llvm-project-ame/` |

`make llvm` first probes the host-side RISC-V cross compiler (in the order `RISCV`,
`RISCV_TOOLCHAIN_PREFIX`, `riscv64-linux-gnu-`) and reports an error asking for
`gcc-riscv64-linux-gnu` if none is found.
