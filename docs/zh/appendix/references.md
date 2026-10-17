# 附录 C：参考文档与仓库 {#sec:appendix-references}

本附录汇总本手册引用的手册、代码仓库与工具入口。仓库地址取自 `xsai-env` 的 `.gitmodules` 与 `VERSIONS`，钉住的版本见[子模块与版本管理](../sdk/submodules.md#sec:sdk-submodules)。

## 相关手册

* [香山开源处理器用户手册（昆明湖 V2R2）](https://docs.xiangshan.cc/projects/user-guide/zh-cn/latest/)——本手册的基线行为。本手册只写相对它的增量，通用部分以它为准
* [同手册的 PDF 与历史版本](https://github.com/OpenXiangShan/XiangShan-User-Guide/releases)
* [本手册源码仓库](https://github.com/OurCompArchGroup/XiangShan-User-Guide)

香炉峰 ISA 规范与提案（ZAMES / ZMASYNC / 低精度转换）见下表 `riscv-matrix-extension-spec`。

## 代码仓库

以下地址取自 `xsai-env/.gitmodules` 与 `VERSIONS`，统一写成 HTTPS 便于直接克隆；钉住的 revision 见[子模块与版本管理](../sdk/submodules.md#sec:sdk-submodules)。

### 处理器与矩阵单元

| 仓库 | 内容 |
| --- | --- |
| [OpenXiangShan/XSAI](https://github.com/OpenXiangShan/XSAI) | XiangShan AI RTL，矩阵核热点在 `XSAI/CUTE/` |
| [OpenXiangShan/CUTE](https://github.com/OpenXiangShan/CUTE) | 矩阵计算单元（CUTE），独立上游仓库 |
| [OpenCUTE/CUTE-Design-Doc](https://github.com/OpenCUTE/CUTE-Design-Doc) | CUTE 设计文档 |
| [OpenXiangShan/HBL2](https://github.com/OpenXiangShan/HBL2) | 高带宽 L2 |
| [OpenXiangShan/CoupledL2](https://github.com/OpenXiangShan/CoupledL2) | 基线 L2（HBL2 基于它改造） |

### 编译器与算子

| 仓库（`xsai-env` 内路径） | 内容 |
| --- | --- |
| [OurCompArchGroup/llvm-project-ame](https://github.com/OurCompArchGroup/llvm-project-ame)（`llvm-project-ame`） | AME 版 LLVM 工具链 |
| [OurCompArchGroup/llvm-release](https://github.com/OurCompArchGroup/llvm-release/tags) | 预编译 LLVM 包，优先用它，免去自行构建 |
| [OurCompArchGroup/buddy-mlir](https://github.com/OurCompArchGroup/buddy-mlir) | 多层级编译流中间层（分支 `zames-backend-v1-no-ra`） |
| [OurCompArchGroup/triton-riscv](https://github.com/OurCompArchGroup/triton-riscv) | Triton RISC-V 后端 |
| [OurCompArchGroup/xsai-blas](https://github.com/OurCompArchGroup/xsai-blas) | 算子库（softmax、layernorm、rmsnorm、silu、gelu 等） |
| [OurCompArchGroup/TMA-toolkit](https://github.com/OurCompArchGroup/TMA-toolkit)（`tools/TMA-toolkit`） | Top-down 性能分析工具与计数器 preset |
| [OurCompArchGroup/nexus-am-ame](https://github.com/OurCompArchGroup/nexus-am-ame)（`nexus-am`） | 裸机 AM 运行时 |
| [OurCompArchGroup/riscv-matrix-extension-spec](https://github.com/OurCompArchGroup/riscv-matrix-extension-spec)（`riscv-matrix-spec`） | 矩阵扩展规范与提案 |

### 推理框架

| 仓库（`xsai-env` 内路径） | 内容 |
| --- | --- |
| [OurCompArchGroup/MNN](https://github.com/OurCompArchGroup/MNN)（`software/MNN`） | MNN 的 AME 适配分支 |
| [OurCompArchGroup/ncnn](https://github.com/OurCompArchGroup/ncnn)（`software/ncnn`） | ncnn 的 AME 适配分支 |
| [OurCompArchGroup/llama.cpp](https://github.com/OurCompArchGroup/llama.cpp)（`software/llama.cpp`） | llama.cpp / ggml 的 AME 适配分支 |

三个都是各自上游的 fork，上游地址分别为 [alibaba/MNN](https://github.com/alibaba/MNN)、[Tencent/ncnn](https://github.com/Tencent/ncnn)、[ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)。改动内容见[算子库与推理框架](../software/frameworks.md#sec:sw-frameworks)。

### 模拟器与固件

| 仓库（`xsai-env` 内路径） | 内容 |
| --- | --- |
| [OpenXiangShan/NEMU](https://github.com/OpenXiangShan/NEMU) | Golden model / ISA 参考 |
| [OpenXiangShan/qemu](https://github.com/OpenXiangShan/qemu) | QEMU（分支 `9.0.0_matrix-v0.12`） |
| [OpenXiangShan/DRAMsim3](https://github.com/OpenXiangShan/DRAMsim3) | DRAM 模拟器 |
| [OSCPU/NutShell](https://github.com/OSCPU/NutShell) | 参考处理器 |
| [OpenXiangShan/LibCheckpoint](https://github.com/OpenXiangShan/LibCheckpoint)（`firmware/LibCheckpoint`） | checkpoint 库 |
| [OpenXiangShan/LibCheckpointAlpha](https://github.com/OpenXiangShan/LibCheckpointAlpha)（`firmware/gcpt_restore`） | restore-only GCPT |
| [OpenXiangShan/nemu_board](https://github.com/OpenXiangShan/nemu_board)（`firmware/nemu_board`） | NEMU 板级文件与 DTB 构建 |
| [riscv-software-src/opensbi](https://github.com/riscv-software-src/opensbi)（`firmware/opensbi`） | OpenSBI |
| [OurCompArchGroup/riscv-rootfs](https://github.com/OurCompArchGroup/riscv-rootfs)（`firmware/riscv-rootfs`） | Linux rootfs 与 apps |

集成工作台本身：[OpenXiangShan/xsai-env](https://github.com/OpenXiangShan/xsai-env)。

## 工具与资料

* `xsai-env` 仓库内的 `docs/` 与 `AGENTS.md`：环境说明与工作流
* 环境自检：`make test-smoke` / `make test`
* 问题上报：`scripts/bug-report.sh`、`scripts/create-issue.sh`
* 香山文档总站：<https://docs.xiangshan.cc/>

## 构建产物与负载

| 路径 | 内容 |
| --- | --- |
| `XSAI/build/emu` | Verilator 仿真器 |
| `XSAI/build/rtl/SimTop.sv` | 仿真专用 RTL 顶层 |
| `XSAI/build/rtl/XSTop.sv` | 综合用 RTL 顶层 |
| `XSAI/ready-to-run/*.bin` | 预置裸机镜像 |
| `firmware/gcpt_restore/build-*/build/gcpt.bin` | checkpoint 恢复启动镜像 |
| `firmware/checkpoints/**/*.zstd` | checkpoint 分片 |
