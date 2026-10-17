# Appendix C: References and Repositories {#sec:appendix-references}

This appendix collects the manuals, code repositories and tool entry points this manual refers to. The repository addresses come from `xsai-env`'s `.gitmodules` and `VERSIONS`; for the pinned revisions see [Submodules and Version Management](../sdk/submodules.md#sec:sdk-submodules).

## Manuals

* [XiangShan Open-Source Processor User Guide (Kunminghu V2R2)](https://docs.xiangshan.cc/projects/user-guide/en/latest/) — the baseline behaviour. This manual describes only what XSAI adds on top of it; for everything shared, that guide is authoritative
* [PDF and older releases of the same guide](https://github.com/OpenXiangShan/XiangShan-User-Guide/releases)
* [Source repository of this manual](https://github.com/OurCompArchGroup/XiangShan-User-Guide)

The XSAI ISA specifications and proposals (ZAMES / ZMASYNC / low-precision convert) live in `riscv-matrix-extension-spec` below.

## Repositories

The addresses below come from `xsai-env/.gitmodules` and `VERSIONS`; they are written as HTTPS so they can be cloned directly. For the pinned revisions see [Submodules and Version Management](../sdk/submodules.md#sec:sdk-submodules).

### Processor and matrix unit

| Repository | Content |
| --- | --- |
| [OpenXiangShan/XSAI](https://github.com/OpenXiangShan/XSAI) | the XiangShan AI RTL, with the matrix core hotspot under `XSAI/CUTE/` |
| [OpenXiangShan/CUTE](https://github.com/OpenXiangShan/CUTE) | the matrix compute unit (CUTE), an independent upstream repository |
| [OpenCUTE/CUTE-Design-Doc](https://github.com/OpenCUTE/CUTE-Design-Doc) | CUTE design documents |
| [OpenXiangShan/HBL2](https://github.com/OpenXiangShan/HBL2) | the high-bandwidth L2 |
| [OpenXiangShan/CoupledL2](https://github.com/OpenXiangShan/CoupledL2) | the baseline L2 that HBL2 reworks |

### Compiler and operators

| Repository (path inside `xsai-env`) | Content |
| --- | --- |
| [OurCompArchGroup/llvm-project-ame](https://github.com/OurCompArchGroup/llvm-project-ame) (`llvm-project-ame`) | the AME LLVM toolchain |
| [OurCompArchGroup/llvm-release](https://github.com/OurCompArchGroup/llvm-release/tags) | pre-built LLVM packages; prefer these over building it yourself |
| [OurCompArchGroup/buddy-mlir](https://github.com/OurCompArchGroup/buddy-mlir) | the multi-level compilation intermediate layer (branch `zames-backend-v1-no-ra`) |
| [OurCompArchGroup/triton-riscv](https://github.com/OurCompArchGroup/triton-riscv) | the Triton RISC-V backend |
| [OurCompArchGroup/xsai-blas](https://github.com/OurCompArchGroup/xsai-blas) | operator library (softmax, layernorm, rmsnorm, silu, gelu and others) |
| [OurCompArchGroup/TMA-toolkit](https://github.com/OurCompArchGroup/TMA-toolkit) (`tools/TMA-toolkit`) | Top-down performance analysis tooling and counter presets |
| [OurCompArchGroup/nexus-am-ame](https://github.com/OurCompArchGroup/nexus-am-ame) (`nexus-am`) | the bare-metal AM runtime |
| [OurCompArchGroup/riscv-matrix-extension-spec](https://github.com/OurCompArchGroup/riscv-matrix-extension-spec) (`riscv-matrix-spec`) | the matrix extension specification and proposals |

### Inference frameworks

| Repository (path inside `xsai-env`) | Content |
| --- | --- |
| [OurCompArchGroup/MNN](https://github.com/OurCompArchGroup/MNN) (`software/MNN`) | MNN fork with the AME port |
| [OurCompArchGroup/ncnn](https://github.com/OurCompArchGroup/ncnn) (`software/ncnn`) | ncnn fork with the AME port |
| [OurCompArchGroup/llama.cpp](https://github.com/OurCompArchGroup/llama.cpp) (`software/llama.cpp`) | llama.cpp / ggml fork with the AME port |

All three are forks of their respective upstreams — [alibaba/MNN](https://github.com/alibaba/MNN), [Tencent/ncnn](https://github.com/Tencent/ncnn) and [ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp). For what was changed see [Operator Libraries and Inference Frameworks](../software/frameworks.md#sec:sw-frameworks).

### Simulators and firmware

| Repository (path inside `xsai-env`) | Content |
| --- | --- |
| [OpenXiangShan/NEMU](https://github.com/OpenXiangShan/NEMU) | golden model / ISA reference |
| [OpenXiangShan/qemu](https://github.com/OpenXiangShan/qemu) | QEMU (branch `9.0.0_matrix-v0.12`) |
| [OpenXiangShan/DRAMsim3](https://github.com/OpenXiangShan/DRAMsim3) | DRAM simulator |
| [OSCPU/NutShell](https://github.com/OSCPU/NutShell) | reference processor |
| [OpenXiangShan/LibCheckpoint](https://github.com/OpenXiangShan/LibCheckpoint) (`firmware/LibCheckpoint`) | checkpoint library |
| [OpenXiangShan/LibCheckpointAlpha](https://github.com/OpenXiangShan/LibCheckpointAlpha) (`firmware/gcpt_restore`) | restore-only GCPT |
| [OpenXiangShan/nemu_board](https://github.com/OpenXiangShan/nemu_board) (`firmware/nemu_board`) | NEMU board files and DTB build |
| [riscv-software-src/opensbi](https://github.com/riscv-software-src/opensbi) (`firmware/opensbi`) | OpenSBI |
| [OurCompArchGroup/riscv-rootfs](https://github.com/OurCompArchGroup/riscv-rootfs) (`firmware/riscv-rootfs`) | Linux rootfs and apps |

The integration workbench itself: [OpenXiangShan/xsai-env](https://github.com/OpenXiangShan/xsai-env).

## Tools and material

* `docs/` and `AGENTS.md` inside the `xsai-env` repository: environment notes and workflows
* Environment checks: `make test-smoke` / `make test`
* Reporting: `scripts/bug-report.sh`, `scripts/create-issue.sh`
* XiangShan documentation hub: <https://docs.xiangshan.cc/>

## Build artifacts and payloads

| Path | Contents |
| --- | --- |
| `XSAI/build/emu` | Verilator emulator |
| `XSAI/build/rtl/SimTop.sv` | Simulation-only RTL top |
| `XSAI/build/rtl/XSTop.sv` | Synthesis-style RTL top |
| `XSAI/ready-to-run/*.bin` | Pre-built bare-metal images |
| `firmware/gcpt_restore/build-*/build/gcpt.bin` | Checkpoint restore boot image |
| `firmware/checkpoints/**/*.zstd` | Checkpoint slices |
