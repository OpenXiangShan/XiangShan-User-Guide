# 子模块与版本管理 {#sec:sdk-submodules}

`xsai-env` 的各组件以 git 子模块签出，顶层 `VERSIONS` 记录钉住的版本。这一章讲版本记录在哪、怎么更新，以及改动子模块时的先后顺序。目录职责见[SDK 组成与目录结构](layout.md#sec:sdk-layout)。

## 子模块清单

`VERSIONS` 由 `scripts/update-versions.sh` 自动生成，**不要手改**。下表逐字取自该文件，`(detached)` 表示签出在分离头指针上：

| 路径 | 组件名 | 分支/标签 | COMMIT | 用途 |
| --- | --- | --- | --- | --- |
| `DRAMsim3` | DRAMsim3 | `(detached)` | `1d2a9bf6da8e050d975ef2669c42faa93943f489` | DRAM 模拟器 |
| `NEMU` | NEMU | `v2026.07.r12` | `0b8e703791b255b2162ad2f8d83930cff7fd592c` | Golden model / ISA 参考：difftest 参考 `.so`、独立 profiling 与 checkpoint 支持、debug monitor |
| `NutShell` | NutShell | `(detached)` | `fc12171d929e7e589fab9f794ab63ce12e6c594e` | 某些验证流程使用的参考处理器 |
| `XSAI` | XSAI | `fix/rob-redirect-interlock` | `ba3406b5817cc81171fe6f17173bcbbf790455ec` | XiangShan AI RTL 源码、生成 Verilog、仿真器构建、DUT 侧 difftest；矩阵核热点在 `XSAI/CUTE/` |
| `docs/CUTE-Design-Doc` | CUTE 设计文档 | `master` | `93aa3d27bcb32624a86abfbd081e8aa53b3e87a7` | CUTE 设计文档，以子模块形式供在工作区内查阅 |
| `firmware/LibCheckpoint` | LibCheckpoint | `(detached)` | `2115c400af664ba06c57114db39a777ee7e5f1d0` | checkpoint 库 |
| `firmware/gcpt_restore` | LibCheckpointAlpha | `main` | `5b4fefe9efc5d22802f9e592ad2649b38d5146c1` | restore-only GCPT 二进制，用于 checkpoint 恢复 |
| `firmware/nemu_board` | nemu_board | `master` | `5c59af795b395f18368e37c2987728aa7eef16f9` | NEMU 板级文件与 DTB 构建 |
| `firmware/opensbi` | OpenSBI | `v1.8.1` | `74434f255873d74e56cc50aa762d1caf24c099f8` | QEMU 与 NEMU 的 OpenSBI firmware payload |
| `firmware/riscv-rootfs` | riscv-rootfs | `checkpoint` | `2194fa7cdd21f9ac5594f8f1cc790e7c36662bf3` | Linux rootfs 与 apps（`hello_xsai`、`gemm_precomp`、`llama.cpp`） |
| `llvm-project-ame` | llvm-project-ame | `triton-commit-hash` | `54eb82653d7a8ee110a604dac37571eadb53f4ef` | 支持 AME 的 LLVM/Clang、反汇编、底层 codegen |
| `nexus-am` | nexus-am | `test/ame-ls-word-cases` | `0a3325b2f42271cb8777f4d047dab8295f8de1cc` | AM 运行时、裸机库、NEMU 与 RTL 流程使用的 AM apps/tests |
| `qemu` | qemu | `9.0.0_matrix-v0.12` | `81900fed133533518785fec66c73ea3d0bd1eaf3` | Linux/user-mode 仿真、QEMU machine 支持、checkpoint 流程使用的 profiling plugin |
| `riscv-matrix-spec` | riscv-matrix-spec | `latest-511ddf6996d9ea0376ebd3539dcde7ec2af59b27` | `511ddf6996d9ea0376ebd3539dcde7ec2af59b27` | 矩阵扩展规范，ISA 与 codegen 契约的上游 |

`VERSIONS` 同时记录每个条目的 URL（如 `git@github.com:OpenXiangShan/XSAI`）。`software/MNN`、`software/ncnn`、`software/llama.cpp` 与 `tools/TMA-toolkit` 同样由 `.gitmodules` 注册并记录在 `VERSIONS` 中，属顶层子模块。

## VERSIONS 的维护

* `make versions` 从当前子模块状态重新生成 `VERSIONS`；不要在编辑器里直接改这个文件。
* 对每一次有意的根级子模块 bump 都要跑 `make versions`，它刷新顶层记录，让审阅者无需从 gitlink 反推即可检查被钉住的依赖状态；`VERSIONS` 与 gitlink 放进同一个父提交。
* 根 bump PR 要写明子模块路径、新旧 commit、关联的子模块 PR、为什么要在这里 bump，以及从根工作流跑过的验证。
* `make update`（`Update submodules to latest`）会更新子模块本身，与只做记录的 `make versions` 是两件事。

## 更新子模块

优先用显式路径更新，不要随便跑 `git submodule update --remote --recursive`：`.gitmodules` 中有些条目是 shallow、钉在非默认分支、或标了 `update = none`。开根 PR 前检查：

```bash
git status --short
git submodule status --recursive
git diff --submodule=log
```

## 改动子模块的顺序

子模块变更产生两个不同的 commit：子模块仓库里的真实代码 commit，与 `xsai-env` 里的 gitlink bump commit；外层只能指向可在远端仓库 fetch 到的子模块 commit。

1. 从 `.gitmodules` 确认归属仓库。
2. 变更不属于本地集成时，在归属仓库立项并关联 issue。
3. 在子模块内从其配置的上游分支拉分支。
4. 在子模块仓库内 commit、验证、push、开 PR。
5. 子模块 PR 合并后，更新 `xsai-env` 内的子模块 checkout。
6. 运行 `make versions`。
7. 在 `xsai-env` 中提交 gitlink bump 与 `VERSIONS` 更新，附验证结果与子模块 PR 链接。

嵌套子模块从里往外提交。以改动位于 `XSAI/CUTE` 为例：先在 `XSAI/CUTE` 提交并合并，再更新 `XSAI` 内的 `XSAI/CUTE` gitlink 并合并 `XSAI` PR，最后更新 `xsai-env` 内的顶层 `XSAI` gitlink、跑 `make versions`、开根 bump PR。每一层都指向下一层已提交、已 push、可审阅的 revision。

根 PR 依赖尚未合并的子模块 PR 时，根 PR 保持 draft、链接子模块 PR、写明临时 commit SHA，在子模块 commit 合并或稳定前不要 merge 根 PR；**不要提交指向本地-only commit 的 gitlink**。

## 跨子模块的依赖方向

| 链路 | 顺序 |
| --- | --- |
| ISA 与 codegen 契约 | `riscv-matrix-spec` → `llvm-project-ame` / `DSL/` → `software/` + `nexus-am` → `NEMU`、`qemu`、`XSAI` |
| Linux userspace bring-up | toolchain → `firmware/riscv-rootfs/apps/` → `firmware/` 镜像组装 → `qemu` → 可选 `XSAI` 或 checkpoint 消费者 |
| 裸机 / AM 流程 | toolchain → `nexus-am` runtime + apps/tests → `NEMU` 或 `XSAI` |
| RTL difftest 流程 | `NEMU` 参考 `.so` → `XSAI/difftest` → `XSAI/build/emu` |
| 仓库 checkpoint 流程 | `firmware/` payload + DTB → `qemu` profiling plugin → `NEMU/resource/simpoint/` 聚类二进制 → `scripts/checkpoint.sh` 编排 → `firmware/checkpoints/` |

## 与子模块相关的耦合场景

| 场景 | 涉及子模块 | 处理 |
| --- | --- | --- |
| Matrix ISA、intrinsic、CSR 或 ABI 变更 | `riscv-matrix-spec`、`llvm-project-ame`、`nexus-am`、`NEMU`、`qemu`、`XSAI` | 先落地 source-of-truth 变更，再逐个更新消费者，每层做显式验证 |
| Memory-map 或 reserved-memory 变更 | `XSAI`（`XSAI/CUTE/`）、`firmware/nemu_board`、`firmware/riscv-rootfs`（`hello_xsai`） | 按 firmware/platform 契约变更处理；`mk/memory.mk`、`firmware/linux-6.18/` config 假设与 QEMU 运行参数在根工作区 |
| Checkpoint 流变更 | `qemu`、`firmware/gcpt_restore`、`NEMU`（`resource/simpoint/`） | 保持单一集成负责人，失败模式通常只在端到端可见；编排在根工作区的 `scripts/checkpoint.sh` 与 `Makefile` |
| Rootfs 启动 workload 变更 | `firmware/riscv-rootfs` | 把 `firmware/riscv-rootfs/Makefile` 的构建、`rootfsimg/initramfs-*.txt` 的打包与 `rootfsimg/init-*.sh` 的启动调用当作一个改动 |

以上场景都要串行推进。

## 贡献约束

| 条目 | 说明 |
| --- | --- |
| 子模块的 gitlink | 外层只能指向远端可 fetch 的 commit，开父 PR 之前子模块的 commit 必须已 push |
