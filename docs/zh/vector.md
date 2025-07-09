---
file_authors_:
- XiaoFeibao <some@example.com> 
- WangZhiZun <some@example.com>
---

# 向量 {#sec:vector}

## 版本支持

兼容 RISC-V “V” Vector Extension, Version 1.0 。

## 向量编程模型

向量扩展支持以下特性：

* 拥有 32 个独立的向量架构寄存器 v0-v31。向量寄存器的位宽为 128 位。
* 对于向量浮点指令，支持的元素类型为 FP16、FP32、FP64（即 SEW = 16/32/64）。
* 对于向量整型指令，支持的元素类型为 INT8、INT16、INT32 和 INT64（即 SEW = 8/16/32/64）。
* 支持向量寄存器的分组，以提高向量运算的效率。支持4种分组方式：每组包含 1/2/4/8 个向量寄存器，分成 32/16/8/4 个组。

## 向量控制寄存器

有 7 个非特权 CSR：

* vstart

  向量起始位置寄存器指定了执行向量指令时起始元素位置。每条向量指令执行后 vstart 都会被清零。在大多数情况下，软件不需要改动 vstart。只有向量存储指令支持非 0 的 vstart；所有的向量运算指令都要求 vstart = 0，否则会产生非法指令异常。

* vxsat

  定点溢出标志位寄存器，只有 bit0 有效，表示是否有定点指令产生溢出结果。

* vxrm

  定点舍入模式寄存器，支持4种舍入模式：向大数舍入、向偶数舍入、向零舍入和向奇数舍入。 

* vcsr

  向量控制状态寄存器。

* vl

  向量长度寄存器指定了向量指令更新目的寄存器的元素范围。一般情况下，向量指令更新目的寄存器中元素序号小于 vl 的元素，元素序号大于等于 vl 的元素根据 vta 的值写全 1 或者保留原值。

* vtype

  向量数据类型寄存器，设定向量计算的基本数据属性，包括：vill、vsew、vlmul、vta 和 vma。

* vlenb

  向量位宽寄存器, 以字节为单位表示向量位宽。
* 
此外还支持向量状态维护功能，在 mstatus[10:9] 处定义了 VS 位，可以用于判断上下文切换时，是否需要保存向量相关的寄存器。

## 向量相关异常

向量指令可以分为三大类：

* 向量运算
* 向量 load
* 向量 store

向量运算不会触发异常。

向量 Load 与向量 Store 统称为向量访存。

向量访存可以引起手册规定的异常。

向量 Load 会引发:

* 3   BreakPoint
* 4   Load address misaligned
* 5   Load access fault
* 13  Load page fault
* 21  Load guest page fault

向量 Store 会引发:

* 3   BreakPoint
* 6   Store address misaligned
* 7   Store access fault
* 15  Store page fault
* 23  Store guest page fault

实现中，向量访存不允许访存 MMIO，对于 MMIO 的向量访存会引发 Load/Store access fault 异常。

在向量访存中触发异常，根据手册规定实现如下:

1. 非 fault-only-first 指令，将会设置 vstart 寄存器为触发异常的元素位置。触发异常的元素保留原值，异常元素之后的元素会根据 Tail 与 Mask 的配置来进行处理。
2. fault-only-first 指令，若异常的元素为第一个元素，则会触发异常。否则将会设置 vl 寄存器为异常的元素位置，且不触发异常。触发异常的元素保留原值，异常元素之后的元素会根据 Tail 与 Mask 的配置来进行处理。
3. segment 指令以 segment 为单位引发异常，在 segment 中引发异常之后，将会设置 vstart 寄存器为触发异常的 segment 位置。segment 中触发异常的元素之前的元素将会正常的被访问执行。
