# 构建系统与 make 目标 {#sec:sdk-build}

顶层 `Makefile` 编排全部构建与仿真路径，日常命令从仓库根发起。本页给出用户入口目标、`make help` 未覆盖的目标、firmware 子目标与验证阶梯。

`make help` 打印用户入口目标及其用途，但**不覆盖全部目标**：`qemu`、`firmware`、`run-nemu`、`run-emu`、`run-user`、`uniform`、`emu-verilator`、`emu-gsim`、`smoke` 存在于 `Makefile` 中而未列出。以下各表按用途分组，并把它们一并收纳。

## 设置与检查

| 目标 | 用途 |
| --- | --- |
| `make deps` | 安装系统依赖（需要 sudo） |
| `make init` / `make init-force` | 初始化子模块与环境 / 强制初始化子模块，避免空目录；全新 checkout 上耗时较久 |
| `make test-smoke` / `make test` | 运行快速非构建冒烟检查 / 测试环境（`./scripts/env-test.sh`，较重） |

## 工具链与模拟器

| 目标 | 用途 |
| --- | --- |
| `make llvm` | 构建自定义 LLVM 工具链（使用系统编译器），产物到 `local/llvm` |
| `make gsim` | 安装最新的 gsim 二进制到 `local/bin` |
| `make nemu` | 构建 NEMU 模拟器 |
| `make docker-nemu-image` / `make nemu-matrix-ref-so-docker` | 从 `centos.Dockerfile` 构建 NEMU Docker 镜像 / 在 Docker 内构建 `riscv64-matrix-xs-ref` 共享库 |
| `make xsai` | 构建 XSAI RTL 仿真（Verilator）；附注 `XSAI_SIM_RTC_CLOCK_DIV=$(XSAI_SIM_RTC_CLOCK_DIV) (even, >= 2)` |
| `make test-matrix` | 运行 matrix 简单测试 |
| `make qemu` | 构建 `qemu-system-riscv64` 与 `qemu-riscv64`（`target-list=riscv64-softmmu,riscv64-linux-user`，`--enable-zstd --enable-plugins`） |
| `make emu-verilator` / `make emu-gsim` | `make xsai` 的实际实现目标（`xsai: emu-verilator`）/ 构建基于 gsim 的 XSAI 仿真路径 |

`make gsim` 会拉取最新上游 release，**不是确定性的 bootstrap 步骤**，只在任务明确需要 gsim 时使用。gsim 路径当前的缺口：gsim `50b371c` 未实现 stateful ZhuJiang `GENERIC_RAM_*` 与 `ResetGenInnerS2` 外部模块，使用 ZhuJiang LLC 生成 C++ 后**在链接期失败**；在 gsim 获得外部模块模型前应使用 OpenLLC，**不要用无状态 stub 替代**。

## 固件与端到端运行

| 目标 | 用途 |
| --- | --- |
| `make firmware` | 构建 rootfs、Linux、DTB、QEMU/NEMU GCPT payload 与 restore-only GCPT；实现为 `$(MAKE) -C firmware all $(_LLAMA_EXTRA)`，是 `make run-qemu` / `make run-nemu` 背后的固件集成入口 |
| `make run-qemu` | 用 GCPT payload 跑 QEMU 仿真（可选：非空 `MODEL_IMG` 会以 virtio-blk 挂载为 `/dev/vda`，本手册负载不需要） |
| `make run-nemu` | 在 NEMU 上运行 GCPT payload |
| `make run-emu` | RTL（Verilator/GSIM）仿真入口：`EMU_BUILD_DIR=... EMU_BIN=... ./scripts/run-emu.sh ... $(PAYLOAD)`；细节见 [Verilator 仿真](../verification/verilator.md#sec:sim-verilator) |
| `make run-emu-debug` | RTL 调试：FST 波形 + ChiselDB（`FORK=1` 跳过波形）；典型参数 `PAYLOAD=<p> DIFF=1 WAVE_BEGIN=50000 WAVE_END=180000` |
| `make run-user` | 存在，但**当前是本地 `llama.cpp` 便利目标，含硬编码模型路径，不应被当作通用验证入口** |

`make run-qemu` / `make run-nemu` 需要时会自动构建缺失的 QEMU、DTB 或 GCPT 二进制（依赖目标 `_ensure_qemu_payload`、`_ensure_nemu_payload`、`_ensure_qemu`、`_ensure_qemu_dtb`）。`make -n` 用在编排或 `run-*` 目标上要小心：recipe 内的递归 `$(MAKE)` 仍可能执行，要求无副作用的 dry run 时先读 `Makefile`。

## firmware 子目标

| 子目标 | 用途 |
| --- | --- |
| `make -C firmware all` / `check-env` | 构建全部（默认）/ 校验环境设置；`SHOW_FIRMWARE_BUILD_LOGS=1` 可流式输出主要构建日志 |
| `make -C firmware download-linux` / `setup-submodules` / `init-force` | 下载 Linux 内核 / 初始化 git 子模块 / 强制初始化 firmware 子模块 |
| `make -C firmware build-rootfs` | 构建根文件系统；旋钮 `SHOW_ROOTFS_BUILD_LOG=1`、`ROOTFS_MAKE_JOBS`、`XSAI_INIT_MODE`、`XSAI_WORKLOAD`、`XSAI_AUTO_EXIT`、`XSAI_DROP_SHELL` |
| `make -C firmware build-linux` | 构建 Linux 内核；旋钮 `SHOW_LINUX_BUILD_LOG=1`、`LINUX_MAKE_JOBS`、`FORCE_LINUX_CONFIG=1`、`INITRAMFS_SOURCE`、`INITRAMFS_COMMON_SOURCES` |
| `make -C firmware build-dtb` / `build-dtb-std` / `build-dtb-xsai` | 构建 XSAI 设备树 blob（默认）/ 分别构建标准 XiangShan DTB 与 XSAI 专用 DTB；`build-dtb-std` 的可选旋钮 `DIRECT_MAP_MEM_START`、`DIRECT_MAP_MEM_SIZE`、`STD_TIMEBASE_FREQ`，`build-dtb-xsai` 的旋钮 `XSAI_TIMEBASE_FREQ` |
| `make -C firmware build-opensbi` / `build-opensbi-nemu` | 分别构建 QEMU OpenSBI firmware payload（运行时 DTB）与 NEMU OpenSBI firmware payload（内嵌 DTB） |
| `make -C firmware build-gcpt` / `build-gcpt-nemu` | 分别构建链接 payload 的 QEMU 可引导 GCPT 与 NEMU 可引导 GCPT |
| `make -C firmware build-gcpt-restore` / `build-gcpt-clean` | 构建用于 checkpoint 恢复的 restore-only GCPT / 强制清理并重建 GCPT（如改过 `csr.h` 之后） |
| `make -C firmware clean` / `distclean` | 清理构建产物 / 深清：删除下载内容并反初始化子模块 |

`firmware/Makefile all` 依次执行 `build-rootfs` → `build-linux` → `build-dtb` → `build-gcpt-qemu` → `build-gcpt-nemu` → `build-gcpt-restore`，随后打印 Linux Image、DTB、QEMU 与 NEMU OpenSBI payload、QEMU 与 NEMU GCPT、GCPT Restore 的产物路径。

## SimPoint 与 checkpoint

| 目标 | 用途 |
| --- | --- |
| `make simpoint` | 构建 SimPoint 聚类二进制 |
| `make profile` | 阶段 1：QEMU profiling（BBV 采集） |
| `make cluster` | 阶段 2：SimPoint 聚类 |
| `make ckpt` / `make ckpt PHASE=profile\|cluster\|checkpoint` | 默认 `PHASE=all` 只出**单个切片**、不使用 SimPoint 聚类结果；要按聚类做 checkpoint 需显式 `PHASE=checkpoint` / 只跑单个阶段 |
| `make ckpt-nosimpoint` | 不做 SimPoint 聚类的单切片 checkpoint 流程 |

这些目标的 `MODEL_IMG` 是**可选**的（`Makefile` 默认置空，`checkpoint.sh` 对空值放行；非空时才按 `format=raw` 以 virtio-blk 挂载为 `/dev/vda`）。**本手册涉及的负载都不需要它**：rootfs 以 initramfs 形式内嵌，负载二进制随镜像一起构建，无需外部磁盘镜像。仓库也不提供生成它的目标；`make help` 里「require MODEL_IMG」的说法与代码不符。可用旋钮为 `WORKLOAD_NAME CPT_INTERVAL PROFILING_INTERVALS SIMPOINT_MAX_K MEMORY SMP CHECKPOINT_CONFIG MODEL_IMG CKPT_ARGS`。`make uniform` 目标存在（整段执行每 N 条指令 dump 一次，不需要 SimPoint），但**未列在 `make help`**；`scripts/checkpoint.sh` 的用法串里包含 `uniform` 模式。

参数默认值随入口不同，**不要混用**：

| 入口 | `CHECKPOINT_CONFIG` | `WORKLOAD_NAME` | `CPT_INTERVAL` | `PROFILING_INTERVALS` | `SIMPOINT_MAX_K` | `SMP` |
| --- | --- | --- | --- | --- | --- | --- |
| 顶层 `make ckpt`（取 `Makefile` 的 SimPoint 采样默认） | `build` | `app` | `100000` | `CPT_INTERVAL` | `30` | `1` |
| 直接跑 `scripts/checkpoint.sh`（脚本内更快的单切片默认） | `build` | `app` | `100` | `CPT_INTERVAL` | `10` | `1` |

两种常见模式：Fast single-slice 走 `no_simpoint + do_checkpoint`，典型参数 `CPT_INTERVAL=100`，通常只产出一个 checkpoint，用于跳过 firmware/OS 启动、快速进入目标区间；SimPoint sampling 走 `do_profile + do_cluster + do_checkpoint`，典型参数 `CPT_INTERVAL=100000`、`SIMPOINT_MAX_K=30`，产出多个代表性片段，可在 NEMU 或 RTL emu 上并行回放做硬件侧性能研究；更严格的分阶段流程是 `make profile` → `make cluster` → `make ckpt PHASE=checkpoint`。checkpoint payload 路径取决于生成的 SimPoint/checkpoint 索引以及 `WORKLOAD_NAME`、`CHECKPOINT_CONFIG`；`firmware/checkpoints/build/app/1/_1_1.zstd` 只是**常见示例，不是通用常量**。完整流程见 [Checkpoint 与切片](../verification/checkpoint.md#sec:debug-checkpoint)。

## 打包、分析与维护

| 目标 | 用途 |
| --- | --- |
| `make ccdb` / `make ccdb-append` | 通过 bear 重建统一的 `compile_commands.json` / 追加一次构建并去重 |
| `make update` / `make versions` | 更新子模块到最新 / 从当前子模块状态重新生成 `VERSIONS` |
| `make clean` / `make distclean` | 清理构建产物（NEMU、AM、firmware、`build/`）/ 深清，含 LLVM、qemu 构建、firmware 子模块 |

## 验证阶梯

验证顺序由快到慢逐级收窄：先用最快的模拟器排除软件问题，再进 golden model，最后上 RTL。

```bash
make run-qemu
make run-nemu
make ckpt
make run-nemu PAYLOAD=<checkpoint.zstd>
make run-emu PAYLOAD=<checkpoint.zstd>
```

| 层 | 定位与相对速度 |
| --- | --- |
| QEMU | 对 bring-up 而言约比 NEMU 快一个数量级，且更便于软件 bug 分析 |
| NEMU | 约比 RTL 快两个数量级，是碰 RTL 之前**首选的 golden-model 门**；不要假设 QEMU 验证能覆盖 NEMU 语义 |
| RTL | 应在软件路径已收窄之后使用，主要用于真实性能行为或 workload 级验证 |

### 各 workstream 的快速与集成验证

| Workstream | 快速验证 | 集成验证 |
| --- | --- | --- |
| RTL / `XSAI/` | `make xsai`、`make run-emu-debug PAYLOAD=...` | 带 difftest 的 RTL 定向 workload |
| `NEMU/` 与 `qemu/` | `make nemu`、`make qemu` | 运行目标 workload 或 reference-mode 流程、`make run-qemu` |
| firmware / `nexus-am/` / 编译器 | `make -C firmware build-dtb`、app/rootfs 与 app/test 本地构建、定向 app 重编、`llvm-objdump` | `make firmware`、`make run-qemu`、`make test-matrix` 或定向 AM run、下游 software/runtime 执行（见[编译器与算子 DSL](../software/compiler.md#sec:sw-compiler)） |
| checkpoint flow | 脚本 sanity 与目标存在性 | `make simpoint`、`make profile`、`make cluster`、`make ckpt` |

### workload 侧的 `nemu_signal(...)` 标记

切片依赖两层同时到位：外层编排参数（interval、clustering 旋钮）与 workload 侧标记。信号值定义于 `firmware/riscv-rootfs/apps/hello_xsai/ame.h`：

| 信号 | 值 | 含义 |
| --- | --- | --- |
| `DISABLE_TIME_INTR` | `0x100` | 准备采样；关闭定时器中断 |
| `NOTIFY_PROFILER` | `0x101` | 开始对感兴趣区间（ROI）做 profiling |
| `NOTIFY_PROFILE_EXIT` | `0x102` | 结束 ROI profiling |
| `GOOD_TRAP` | `0x0` | 干净终止 |

放置规则：setup 尽量放在 `NOTIFY_PROFILER` 之前，真正的热 kernel 或代表性 workload 放在 `NOTIFY_PROFILER` 与 `NOTIFY_PROFILE_EXIT` 之间，cleanup 尽量放到 `NOTIFY_PROFILE_EXIT` 之后；保持 ROI 稳定可复现，宁要一个干净 ROI 不要多个嘈杂小区间。**`DISABLE_TIME_INTR` 会改变运行时行为**：依赖定时器中断或正常多线程调度的软件，在该点之后不是直接 profiling 的好候选。

### RTL 层的 difftest 与增量构建缓存

* RTL difftest 链路：`NEMU/` 参考 `.so` → `XSAI/difftest` → `XSAI/build/emu`；出现 difftest mismatch 时，根因可能在 RTL、NEMU 语义、payload 假设或测试镜像本身。增量 RTL 构建缓存按两个 key 决策：`rtl-key` 决定是否必须跑 Chisel/CIRCT elaborate，`emu-key` 决定能否直接落一整套 RTL+Verilator 产物；耗时随机器与配置差异较大，建议在目标机器上实测一次作为基线。
* **依赖图边界**：Verilator 的依赖清单不含 hierarchy-aware 的 parent / child 关系，因此编辑被 split 出的 child 文件（例如 `rtl/CMatrixReg.sv`）后，普通 flat `make` 可能返回成功但 `emu` 产物并未更新。此时应按修改范围强制重建，不要只看 `make` 的返回码。

### AI 软件栈的三层验证

每次算子修改按三层理解，端到端性能是最终 gate：

| 层 | 手段 | 示例（逐字） |
| --- | --- | --- |
| 算子正确性 | rootfs 内 `test-backend-ops test`，目标 backend `RISCV_AME` | `/bin/test-backend-ops test -o MUL_MAT --buft RISCV_AME -p 'type_a=q8_0,type_b=f32,m=(288\|768),n=128,k=(288\|768),bs=[1,1],nr=[1,1]'` |
| 单算子性能 | `test-backend-ops perf` | `/bin/test-backend-ops perf -o MUL_MAT --buft RISCV_AME -p 'type_a=q8_0,type_b=f32,m=512,n=128,k=512,bs=[1,1],nr=[1,1]'` |
| 端到端性能 | `llama-bench --fake-like` | `/bin/llama-bench --fake-like /root/stories15M-q8_0.gguf.om -t 1 -p 128 -n 0 -r 1 --estimate-layers 1 -fa 0 --no-warmup` |
。日志里 `be` 列显示 `CPU` **不代表没用 AME**：当前 AME 是 ggml CPU backend 下的 `RISCV_AME` 路径，是否走 AME 要看 `[AME_PROFILE]`、`[GGML_XSAI_OP_PROFILE]` 和 AME dispatch 日志；比较时保持同一模型、同一 prompt、同一 env 过滤，**不要把** `-p 1`、1B 模型、progress log 开关不同、或 `e[0,1)/6` 与 `e[1,2)/6` 的 stage counters 混为同一实验。
