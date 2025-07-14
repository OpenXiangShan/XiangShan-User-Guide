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

Kunminghu aims to be a general-purpose CPU targeting server and high-performance
embedded scenarios, with the goal planned to be achieved through three
iterations.

- Kunming Lake V1: Kunming Lake V1 is the architectural exploration phase of
  Kunming Lake, involving extensive restructuring based on the original Nanhu
  architecture, with SPECCPU 2006 scores improving from 10 to 15 points.
- Kunming Lake V2: The goal of Kunming Lake V2 is to refine functionality
  according to the latest RISC-V specifications, specifically based on the RVA23
  profile and server SOC spec.
- Kunming Lake V3: The goal of Kunming Lake V3 is to optimize the multi-core
  performance of a single die with 32-64 cores while supporting
  multi-compute-die functionality.

The current version is {{processor_name}}, with the goal of achieving the above
objectives through 2-3 Release versions. The overall features of Kunming Lake
are detailed in the [Features](#sec:feature) section of this chapter, while
specific specifications and instruction set support can be found in the
[@sec:instruction-set] [Instruction Set](instruction-set.md).

To support the development and deployment of Kunming Lake in target scenarios,
the Xiangshan team continues to develop and iterate other related components,
including the performance simulator xs-gem5, instruction set simulator NEMU, and
online comparison framework difftest. This document provides an overview of the
Kunming Lake processor and CPU core-related IPs. For other components, please
refer to the respective documentation.

## Introduction.
As mentioned, {{processor_name}} is a significant component of Xiangshan.
Compared to Kunming Lake V1 and Kunming Lake V2R1, it includes numerous
RISC-V-compliant instructions and IPs. Relative to Kunming Lake V2R1, it is the
first IP in the Xiangshan series to support the CHI protocol.

The {{processor_name}} series IP includes CPU Core (with L2), on-core interrupt
controller (AIA IMSIC), Timer, Debug, and other modules.

## Features {#sec:feature}

### Processor Core Features.

- Supports RV64 and its extended instruction set
- Supports RVV 1.0, VLEN 128bit x 2.
- Supports unaligned access to Cacheable space
- Supports Memory Management Unit (MMU)
- Supports up to 48-bit physical addresses, and 39-bit and 48-bit virtual
  addresses
- Supports timer interrupts and the RVA23-Sstc feature.

### Cache and TLB Features.

- ICache 64KB, supports Parity
- DCache, up to 64KB, supports ECC
- Unified L2, up to 1MB, supports ECC
- L2 serves as the bus exit for {{processor_name}} and cannot be disabled.
- Supports Level 1 and Level 2 TLB.

### Bus interface

- Supports TileLink v1 bus.
- Supports subsets of CHI Issue B and CHI Issue E.b. Transaction and flit fields
  are detailed in the bus interface chapter; CHI version configuration methods
  are described in the bus interface chapter.

### Interrupts.

- CSR compliant with AIA 1.0.
- IMSIC compliant with AIA 1.0 (Note 1).
- Compliant with RISC-V privilege NMI, provides a separate NMI signal, allowing
  for custom connections. For details, see the interrupt section.

### Debug features

- Supports DebugModule spec 0.13;
- Supports HPM;
- Supports E-trace (Note 2).
- Online correctness comparison (Difftest);
- Supports CHI minimal single-core verification environment;

Note 1: AIA aplic is not currently included in the {{processor_name}}
open-source list. If needed, please contact us.

Note 2: The E-trace off-core trace IP is not currently included in the
{{processor_name}} open-source list. For inquiries, please contact us.

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
