# Verilator 仿真 {#sec:sim-verilator}

Verilator 是提交前做功能复验的 RTL 仿真路径。这一章给出流程、构建方式与通过条件。

## 三段式流程

Verilator 仿真路径固定为：

1. `make xsai` 构建仿真器 `XSAI/build/emu`；
2. `make run-emu` / `make run-emu-debug` 作为顶层入口；
3. 由 `scripts/run-emu.sh` 把顶层参数翻译为 `build/emu` 的底层参数并加载 payload；
4. 依据控制台输出、日志、波形、ChiselDB 与 difftest 结果判定是否通过。

## 构建

```bash
make xsai
```

`make xsai` 展开后等价于：

```plain
$(MAKE) -C XSAI emu -j<主机核数> \
  CONFIG=DefaultMatrixConfig LLC=ZhuJiang \
  WITH_DRAMSIM3=0 WITH_CHISELDB=1 WITH_CONSTANTIN=0 \
  EMU_THREADS=8 EMU_TRACE=fst OPT_FAST=-O3 ...
```

| 参数 | 默认值 | 含义 |
| --- | --- | --- |
| `XSAI_SIM_CONFIG` | `DefaultMatrixConfig` | 硬件配置 |
| `XSAI_SIM_LLC` | `ZhuJiang` | 末级缓存配置 |
| `XSAI_SIM_WITH_DRAMSIM3` | `0` | DRAMsim3 内存模型默认关闭，启用需同时提供 `DRAMSIM3_HOME` |
| `XSAI_SIM_WITH_CHISELDB` | `1` | 编译时启用 ChiselDB 支撑代码 |
| `XSAI_SIM_BUILD_JOBS` | 主机核数 | 构建并行度 |
| `EMU_THREADS` | `8` | Verilator 仿真线程数 |
| `EMU_TRACE` | `fst` | **编译期**打开 FST 波形支持，运行期导波的前提 |
| `XSAI_SIM_RTC_CLOCK_DIV` | `100` | RTC 分频，影响 guest 时间与仿真时长（见[常见故障排查](troubleshooting.md#sec:debug-troubleshooting)） |

以上均可在命令行覆盖，例如 `make xsai XSAI_SIM_BUILD_DIR=build-fast`。

底层三个构建目标的关系：

| 目标 | 产物 | 说明 |
| --- | --- | --- |
| `make verilog` | `build/rtl/XSTop.sv` | 综合用顶层（`top.TopMain`） |
| `make sim-verilog` | `build/rtl/SimTop.sv` | 仿真专用顶层（`top.XiangShanSim`） |
| `make emu` | `build/emu` | 在 `sim-verilog` 基础上编译出仿真器 |

即 `make xsai` 走的是**仿真 RTL**（`SimTop.sv`），不是综合 RTL。

## 运行入口

| 入口 | 行为 |
| --- | --- |
| `make run-emu` | 自动确保 `build/emu` 存在；`DIFF` 默认 `1`（开差分）、`LOG` 默认 `0`（不写时间戳日志） |
| `make run-emu-debug` | 强制 `--log` 与 `--db`，可附加 `WARMUP`、`MAX_INSTR`、`WAVE_BEGIN/END`、`FORK` |

脚本层默认（`scripts/run-emu.sh`）：

* 仿真器路径 `XSAI/build/emu`（`XSAI_SIM_BUILD_DIR` 可改）；
* 默认参考模型 `XSAI/ready-to-run/riscv64-nemu-interpreter-so`（可用 `--diff-so` 覆盖）；
* 仿真进程栈尝试设为 64 MiB（`EMU_STACK_KB=65536`）；
* payload 为必填项。

## 三类 payload

| 类型 | 路径 | 用途 |
| --- | --- | --- |
| 预置裸机镜像 | `XSAI/ready-to-run/*.bin` | 最小验证首选 |
| GCPT 启动镜像 | `firmware/gcpt_restore/build-*/build/gcpt.bin` | 完整启动流程 |
| checkpoint 片段 | `firmware/checkpoints/**/*.zstd` | 切片与性能研究 |

## 最小验证

选负载的原则：输入简单可得、失败链路最短、判定快、必要时可升级到带产物的调试运行。推荐优先级：
`coremark-2-iteration.bin` → `microbench.bin` → `linux.bin` → `gcpt.bin` → checkpoint。

```bash
# 档一：最小裸机负载（推荐入口）
make run-emu PAYLOAD=XSAI/ready-to-run/coremark-2-iteration.bin DIFF=1

# 档二：保留日志与 DB
make run-emu-debug PAYLOAD=XSAI/ready-to-run/coremark-2-iteration.bin DIFF=1

# 档三：最小 Linux 级仿真
make run-emu PAYLOAD=XSAI/ready-to-run/linux.bin DIFF=1
```

不要依赖顶层默认 `PAYLOAD`（默认是 `gcpt.bin`，会把固件构建链带进来）。

## 差分开关

| 值 | 效果 | 用途 |
| --- | --- | --- |
| `DIFF=1`（默认） | 传 `--diff`，与参考模型逐步比对 | 标准路径 |
| `DIFF=0` | 传 `--no-diff` | 隔离"是否差分接口本身导致的问题" |

建议两步法：先跑 `DIFF=1`，失败且怀疑参考模型时再补 `DIFF=0`。

## 通过条件

| 输出 | 状态 | 判定 |
| --- | --- | --- |
| `HIT GOOD TRAP` | `STATE_GOODTRAP` | 通过 |
| `EXIT at pc = ...` | `STATE_SIM_EXIT` | 通常通过 |
| `EXCEEDING CYCLE/INSTR LIMIT` | `STATE_LIMIT_EXCEEDED` | 窗口化运行时可接受 |
| `ABORT at pc = ...` | `STATE_ABORT` | 失败 |
| `HIT BAD TRAP` | — | 失败 |

除末行结论外还应确认：payload 是否被正确识别（`The image is ...`、`Zstd file detected` 等）、参考模型是否接通、是否出现 mismatch 或
`No difftest check for more than ... cycles, maybe get stuck.`、以及结束时的 `instrCnt` / `cycleCnt` / `IPC` 统计。

## 调试产物与波形

`run-emu-debug` 默认留下：`log/<prog>_<timestamp>.log`、`...err.log`、`.db`（ChiselDB）。

```bash
make run-emu-debug PAYLOAD=<payload> DIFF=1 WAVE_BEGIN=<b> WAVE_END=<e>
```

波形写至 `log/<prog>_<timestamp>.fst`，且**必须在编译期启用 `EMU_TRACE`** 才能导出。
