# 框架适配路径 {#sec:path-framework}

这一章面向要把矩阵单元接进推理框架或算子库的人（MNN / NCNN / ggml / 自研框架）。前置条件是环境已跑通（见[15 分钟上手](quickstart.md#sec:get-started)），并已了解 ZAMES 编程模型（见[指令集扩展](../isa/instruction-set.md#sec:xsai-instruction-set)）。

按下面的顺序推进，每一步的产物是下一步的输入。具体的规范与约束集中在[算子库与推理框架](../software/frameworks.md#sec:sw-frameworks)，本章只给顺序和接线方式。

## 1. 读出硬件尺寸

矩阵单元的原生 tile 尺寸是 M128 × N128 × K64，由硬件配置决定。用 CSR 探针读出实际值，按读到的值生成核，不要写死。

尺寸用错不会报错，只会算错：上板整层结果错、同一个负载在 QEMU 上却全对，通常就是这个原因。读取方式见[数据寄存器](../isa/registers.md#sec:xsai-registers)。

> 设计文档用 M-K-N 顺序写作 `128x64x128`，与这里的 M-N-K 顺序是同一套尺寸。

## 2. 找到框架原生的替换点

优先级从高到低：

| 优先级 | 替换点 | 例子 |
| --- | --- | --- |
| 1 | "换实现即换核"的函数表 | MNN 的 core functions 表 |
| 2 | arch 层的 layer 实现 | NCNN 的 registry |
| 3 | 调用点逐个替换 | 最后手段，各变体需分别插入 |

三个框架的具体位置见[框架替换点对照](../software/frameworks.md#sec:sw-frameworks)。

## 3. 把矩阵指令收进单一编译单元

所有矩阵指令集中在同一个编译单元里，其他文件只经头文件调用。这样矩阵相关的约束（寄存器钉住、同步覆盖）只需要在一个地方守住，也避免逐文件调整编译选项。

矩阵指令需要编译器开启对应扩展，实际取值是：

```text
-march=rv64gcv_zames_zmasync_zvl128b
```

MNN / NCNN / ggml 都是 CMake 工程，做法是只给装了矩阵指令的那一个源文件加 flag，其余编译单元不带：

```cmake
# MNN：source/backend/cpu/CMakeLists.txt
set_source_files_properties(${CMAKE_CURRENT_LIST_DIR}/compute/ame_xsa.c
    PROPERTIES COMPILE_OPTIONS "-march=rv64gcv_zames_zmasync_zvl128b")
```

分配操作数池的 glue 文件另需传入池的编译期参数：

```cmake
set(XSAI_RESERVED_PHYS_BASE_ADDR "0x100000000ULL" CACHE STRING "AME pool compile-time physical base")
set(XSAI_RESERVED_MEMORY_SIZE   "(6L*1024L*1024L*1024L)" CACHE STRING "AME pool compile-time size")  # 6 GiB，与 mk/memory.mk 及 DTB 一致
set_source_files_properties(${CMAKE_CURRENT_LIST_DIR}/ame/xsai_alloc.c
    PROPERTIES COMPILE_OPTIONS
    "-DRESERVED_PHYS_BASE_ADDR=${XSAI_RESERVED_PHYS_BASE_ADDR};-DRESERVED_MEMORY_SIZE=${XSAI_RESERVED_MEMORY_SIZE}")
```

NCNN 侧对应的开关是 CMake 宏 `NCNN_XSAI_AME=1`，运行期再用环境变量 `XSAI_NCNN_AME` 选择。

其余文件不带该 flag 也能正常链接——这正是单一编译单元做法的前提。

## 4. 加上退回路径

矩阵路径只在满足条件时启用：硬件尺寸可信、形状在上限内、工作量足够。任一不满足就让上层走框架原核，不要返回算错的中间结果。

判定条件与不满足时的处理见[启用条件](../software/frameworks.md#sec:sw-fw-guards)。

最容易踩的两条：

* `mrelease` / `macquire` 没覆盖所有退出分支 → 偶发错、非稳定复现；
* 基址寄存器被编译器回收 → 同样表现为偶发错。

两条都不是"有时候对"的容差问题，而是同步协议被破坏，必须修掉。

## 5. 验证并上板

先跑框架自带的算子测试，再逐级验证。通过标准与可信度排序见[验证方法](../software/frameworks.md#sec:sw-frameworks)，验证方法学见[差分验证](../verification/difftest.md#sec:debug-difftest)。

## 接进去之后

算子跑通不等于跑得快。性能低于预期时先做[性能分析路径](path-perf.md#sec:path-perf)，从软件侧阶段查起，不要先怀疑 RTL。
