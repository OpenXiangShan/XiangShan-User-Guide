# 工作流与贡献流程 {#sec:sdk-workflow}

本仓库使用 issue-first、branch-per-change 的工作流：改动保持小到足以审阅，并在能证明行为的最窄路径上验证。本文面向要给项目提 issue/PR 的人，以及要在同一仓库里同时改多处的人。构建与运行入口见[构建系统与 make 目标](build.md#sec:sdk-build)，子模块与版本记录见[子模块与版本管理](submodules.md#sec:sdk-submodules)。

## 从 issue 开始

| 场景 | 使用的模板 |
| --- | --- |
| Bug | bug report 模板，先用[常见故障排查](../verification/troubleshooting.md#sec:debug-troubleshooting)排查 |
| 原因不明的失败 | problem report 模板，直到根因明确 |
| 新行为或工作流变更 | feature request 模板 |
| 提问 | question 模板 |

终端优先流程：

```bash
bash scripts/bug-report.sh
bash scripts/create-issue.sh --type bug --title "..."
bash scripts/create-issue.sh --type feature --title "..."
```

Issue 标题是给人读的摘要，要带模板前缀（`[Bug Report] ...`、`[Feature Request] ...`、`[Problem] ...`）；`fix(qemu): ...`、`docs(checkpoint): ...` 这类 Conventional Commit 风格留给 commit 与 PR 标题。**根因属于上游组件仓库（`XSAI`、`NEMU`、`qemu`、`riscv-rootfs`）时，须在上游立项并关联 issue**，`xsai-env` 的 issue 只写集成上下文。

## 分支命名

```bash
git switch master
git pull --ff-only
git switch -c fix/123-checkpoint-replay
```

| 前缀 | 用途 |
| --- | --- |
| `fix/<issue>-short-topic` | bug 修复 |
| `feat/<issue>-short-topic` | 新行为 |
| `docs/<issue>-short-topic` | 纯文档 |
| `test/<issue>-short-topic` | 纯测试 |
| `refactor/<issue>-short-topic` | 保持行为的结构调整 |
| `chore/<issue>-short-topic` | 维护 |
| `ci/<issue>-short-topic` | CI 变更 |
| `bump/<component>-<rev-or-topic>` | 子模块或版本 bump |
| `wip/<topic>` | 仅限临时私有工作，开 PR 前必须改名 |

每个分支只有一个主写范围；改动横跨高风险契约（Matrix ISA 语义、difftest、memory-map、checkpoint 格式、rootfs 启动流程）时，**除非接口变更本身需要协同补丁，否则拆成串行 PR**。

## 提交与 PR

Conventional Commits 风格主题：

```text
fix(checkpoint): respect Makefile SimPoint defaults
feat(rootfs): add llama bench model preset
docs(workflow): document branch and PR flow
chore(submodule): bump NEMU to a587e09
```

每个 commit 尽量可审阅、可构建；机械格式化与行为变更分开；有用时在 body 提 issue ID（`Fixes #123`、`Refs #123`）。**不要提交 `local/`、`build/`、`log/`、`firmware/checkpoints/` 下的生成物**。子模块 bump 写明新旧 revision 与原因。

PR 面向 `master`，描述包含关联 issue（`Fixes #123` / `Refs #123`）、用户可见或工作流可见的变更摘要、主要 workstream 与触及路径、已运行的验证命令（或明确说明未跑的原因）、耦合区域的风险与审阅关注点、根因跨仓库时的上游 issue/PR 链接。未完成的工作保持 draft，只有 rebase/merge 到当前 `master` 且验证通过（或剩余缺口已显式说明）后才转 ready。合并前确认分支与 `master` 同步、CI 结果通过或失败已理解并记录；优先 squash 或 rebase merge 以保持 `master` 线性。子模块 bump PR 的审阅者需确认目标 commit 可从子模块远端 fetch，且根验证覆盖集成行为。

## 子模块改动

子模块变更产生两个不同的 commit：子模块仓库里的真实代码 commit，与 `xsai-env` 里的 gitlink bump commit；外层只能指向远端仓库中确实存在的子模块 commit。嵌套子模块从里往外提交，以 `XSAI/CUTE` 为例是 `XSAI/CUTE` → `XSAI` → `xsai-env`，每一层都指向下一层已提交、已 push、可审阅的 revision。完整步骤、`make versions` 的执行时机与根 bump PR 的记录要求见[子模块与版本管理](submodules.md#sec:sdk-submodules)。

## 调试与支持

高频问题：

| 问题 | 日志或现象 | 原因 | 处置 |
| --- | --- | --- | --- |
| 内核 panic：No working init found | `Failed to execute /init (error -2)` 后 `Kernel panic - not syncing: No working init found.` | initramfs 里有 `/init`，但 busybox 指向的 loader 路径不在镜像中 | `make firmware` 后 `make run-qemu`；发生在切换环境之后时，先 `make -C firmware/riscv-rootfs clean` 再重建 |
| RTL 下 Linux 启动极慢 | OpenSBI 与早期 Linux 消息正常，其后的启动消息可能耗分钟到数小时 | `mtime` 与设备树 `timebase-frequency` 的比例不对 | 见下节 timebase 的取值 |

### timebase 的取值

每 guest 秒的 RTL 周期数等于 `RTC clock divider` × `timebase-frequency`，XSAI 仿真硬件默认把 RTL 时钟除以 100。声明 10 MHz 的 DTB 因此需要 `1,000,000,000` 个 RTL 周期才算一个 guest 秒；估算宿主时间时，用这个周期数除以你自己后端实测的仿真速率。仓库随附的 XSAI Linux 镜像与 XSAI 生成的 DTS 用 1 MHz，QEMU 的 `nemu` machine 用 10 MHz，**DTB 不能在 QEMU 与 RTL 之间直接搬用而不核对这个值**。启用 RTC 驱动或 CPUFreq 不能修正错误的 `mtime` 标度。

```bash
fdtget firmware/nemu_board/dts/build/xiangshan_ai.dtb /cpus timebase-frequency
grep -E 'CONFIG_(HZ|NO_HZ|RISCV_TIMER|CPU_FREQ|RTC_CLASS)' firmware/riscv-linux/.config

make -C firmware build-dtb-xsai XSAI_TIMEBASE_FREQ=10000000
make run-qemu

make -C firmware build-dtb-xsai XSAI_TIMEBASE_FREQ=1000000
make -C firmware build-gcpt-nemu
make xsai XSAI_SIM_RTC_CLOCK_DIV=100
make run-emu PAYLOAD=firmware/gcpt_restore/build-nemu/build/gcpt.bin
```

启动日志必须报告同一个 timebase，例如 `Platform Timer Device : aclint-mtimer @ 1000000Hz`、`sched_clock: 64 bits at 1MHz`。改 DTB 后必须重建 NEMU/RTL payload，因为 payload 内嵌 DTB；每个 divider 用独立的仿真构建目录，fast-RTC 即 `XSAI_SIM_BUILD_DIR=build-fast-rtc XSAI_SIM_RTC_CLOCK_DIV=2`。fast-RTC profile 适合软件启动与调试，**不适合墙钟或定时器延迟测量**；架构性能结果用 `cycle`、`instret` 与默认 divider。

### 上报与通知

`bash scripts/bug-report.sh` 生成 bug 报告用的环境与仓库信息包（选项 `--basic`、`--build-cmd <cmd>`、`--run-cmd <cmd>`、`--note <text>`，产物为 `${ROOT}/bug-report` 目录与 `bug-report.tar.gz`）；`bash scripts/create-issue.sh` 是终端优先的 issue 工作流，基于 GitHub CLI，默认 repo 为 `OpenXiangShan/xsai-env`，未认证时报 `GitHub CLI is not authenticated. Run 'gh auth login' first.`。

## 工作流边界与并行规则

五条运行原则：

1. 一个任务只有一个主写范围。
2. 允许跨子系统改动，但仅当被改的正是接口本身时。
3. 若 A 改了 B 的契约，先改 A，第二步再集成 B，不让不相关的 agent 同时改两边。
4. 优先用仓库根 `Makefile` 与共享环境入口。
5. 测试与工具应验证或自动化流程，**不应悄悄成为某个子系统契约的唯一 source of truth**。

各 workstream 的主路径、拥有范围与典型入口见[SDK 组成与目录结构](layout.md#sec:sdk-layout)。

**可并行**：

* `docs/`、`README.md`、`AGENTS.md`、`.agents/skills/` 下的纯文档任务。
* 单个 `firmware/riscv-rootfs/apps/<app>/`、`nexus-am/apps/<app>/` 或 `nexus-am/tests/<test>/` 内自包含的改动，不涉及共享 rootfs manifest、init 脚本、公共 runtime 或 ISA 契约。
* `tools/` 或 `scripts/` 下不改变组件契约的独立 helper。

**必须串行**（除非有非常明确的写所有权拆分）：

* Matrix ISA 语义、CSR 行为、指令编码或 ABI 期望。
* `NEMU/` 与 `XSAI/` 之间的 difftest/reference-model 对齐。
* Memory map、DTB、reserved-memory 或 DMA window 变更。
* Checkpoint 格式、restore 行为，或 profile/cluster/dump 编排。
* `nexus-am/` 中会扇出到大量 apps/tests 的共享运行时/库改动。
* `Makefile`、`scripts/`、`env.sh`、`.envrc*` 下的顶层环境与构建入口改动。

高风险耦合区域与处理方式：

| 区域 | 涉及文件 | 建议 |
| --- | --- | --- |
| Matrix ISA、intrinsic、CSR 或 ABI 变更 | `llvm-project-ame/`、`DSL/`、`nexus-am/`、`NEMU/`、`qemu/`、`XSAI/` | 先落地 source-of-truth 变更，再逐个更新消费者，每层做显式验证 |
| Difftest 对齐 | `NEMU/` 与 `XSAI/` | 改契约的一方先改，第二步再集成另一方 |
| Memory-map 与 DTB 变更 | `mk/`、firmware board 文件、Linux config 假设、rootfs app（如 `hello_xsai`） | 按 firmware/platform 契约变更处理 |
| Checkpoint 流变更 | `scripts/checkpoint.sh`、`Makefile`、`qemu/`、`firmware/gcpt_restore/`、`NEMU/resource/simpoint/` | 保持单一集成负责人，失败模式通常只在端到端可见 |
| Rootfs 启动流变更 | app 代码、`firmware/riscv-rootfs/Makefile`、initramfs manifests、init 脚本 | 把构建、打包、启动调用当作一个改动 |

高风险耦合改动要求至少一名熟悉归属子系统的审阅者。路由顺序：先识别主 workstream，列出最可能的 source-of-truth 路径，标出下游消费者（它们可能需要验证，但此时不应编辑）；必须改动多个 source of truth 时拆成串行阶段，偏好最小、局部的编辑，并在能证明改动的最窄路径上验证；不确定归属时，从定义接口的子系统开始。
