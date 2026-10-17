# 编译器与算子 DSL {#sec:sw-compiler}

香炉峰的编译器工作集中在 RISC-V 后端：让 LLVM 认识矩阵指令，并让上层 DSL 能把它们生成出来。本章说明工具链的能力边界与构建方式。

## 定位

XSAI 以 LLVM 作为主要编译器扩展基础，修改集中在 RISC-V 后端。重点不是重写 C/C++ 前端，而是在既有 LLVM 框架内增加矩阵扩展支持，从而让同一套代码生成能力同时服务传统 C/C++ 路径与上层 DSL（Triton / TileLang 都依赖 LLVM）。

已完成能力：

* 矩阵指令的描述、编码与汇编 / 反汇编支持；
* 编程模型优化；
* 矩阵指令与 RISC-V 标量、向量指令之间的执行顺序与同步关系处理；
* 为上层算子编译器提供底层指令映射接口（buddy-mlir 路径）。

源码版本与可选预编译包见本章末的版本对应表。

## LLVM 后端

* 支持 `ZAMES`（矩阵计算）与 `ZMASYNC`（矩阵同步）两个 feature；
* 提供 intrinsic 与内建类型，负责伪指令展开、配置指令的自动插入与去重；
* 矩阵寄存器按 callee-saved 约定处理：跨调用时整寄存器 spill / reload。

### 用法

```bash
llvm-mc -triple=riscv64 -mattr=+zames input.s
llvm-mc -triple=riscv64 -mattr=+zmasync input.s
llc -mtriple=riscv64 -mattr=+zames input.ll
```

指令、寄存器与 `mcfg` 编码见[指令集扩展](../isa/instruction-set.md#sec:xsai-instruction-set)。

## Triton

### 编译路径

```text
Triton IR → Linalg → Zames → LLVM IR → 汇编
```

这条链上没有"一步到位"的翻译，而是逐级 **Lowering**：每一级把上层 IR 降到更接近硬件的形式，由下一级接手。另有 `TileLang → zames intrinsic` 一条独立路径。Triton-riscv 的 xscpu 后端正在接入 JIT。

### 编程模型要求

传统 Triton 面向 GPU 类并行设备，而 XSAI 在保留 CPU 编程模型的前提下用矩阵扩展提供高吞吐，两者执行模型有差异。因此需要处理：

1. Triton 的 tile 抽象与矩阵操作之间的映射；
2. tile 数据布局、访存形式及硬件资源约束；
3. 异步矩阵执行与程序同步语义；
4. 矩阵计算与标量、向量操作之间的协同；
5. 针对不同矩阵形状及数据类型的性能优化。

显式异步操作可用 `tl.regreset`、`tl.release`、`tl.acquire`、`tl.fence` 表达；矩阵路径需要显式表达 tile 尺寸、K 分块与同步点。

### 环境搭建

三份源码来自同一组织下的仓库：

```bash
export DSL_ROOT="$(pwd)"      # 三份源码都放在这个目录下
git clone git@github.com:OurCompArchGroup/buddy-mlir.git
git clone git@github.com:OurCompArchGroup/xsai-blas.git
git clone git@github.com:OurCompArchGroup/triton-riscv.git

cd "$DSL_ROOT/buddy-mlir" && git checkout zames-backend-v1-no-ra
```

以下各代码块都假定 `DSL_ROOT` 仍在同一 shell 会话中；若分多次执行，请在每个新 shell 里重新 `export DSL_ROOT=<你 clone 三份源码的根目录>`。


buddy-mlir 依赖一个 LLVM 子模块；不用于开发时可只取一层以省时间和空间：

```bash
cd "$DSL_ROOT/buddy-mlir"
git submodule update --init --depth=1 llvm
export UV_CACHE_DIR=/path/to/uv_cache
uv pip install -r requirement
```

构建 LLVM / MLIR / CLANG：

```bash
cd "$DSL_ROOT/buddy-mlir" && mkdir -p llvm/build && cd llvm/build
cmake -G Ninja ../llvm \
      -DLLVM_ENABLE_PROJECTS="mlir;clang" \
      -DLLVM_ENABLE_RUNTIMES="openmp" \
      -DLIBOMP_USE_QUAD_PRECISION=OFF \
      -DLLVM_TARGETS_TO_BUILD="host;RISCV" \
      -DLLVM_ENABLE_ASSERTIONS=ON \
      -DOPENMP_ENABLE_LIBOMPTARGET=OFF \
      -DCMAKE_BUILD_TYPE=RELEASE \
      -DMLIR_ENABLE_BINDINGS_PYTHON=ON \
      -DPython3_EXECUTABLE=$(which python3)
ninja check-clang check-mlir openmp
```

构建 buddy-mlir：

```bash
cd "$DSL_ROOT/buddy-mlir" && mkdir -p build && cd build
cmake -G Ninja .. \
      -DMLIR_DIR=$PWD/../llvm/build/lib/cmake/mlir \
      -DLLVM_DIR=$PWD/../llvm/build/lib/cmake/llvm \
      -DLLVM_ENABLE_ASSERTIONS=ON \
      -DCMAKE_BUILD_TYPE=RELEASE \
      -DBUDDY_MLIR_ENABLE_PYTHON_PACKAGES=ON \
      -DPython3_EXECUTABLE=$(which python3)
ninja && ninja check-buddy
```

构建 triton-riscv。triton 必须切到与 triton-riscv 匹配的 commit，并以 patch 方式叠加改动：

```bash
export TRITON_RISCV_DIR="$DSL_ROOT/triton-riscv"
cd "$DSL_ROOT"
git clone https://github.com/triton-lang/triton.git triton
cd "$DSL_ROOT/triton" && git checkout "$(cat "${TRITON_RISCV_DIR}/triton-hash.txt")"
"${TRITON_RISCV_DIR}/scripts/apply_patches.sh" "$DSL_ROOT/triton"

uv venv && source .venv/bin/activate
uv pip install cmake ninja pytest-xdist pybind11 setuptools numpy
uv pip install --python .venv/bin/python torch \
      --index-url https://download.pytorch.org/whl/cpu

source scripts/triton-riscv-env.sh          # 首次：设置默认值
make -f Makefile.rebuild triton-rebuild MAX_JOBS=8
source scripts/triton-riscv-env.sh          # 二次：这次会带上 triton-shared-opt-path
```

`triton-riscv-env.sh` 基本只设置默认值，按上述步骤操作即可；否则需要手动 export 部分变量。

### 算子示例

以 INT8 GEMM 为例，`tl.dot` 会 Lowering 到矩阵单元的硬件矩阵指令：

```python
import torch
import triton
import triton.language as tl

@triton.jit
def gemm_amx_kernel(A_ptr, B_ptr, C_ptr, M, N, K,
                    BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr,
                    BLOCK_SIZE_K: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)

    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)
    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)
    offs_k = tl.arange(0, BLOCK_SIZE_K)

    acc = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.int32)

    for k in range(0, K, BLOCK_SIZE_K):
        A = tl.load(A_ptr + (offs_m[:, None] * K + (offs_k[None, :] + k)), dtype=tl.int8)
        B = tl.load(B_ptr + ((offs_k[:, None] + k) * N + offs_n[None, :]), dtype=tl.int8)
        acc += tl.dot(A, B)

    tl.store(C_ptr + (offs_m[:, None] * N + offs_n[None, :]), acc)
```

Lowering 过程会打印候选信息，可用于确认是否命中矩阵路径：

```text
[triton-cpu-dot-conversion]: Found AMX candidate
[triton-cpu-dot-conversion]:   TileM: 16
[triton-cpu-dot-conversion]:   TileN: 16
[triton-cpu-dot-conversion]:   TileK: 64
```

### 测试与已知失败

```bash
pytest python/examples/ \
      --ignore=python/examples/test_core.py \
      --ignore=python/examples/test_annotations.py \
      --ignore=python/examples/flaggems \
      -v
```

已知失败按现象分三类（数量随版本变动，这里只列现象与成因）：

| 现象 | 原因 |
| --- | --- |
| column / block gather-scatter | 指针分析无法结构化部分 `div` / `rem` 地址表达式，回退成 `linalg.generic`，未被 buddy 直接降级 |
| `-lower-linalg-to-vir` | 只支持 f32 的 `addf` / `maxnumf`，不支持 i32 的 `arith.maxsi` |
| swap | bufferization 错误消除了临时 buffer，把交换变成两次 `memcpy` |

## TileLang

* 已接入矩阵 intrinsic，可用于表达 GEMM 等算子；相关 PR 已合入上游；
* 目标是在矩阵单元上直接使用算子 DSL，避免手写汇编。

## buddy-mlir

* 作为多层级编译流的中间层，承接从高层算子到后端代码的 Lowering；
* 同时是 LLVM 侧提供给上层算子编译器的底层指令映射接口。

## 版本对应

| 组件 | 版本 / 分支 |
| --- | --- |
| LLVM（SDK 固定源码） | **21**；由 `VERSIONS` 固定 `llvm-project-ame` 的 commit，`llvm-mc --version` 报 `21.0.0git` |
| LLVM（可选预编译包） | 见 <https://github.com/OurCompArchGroup/llvm-release/tags>（当前 tag `20260708` 的产物名为 `llvm-20260708-proposal-14.tar.gz`）。其实际版本以该包自身的 `llvm-mc --version` 为准 |
| Triton | commit 由 `triton-riscv/triton-hash.txt` 固定，并以 `scripts/apply_patches.sh` 叠加改动 |
| buddy-mlir | 分支 `zames-backend-v1-no-ra` |
| ISA | ZAMES / ZMASYNC，实现对应 proposal-12。预编译包的产物名带 `proposal-14`，属编译器发布名，与本文所述 ISA 提案号不是同一套编号 |

模拟器与工具链的版本对应见[功能模拟器](simulators.md#sec:sw-simulators)与[子模块与版本管理](../sdk/submodules.md#sec:sdk-submodules)。
