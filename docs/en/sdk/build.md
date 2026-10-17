# Build System and make Targets {#sec:sdk-build}

The top-level `Makefile` orchestrates every build and simulation path, and day-to-day commands are issued from the repository root. This page covers the user-facing entry targets, the targets that `make help` does not list, the firmware sub-targets, and the validation ladder.

`make help` prints the user-facing entry targets and their purposes, but **it does not cover every target**: `qemu`, `firmware`, `run-nemu`, `run-emu`, `run-user`, `uniform`, `emu-verilator`, `emu-gsim` and `smoke` exist in the `Makefile` without being listed. The tables below group targets by purpose and include them all.

## Setup and checks

| Target | Purpose |
| --- | --- |
| `make deps` | Install system dependencies (requires sudo) |
| `make init` / `make init-force` | Initialise submodules and environment / force initialise submodules to avoid empty folders; slow on a fresh checkout |
| `make test-smoke` / `make test` | Run fast non-build smoke checks / test the environment (`./scripts/env-test.sh`, heavier) |

## Toolchain and simulators

| Target | Purpose |
| --- | --- |
| `make llvm` | Build the custom LLVM toolchain (uses the system compiler); the product goes to `local/llvm` |
| `make gsim` | Install the latest gsim binary to `local/bin` |
| `make nemu` | Build the NEMU simulator |
| `make docker-nemu-image` / `make nemu-matrix-ref-so-docker` | Build the NEMU Docker image from `centos.Dockerfile` / build the `riscv64-matrix-xs-ref` shared library in Docker |
| `make xsai` | Build XSAI RTL simulation (Verilator); note `XSAI_SIM_RTC_CLOCK_DIV=$(XSAI_SIM_RTC_CLOCK_DIV) (even, >= 2)` |
| `make test-matrix` | Run matrix simple test |
| `make qemu` | Build `qemu-system-riscv64` and `qemu-riscv64` (`target-list=riscv64-softmmu,riscv64-linux-user`, `--enable-zstd --enable-plugins`) |
| `make emu-verilator` / `make emu-gsim` | The actual implementation target behind `make xsai` (`xsai: emu-verilator`) / build the gsim-based XSAI simulation path |

`make gsim` pulls the latest upstream release, so **it is not a deterministic bootstrap step**; use it only when a task explicitly needs gsim. One known gap on the gsim path: gsim `50b371c` does not implement the stateful ZhuJiang `GENERIC_RAM_*` and `ResetGenInnerS2` external modules, so `MinimalMatrixConfig` + `XSAI_SIM_LLC=ZhuJiang` **fails at link time** after generating C++; use OpenLLC until gsim has external module models, and **do not substitute a stateless stub**.

## Firmware and end-to-end runs

| Target | Purpose |
| --- | --- |
| `make firmware` | Build rootfs, Linux, DTB, QEMU/NEMU GCPT payloads and the restore-only GCPT; implemented as `$(MAKE) -C firmware all $(_LLAMA_EXTRA)`, and the firmware integration entry behind `make run-qemu` / `make run-nemu` |
| `make run-qemu` | Run QEMU simulation with a GCPT payload (optional: a non-empty `MODEL_IMG` mounts as `/dev/vda` through virtio-blk; the workloads here do not need it) |
| `make run-nemu` | Run the GCPT payload on NEMU |
| `make run-emu` | RTL (Verilator/GSIM) simulation entry: `EMU_BUILD_DIR=... EMU_BIN=... ./scripts/run-emu.sh ... $(PAYLOAD)`; see [Verilator Simulation](../verification/verilator.md#sec:sim-verilator) |
| `make run-emu-debug` | RTL debug: FST wave + ChiselDB (`FORK=1` skips the wave); typical arguments `PAYLOAD=<p> DIFF=1 WAVE_BEGIN=50000 WAVE_END=180000` |
| `make run-user` | Exists, but **it is currently a local `llama.cpp` convenience target with a hard-coded model path and must not be treated as a general validation entry** |

`make run-qemu` / `make run-nemu` automatically build any missing QEMU, DTB or GCPT binary when needed (dependency targets `_ensure_qemu_payload`, `_ensure_nemu_payload`, `_ensure_qemu`, `_ensure_qemu_dtb`). Be careful with `make -n` on orchestration or `run-*` targets: a recursive `$(MAKE)` inside a recipe may still execute, so read the `Makefile` first when a side-effect-free dry run is required.

## firmware sub-targets

| Sub-target | Purpose |
| --- | --- |
| `make -C firmware all` / `check-env` | Build everything (default) / verify environment setup; `SHOW_FIRMWARE_BUILD_LOGS=1` streams the main build logs |
| `make -C firmware download-linux` / `setup-submodules` / `init-force` | Download Linux kernel / initialise git submodules / force initialise firmware submodules |
| `make -C firmware build-rootfs` | Build root filesystem; knobs `SHOW_ROOTFS_BUILD_LOG=1`, `ROOTFS_MAKE_JOBS`, `XSAI_INIT_MODE`, `XSAI_WORKLOAD`, `XSAI_AUTO_EXIT`, `XSAI_DROP_SHELL` |
| `make -C firmware build-linux` | Build Linux kernel; knobs `SHOW_LINUX_BUILD_LOG=1`, `LINUX_MAKE_JOBS`, `FORCE_LINUX_CONFIG=1`, `INITRAMFS_SOURCE`, `INITRAMFS_COMMON_SOURCES` |
| `make -C firmware build-dtb` / `build-dtb-std` / `build-dtb-xsai` | Build the XSAI device tree blob (default) / build the standard XiangShan DTB and the XSAI-specific DTB; optional knobs for `build-dtb-std` are `DIRECT_MAP_MEM_START`, `DIRECT_MAP_MEM_SIZE` and `STD_TIMEBASE_FREQ`, and `XSAI_TIMEBASE_FREQ` for `build-dtb-xsai` |
| `make -C firmware build-opensbi` / `build-opensbi-nemu` | Build the QEMU OpenSBI firmware payload (runtime DTB) / the NEMU OpenSBI firmware payload (embedded DTB) |
| `make -C firmware build-gcpt` / `build-gcpt-nemu` | Build the QEMU bootable GCPT / the NEMU bootable GCPT linked with the payload |
| `make -C firmware build-gcpt-restore` / `build-gcpt-clean` | Build the restore-only GCPT binary for checkpoint resume / force a clean rebuild of GCPT (for example after editing `csr.h`) |
| `make -C firmware clean` / `distclean` | Clean build products / deep clean: remove downloads and deinit submodules |

`firmware/Makefile all` runs `build-rootfs` → `build-linux` → `build-dtb` → `build-gcpt-qemu` → `build-gcpt-nemu` → `build-gcpt-restore` in that order, then prints the product paths for the Linux Image, DTB, QEMU and NEMU OpenSBI payloads, QEMU and NEMU GCPT, and GCPT Restore.

## SimPoint and checkpoint

| Target | Purpose |
| --- | --- |
| `make simpoint` | Build the SimPoint clustering binary |
| `make profile` | Phase 1: QEMU profiling (BBV collection) |
| `make cluster` | Phase 2: SimPoint clustering |
| `make ckpt` / `make ckpt PHASE=profile\|cluster\|checkpoint` | the default `PHASE=all` writes **one slice** and ignores SimPoint results; use an explicit `PHASE=checkpoint` to checkpoint from a clustering / run a single phase |
| `make ckpt-nosimpoint` | One-slice checkpoint flow without SimPoint clustering |

`MODEL_IMG` is **optional** here (`Makefile` defaults it to empty and `checkpoint.sh` accepts empty; only a non-empty value is attached as `/dev/vda` through virtio-blk with `format=raw`). **None of the workloads this manual covers needs it**: the rootfs is embedded as an initramfs and workload binaries are built into the image, so no external disk image is involved. The repository also provides no target that produces one, and the `make help` wording that calls it required does not match the code. The available knobs are `WORKLOAD_NAME CPT_INTERVAL PROFILING_INTERVALS SIMPOINT_MAX_K MEMORY SMP CHECKPOINT_CONFIG MODEL_IMG CKPT_ARGS`. The `make uniform` target exists (dump every N instructions across the whole execution, no SimPoint needed) but **is not listed in `make help`**; the usage string of `scripts/checkpoint.sh` includes the `uniform` mode.

Parameter defaults differ between entry points, so **do not mix them**:

| Entry | `CHECKPOINT_CONFIG` | `WORKLOAD_NAME` | `CPT_INTERVAL` | `PROFILING_INTERVALS` | `SIMPOINT_MAX_K` | `SMP` |
| --- | --- | --- | --- | --- | --- | --- |
| Top-level `make ckpt` (takes the `Makefile` SimPoint sampling defaults) | `build` | `app` | `100000` | `CPT_INTERVAL` | `30` | `1` |
| Running `scripts/checkpoint.sh` directly (the faster one-slice defaults inside the script) | `build` | `app` | `100` | `CPT_INTERVAL` | `10` | `1` |

Two modes are common: Fast single-slice uses `no_simpoint + do_checkpoint` with typical parameters `CPT_INTERVAL=100`, usually producing one checkpoint to skip firmware/OS boot and enter the target region quickly; SimPoint sampling uses `do_profile + do_cluster + do_checkpoint` with typical parameters `CPT_INTERVAL=100000` and `SIMPOINT_MAX_K=30`, producing several representative slices that can be replayed in parallel on NEMU or the RTL emu for hardware-side performance studies; the stricter phased flow is `make profile` → `make cluster` → `make ckpt PHASE=checkpoint`. The checkpoint payload path depends on the generated SimPoint/checkpoint index as well as `WORKLOAD_NAME` and `CHECKPOINT_CONFIG`; `firmware/checkpoints/build/app/1/_1_1.zstd` is only **a common example, not a general constant**. The full flow is in [Checkpoint and Slicing](../verification/checkpoint.md#sec:debug-checkpoint).

## Packaging, analysis and maintenance

| Target | Purpose |
| --- | --- |
| `make ccdb` / `make ccdb-append` | Rebuild the unified `compile_commands.json` via bear / append a build to it and deduplicate |
| `make update` / `make versions` | Update submodules to the latest / regenerate the `VERSIONS` file from the current submodule state |
| `make clean` / `make distclean` | Clean build products (NEMU, AM, firmware, `build/`) / deep clean including LLVM, the qemu build and firmware submodules |

## Validation ladder

The validation order narrows from fastest to slowest: rule out software problems on the fastest simulator first, then move to the golden model, and only then to RTL.

```bash
make run-qemu
make run-nemu
make ckpt
make run-nemu PAYLOAD=<checkpoint.zstd>
make run-emu PAYLOAD=<checkpoint.zstd>
```

| Layer | Role and relative speed |
| --- | --- |
| QEMU | About an order of magnitude faster than NEMU for bring-up, and easier for software bug analysis |
| NEMU | About two orders of magnitude faster than RTL, and the **preferred golden-model gate** before touching RTL; do not assume that QEMU validation covers NEMU semantics |
| RTL | Use it after the software path has narrowed; it mainly covers real performance behaviour and workload-level validation |

### Fast and integration validation per workstream

| Workstream | Fast validation | Integration validation |
| --- | --- | --- |
| RTL / `XSAI/` | `make xsai`, `make run-emu-debug PAYLOAD=...` | A targeted RTL workload with difftest |
| `NEMU/` and `qemu/` | `make nemu`, `make qemu` | Run the target workload or the reference-mode flow, `make run-qemu` |
| firmware / `nexus-am/` / compiler | `make -C firmware build-dtb`, local app/rootfs and app/test builds, targeted app rebuilds, `llvm-objdump` | `make firmware`, `make run-qemu`, `make test-matrix` or a targeted AM run, downstream software/runtime execution (see [Compiler and Operator DSL](../software/compiler.md#sec:sw-compiler)) |
| checkpoint flow | Script sanity and target existence | `make simpoint`, `make profile`, `make cluster`, `make ckpt` |

### Workload-side `nemu_signal(...)` markers

Slicing needs both layers in place: the outer orchestration parameters (interval and clustering knobs) and the workload-side markers. The signal values are defined in `firmware/riscv-rootfs/apps/hello_xsai/ame.h`:

| Signal | Value | Meaning |
| --- | --- | --- |
| `DISABLE_TIME_INTR` | `0x100` | Prepare for sampling; disable timer interrupts |
| `NOTIFY_PROFILER` | `0x101` | Start profiling the region of interest (ROI) |
| `NOTIFY_PROFILE_EXIT` | `0x102` | End ROI profiling |
| `GOOD_TRAP` | `0x0` | Clean termination |

Placement rules: setup goes before `NOTIFY_PROFILER` where possible, the real hot kernel or representative workload goes between `NOTIFY_PROFILER` and `NOTIFY_PROFILE_EXIT`, and cleanup goes after `NOTIFY_PROFILE_EXIT` where possible; keep the ROI stable and reproducible, preferring one clean ROI over several noisy small ones. **`DISABLE_TIME_INTR` changes runtime behaviour**: software that depends on timer interrupts or normal multi-threaded scheduling is not a good candidate for direct profiling after that point.

### RTL difftest and the incremental build-cache boundary

* RTL difftest path: the `NEMU/` reference `.so` → `XSAI/difftest` → `XSAI/build/emu`; when a difftest mismatch appears, the root cause may lie in the RTL, in NEMU semantics, in payload assumptions or in the test image itself. The incremental RTL build cache decides on two keys: `rtl-key` decides whether Chisel/CIRCT elaboration must run at all, and `emu-key` decides whether a full set of RTL+Verilator products can be reused directly; build time varies widely with machine and configuration, so measure a baseline on your own target machine.
* **Dependency-graph boundary**: the Verilator dependency list has no hierarchy-aware parent/child relation, so after editing a split-out child file (for example `rtl/CMatrixReg.sv`) an ordinary flat `make` may return success while the `emu` artifact was never updated. Force a rebuild for the affected scope rather than trusting `make`'s return code.

### Three-layer validation for the AI software stack

Treat every operator change as three layers, with end-to-end performance as the final gate:

| Layer | Means | Example (verbatim) |
| --- | --- | --- |
| Operator correctness | `test-backend-ops test` inside the rootfs, with backend `RISCV_AME` | `/bin/test-backend-ops test -o MUL_MAT --buft RISCV_AME -p 'type_a=q8_0,type_b=f32,m=(288\|768),n=128,k=(288\|768),bs=[1,1],nr=[1,1]'` |
| Single-operator performance | `test-backend-ops perf` | `/bin/test-backend-ops perf -o MUL_MAT --buft RISCV_AME -p 'type_a=q8_0,type_b=f32,m=512,n=128,k=512,bs=[1,1],nr=[1,1]'` |
| End-to-end performance | `llama-bench --fake-like` | `/bin/llama-bench --fake-like /root/stories15M-q8_0.gguf.om -t 1 -p 128 -n 0 -r 1 --estimate-layers 1 -fa 0 --no-warmup` |

A `CPU` value in the `be` column **does not mean that AME was unused**: AME is currently the `RISCV_AME` path under the ggml CPU backend, so whether AME is used has to be read from `[AME_PROFILE]`, `[GGML_XSAI_OP_PROFILE]` and the AME dispatch logs; when comparing, keep the same model, the same prompt and the same env filter, and **do not mix** `-p 1`, 1B models, differing progress-log settings, or the `e[0,1)/6` and `e[1,2)/6` stage counters into one experiment.
