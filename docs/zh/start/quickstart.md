# 15 分钟上手 {#sec:get-started}

这一章带你在一台 Linux 工作站上跑通 `xsai-env` 环境，并运行第一个负载。开始前需要 RISC-V 交叉编译工具链与 `direnv`，例如 Ubuntu / Debian 上：

```bash
sudo apt install gcc-riscv64-linux-gnu g++-riscv64-linux-gnu gfortran-riscv64-linux-gnu binutils-riscv64-linux-gnu
```

## 一、拿到工作台

`xsai-env` 是香炉峰软硬件开发的集成工作台，把 RTL、模拟器、固件、根文件系统、工具链与测试流程放在同一个顶层 `Makefile` 下。日常命令一律从仓库根目录发起，不要进各子模块里分别查找。

```bash
git clone https://github.com/OpenXiangShan/xsai-env
cd xsai-env
sudo make deps        # 安装系统依赖（Ubuntu / Debian）
direnv allow
make init-force
```

初始化会递归拉取全部子模块，并设置 `XS_PROJECT_ROOT`、`NOOP_HOME`（RTL）、`NEMU_HOME`、`QEMU_HOME`、`AM_HOME` 等路径。

**部分子模块当前无法匿名拉取**：`llvm-project-ame`、`riscv-matrix-extension-spec` 等仓库仍在整理开源中。看到下面的提示属正常，可以先跳过，软件与仿真流程不受影响：

```text
Skipping submodule 'NutShell'
Cloning into 'riscv-matrix-spec'...
remote: Invalid username or token. Password authentication is not supported for Git operations.
fatal: Authentication failed for 'https://github.com/OurCompArchGroup/riscv-matrix-extension-spec.git/'
Failed to clone 'riscv-matrix-spec'
make: *** [Makefile:180: init-force] Error
```

编译器不必从源码构建，直接用预编译包，见 [AME LLVM 的获取](../sdk/layout.md#sec:sdk-layout)：

```bash
wget https://github.com/OurCompArchGroup/llvm-release/releases/download/20260708/llvm-20260708-proposal-14.tar.gz
tar -xf llvm-20260708-proposal-14.tar.gz
```

机器相关的覆盖项（工具链路径、LLVM 路径、代理等）放在不纳入版本管理的 `.envrc.local` 里，从模板复制后按本机情况修改：

```bash
cp .envrc.local.example .envrc.local
```

## 二、先做自检

```bash
make test-smoke      # 检查脚本与 Makefile 入口是否可用
```

自检通过再往下走。`make test` 是完整环境自检（构建 NEMU 与 NutShell，并跑一次 microbench），比 `test-smoke` 慢很多，建议在需要确认整条链路可用时再跑。

## 三、按需构建

不必全建，按你的目标选：

```bash
make llvm      # 本地 AME LLVM 工具链（也可直接用预编译包，见上文）
make nemu      # NEMU
make qemu      # QEMU
make xsai      # 等价 make emu-verilator：编译 XSAI 的 Verilator RTL 仿真
make firmware  # 串起 Linux kernel + riscv-rootfs + OpenSBI 等
```

`make xsai` 得到的 Verilator 仿真可用于提交前的功能复验；纯软件迭代优先用 QEMU 或 NEMU。

## 四、跑通第一个负载

先用快的把软件跑通，再上慢的：

```bash
make run-qemu                                  # 最快，先排软件与启动路径
make run-nemu                                  # 次快，且是 golden model 侧的中间层
make run-emu  PAYLOAD=<payload.bin>            # RTL 仿真
```

`make run-emu` 需要显式给 `PAYLOAD`。表示正常结束的字符串包括 `HIT GOOD TRAP`、`EXIT at pc`、`EXCEEDING CYCLE`、`ABORT`。

需要做切片分析时，先做 checkpoint：

```bash
make run-qemu
make run-nemu
make ckpt                                      # 制作 checkpoint
make run-nemu PAYLOAD=<checkpoint.zstd>
make run-emu  PAYLOAD=<checkpoint.zstd>
```

要按 SimPoint 聚类结果做 checkpoint，必须用 `make ckpt PHASE=checkpoint`；直接 `make ckpt` 走 `PHASE=all`，会跳过 profile 与 cluster 直接出单切片。详见 [Checkpoint 与切片](../verification/checkpoint.md#sec:debug-checkpoint)。

## 五、确认环境可用

| 检查 | 期望 |
| --- | --- |
| 初始化 | 子模块全部 checkout，环境变量已设置 |
| `make test-smoke` | 返回 0 |
| 第一个 QEMU 负载 | 正常结束 |
| 第一个 RTL 负载 | `HIT GOOD TRAP` |

到这里环境就通了。接下来按目标选路径：

* 适配算子与框架 → [框架适配路径](path-framework.md#sec:path-framework)
* 做性能分析 → [性能分析路径](path-perf.md#sec:path-perf)
* 理解软硬件如何配合 → [软硬件协同](../optimization/co-design.md#sec:co-design)
* 了解目录与构建目标 → [SDK 组成与目录结构](../sdk/layout.md#sec:sdk-layout)与[构建系统与 make 目标](../sdk/build.md#sec:sdk-build)

## 常见误区

* 不要在子模块里单独找命令，日常入口都在顶层 `Makefile`。
* 部分子模块仍在整理开源中，拉取失败不等于配置有错。
* `timebase` 在两个流程里不是同一个值：RTL 用核内 DTS（1 MHz），`firmware/nemu_board/dts/build/xiangshan_ai.dtb` 由 DTSGen 为固件流程生成（默认 10 MHz）。DTB 不能在两条流程间直接搬运，详见[常见故障排查](../verification/troubleshooting.md#sec:debug-troubleshooting)。
* RTL 仿真属重负载，按本机可用的 CPU 与内存设置并行度，避免影响同机其他任务。
