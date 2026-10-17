# 环境准备 {#sec:sim-environment}

这一章说明仿真环境搭好之后怎么用：目录职责、常用目标，以及几条仿真流程怎么选。首次搭建的完整步骤在[15 分钟上手](../start/quickstart.md#sec:get-started)。

## 目录职责

`xsai-env` 是香炉峰的集成工作区，顶层 `Makefile` 负责编排：

| 目录 | 内容 |
| --- | --- |
| `XSAI/` | RTL 工程，仿真器产物在 `XSAI/build/` |
| `NEMU/`、`qemu/` | 功能模拟器 |
| `firmware/` | 固件、rootfs、checkpoint 与设备树 |
| `tools/` | 性能分析工具 |
| `local/`、`build/`、`log/` | 生成产物，不入库 |

环境变量 `RISCV`、`RISCV_SYSROOT`、`QEMU_LD_PREFIX` 会自动探测；机器相关的覆盖写入 `.envrc.local`。顶层不导出 `CROSS_COMPILE`，固件与软件流程各自设置工具链前缀。

## 常用目标

| 目标 | 作用 |
| --- | --- |
| `make xsai` | 构建 Verilator 仿真器 |
| `make run-emu` | 运行 Verilator 仿真 |
| `make run-nemu` | 运行 NEMU |
| `make run-qemu` | 运行 QEMU |
| `make firmware` | 构建固件与 rootfs |
| `make test-smoke` | 快速环境自检 |
| `make test` | 完整环境自检，较慢 |

完整列表见 `make help`；`make help` 不覆盖的目标见[构建系统与 make 目标](../sdk/build.md#sec:sdk-build)。

## 怎么选仿真流程

| 你要做什么 | 用哪个 | 说明 |
| --- | --- | --- |
| 快速迭代软件、查启动路径 | QEMU | 最快，只验算术语义 |
| 与参考模型逐步比对 | NEMU | 差分验证的参考侧 |
| 提交前功能复验、抓波形 | Verilator | 见 [Verilator 仿真](verilator.md#sec:sim-verilator) |
| 覆盖率收集、双引擎交叉确认 | VCS | 见 [VCS 仿真与用例框架](vcs.md#sec:sim-vcs) |
| 定位功能差异到具体指令 | 差分验证 | 见[差分验证](difftest.md#sec:debug-difftest) |
| 反复分析同一段负载 | checkpoint 切片 | 见 [Checkpoint 与切片](checkpoint.md#sec:debug-checkpoint) |

先用快的把软件跑通，再逐级往慢的走。

## 自检

先 `make test-smoke` 做快速验证；`make test` 会构建 NEMU 与 NutShell 并跑一次 microbench，只在需要确认整条链路时运行。

`make help` 与 `make -n <target>` 可以确认命令路径，但 `run-*` 类目标内含递归 `$(MAKE)`，`-n` 并非绝对无副作用。
