# Compiler and Operator DSLs {#sec:sw-compiler}

XSAI's compiler work concentrates on the RISC-V backend: teaching LLVM the matrix instructions and letting the upper-layer DSLs emit them. This chapter describes the toolchain's capability boundary and how to build it.

## Positioning

XSAI builds its compiler extensions on LLVM, with the changes concentrated in the
RISC-V backend. The point is not to rewrite the C/C++ front end but to add matrix
extension support inside the existing LLVM framework, so that one code generation
path serves both traditional C/C++ and the higher-level DSLs (both Triton and
TileLang depend on LLVM).

Capabilities already in place:

* description, encoding and assembly / disassembly support for the matrix
  instructions;
* programming model improvements;
* handling of execution order and synchronization between matrix instructions and
  RISC-V scalar and vector instructions;
* a low-level instruction mapping interface for higher-level operator compilers
  (the buddy-mlir path).

For the source version and the optional prebuilt packages, see the version
correspondence table at the end of this chapter.

## LLVM backend

* supports the `ZAMES` (matrix compute) and `ZMASYNC` (matrix synchronization)
  features;
* provides intrinsics and builtin types, and handles pseudo-instruction expansion
  plus automatic insertion and deduplication of configuration instructions;
* treats matrix registers by the callee-saved convention: a whole-register spill
  and reload across calls.

### Usage

```bash
llvm-mc -triple=riscv64 -mattr=+zames input.s
llvm-mc -triple=riscv64 -mattr=+zmasync input.s
llc -mtriple=riscv64 -mattr=+zames input.ll
```

For the instructions, registers and `mcfg` encodings see
[Instruction Set Extensions](../isa/instruction-set.md#sec:xsai-instruction-set).

## Triton

### Compilation path

```text
Triton IR → Linalg → Zames → LLVM IR → assembly
```

There is no single-step conversion in this chain: it proceeds by successive
**lowering**, each stage bringing the IR closer to hardware for the next stage to
take over. A separate `TileLang → zames intrinsic` path also exists. The xscpu backend of
triton-riscv is being connected to the JIT.

### Programming model requirements

Traditional Triton targets GPU-like parallel devices, whereas XSAI keeps the CPU
programming model and provides throughput through the matrix extension. The two
execution models differ, so the following must be handled:

1. the mapping between Triton's tile abstraction and matrix operations;
2. tile data layout, access patterns and hardware resource constraints;
3. asynchronous matrix execution and program synchronization semantics;
4. cooperation between matrix computation and scalar / vector operations;
5. performance optimisation for different matrix shapes and data types.

Explicit asynchronous operations can be expressed with `tl.regreset`,
`tl.release`, `tl.acquire` and `tl.fence`; the matrix path requires the tile size,
K blocking and synchronization points to be expressed explicitly.

### Setting up the environment

Three source trees come from repositories under the same organisation:

```bash
export DSL_ROOT="$(pwd)"      # the three source trees live here
git clone git@github.com:OurCompArchGroup/buddy-mlir.git
git clone git@github.com:OurCompArchGroup/xsai-blas.git
git clone git@github.com:OurCompArchGroup/triton-riscv.git

cd "$DSL_ROOT/buddy-mlir" && git checkout zames-backend-v1-no-ra
```

The blocks below assume `DSL_ROOT` is still set in the same shell session. If you
run them in separate shells, re-export it in each new shell with
`export DSL_ROOT=<the root where you cloned the three source trees>`.


buddy-mlir depends on an LLVM submodule; a shallow copy is enough when you are not
developing it:

```bash
cd "$DSL_ROOT/buddy-mlir"
git submodule update --init --depth=1 llvm
export UV_CACHE_DIR=/path/to/uv_cache
uv pip install -r requirement
```

Build LLVM / MLIR / CLANG:

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

Build buddy-mlir:

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

Build triton-riscv. Triton must be checked out at the commit matching triton-riscv,
with the changes applied as patches:

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

source scripts/triton-riscv-env.sh          # first time: sets the defaults
make -f Makefile.rebuild triton-rebuild MAX_JOBS=8
source scripts/triton-riscv-env.sh          # second time: now also sets triton-shared-opt-path
```

`triton-riscv-env.sh` mostly just sets defaults, so following the steps above is
sufficient; otherwise some variables must be exported by hand.

### Operator example

For an INT8 GEMM, `tl.dot` is lowered onto the matrix unit:

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

The lowering prints candidate information, which confirms whether the matrix path
was hit:

```text
[triton-cpu-dot-conversion]: Found AMX candidate
[triton-cpu-dot-conversion]:   TileM: 16
[triton-cpu-dot-conversion]:   TileN: 16
[triton-cpu-dot-conversion]:   TileK: 64
```

### Tests and known failures

```bash
pytest python/examples/ \
      --ignore=python/examples/test_core.py \
      --ignore=python/examples/test_annotations.py \
      --ignore=python/examples/flaggems \
      -v
```

Known failures fall into three groups (counts shift between versions, so only the
symptom and cause are listed):

| Symptom | Cause |
| --- | --- |
| column / block gather-scatter | pointer analysis cannot structure some `div` / `rem` address expressions, so they fall back to `linalg.generic` instead of being lowered directly by buddy |
| `-lower-linalg-to-vir` | only f32 `addf` / `maxnumf` are supported, not i32 `arith.maxsi` |
| swap | bufferization wrongly removed the temporary buffer, turning the swap into two `memcpy` calls |

## TileLang

* matrix intrinsics are connected and GEMM-like operators can be expressed; the
  relevant PRs are merged upstream;
* the goal is to use the operator DSL directly on the matrix unit and avoid
  hand-written assembly.

## buddy-mlir

* serves as the intermediate layer of the multi-level compilation flow, carrying
  the lowering from high-level operators down to backend code;
* it is also the low-level instruction mapping interface that the LLVM side
  offers to higher-level operator compilers.

## Version correspondence

| Component | Version / branch |
| --- | --- |
| LLVM (source pinned by the SDK) | **21**; the commit is pinned in `VERSIONS` for `llvm-project-ame`, and `llvm-mc --version` reports `21.0.0git` |
| LLVM (optional prebuilt package) | see <https://github.com/OurCompArchGroup/llvm-release/tags> (the `20260708` tag ships `llvm-20260708-proposal-14.tar.gz`). Its actual version is whatever that package's own `llvm-mc --version` reports |
| Triton | commit pinned by `triton-riscv/triton-hash.txt`, with changes applied by `scripts/apply_patches.sh` |
| buddy-mlir | branch `zames-backend-v1-no-ra` |
| ISA | ZAMES / ZMASYNC, implementation matching proposal-12. The prebuilt artifact is named `proposal-14`, which is a compiler release name and is not the same numbering axis as the ISA proposal number used here |

For the simulator and toolchain correspondence see
[Functional Simulators](simulators.md#sec:sw-simulators) and
[Submodules and Version Management](../sdk/submodules.md#sec:sdk-submodules).
