---
file_authors_:
- ZHANG Jian <zhangjian@bosc.ac.cn>
---

# Introduction {#sec:introduction}

This chapter provides an overview of the {{processor_name}} . The
{{processor_name}} is the V2R2 version of the third-generation
microarchitecture, Kunminghu, developed by the Xiangshan Processor Team at the
Beijing Insitute of Open Source Chip (hereinafter referred to as the Xiangshan
Team).

昆明湖的目标是面向服务器和高性能嵌入式场景的通用 CPU，计划通过三次迭代完成这一目标。

- 昆明湖 V1：昆明湖 V1 是昆明湖架构探索阶段，在原有南湖架构上做了大量重构，SPECCPU 2006 得分从 10 分提升到 15 分
- 昆明湖 V2：昆明湖 V2 的目标依照最新 RISC-V 规范完善功能，具体的规范来自 RVA23 profile 和 server SOC spec
- 昆明湖 V3：昆明湖 V3 的目标是优化单 die 32-64 核的多核性能，同时支持多计算die的功能

当前版本为 {{processor_name}} ，计划通过 2-3 个 Release 版本完成上述目标，昆明湖整体特性见本章
[特性](#sec:feature) 小节，具体规范和指令集支持情况见 [@sec:instruction-set]
[指令集](instruction-set.md)。

为了支持昆明湖的研发和在目标场景落地，香山团队持续开发迭代其它相关组件，包括性能模拟器 xs-gem5，指令集仿真器 NEMU，在线比较框架 difftest
等。本文是昆明湖处理器和 CPU 核相关 IP 的说明，其它组件见相应文档。

## 简介
如上所述， {{processor_name}} 是香山的重要组成部分。与昆明湖 V1 和昆明湖 V2R1 相比，增加了大量符合 RISC-V 规范的指令和
IP；与昆明湖 V2R1 相比，是香山系列 IP 中首个支持 CHI 协议的 IP。

{{processor_name}} 系列 IP 包括 CPU Core（含L2），核内中断控制器（AIA IMSIC），Timer 和 Debug 等模块。

## 特性 {#sec:feature}

### 处理器核特性

- 支持 RV64 及其扩建指令集
- 支持 RVV 1.0，VLEN 128bit x 2
- 支持 Cacheable 空间的非对齐访问
- 支持内存管理单元（MMU）
- 最大支持 48 位物理地址，支持 39 位和 48 位虚拟地址
- 支持 timer 中断，支持 RVA23-Sstc 特性

### Cache 和 TLB 特性

- ICache 64KB，支持 Parity
- DCache，最高 64KB，支持 ECC
- Unified L2，最高 1MB，支持 ECC
- L2 作为 {{processor_name}} 的总线出口，不支持关闭
- 支持一级和二级 TLB

### 总线接口

- 支持 TileLink v1 总线
- 支持 CHI Issue B 和 CHI Issue E.b 的子集，事务和 flit 字段详见总线接口章节；CHI 版本配置方法见总线接口章节

### 中断

- 符合 AIA 1.0 的 CSR
- 符合 AIA 1.0 的 IMSIC (注1)
- 符合 RISC-V priviledge 的 NMI，提供单独的 NMI 信号，允许用于自行选择连接，详见中断章节

### Debug 特性

- 支持 DebugModule spec 0.13；
- 支持 HPM；
- 支持 E-trace（注2）
- 在线正确性比较（Difftest）；
- 支持 CHI 最小单核验证环境；

注1：AIA aplic 暂不在 {{processor_name}} 开源清单中，如需要可与我们联系;

注2：E-trace 核外 trace IP 暂不在 {{processor_name}} 开源清单中，如需了解可与我们联系。

<!--
## 可配置选项
DCache size
L2 size
CHI版本

## 标准遵从
unpriviledge
priviledge

The RISC-V Instruction Set Manual: Volume II Privileged Architecture

debugmodule
E-trace
server soc spec

指令集遵从版本
Module             | Version | Status
-------------------|---------|--------
Machine ISA        | 1.13    | Draft
Supervisor ISA     | 1.13    | Draft
Smrnmi Extension   | 0.1     | Draft
Svade Extension    | 1.0     | Ratified
Svnapot Extension  | 1.0     | Ratified
Svpbmt Extension   | 1.0     | Ratified
Svinval Extension  | 1.0     | Ratified
Svadu Extension    | 1.0     | Ratified 未支持
Hypervisor ISA     | 1.0     | Ratified

## 版本说明
0.1 draft
0.5 alpha: 早期用户版本

-->
