# Preface {.unnumbered .unlisted}

XSAI (pronounced "kesai") is an AICPU IP. It adds a matrix compute
unit and special vector operations to the general-purpose RISC-V processor
Kunminghu V2R2, keeping the CPU programming model while accelerating AI
inference — a single IP for both general-purpose compute and AI inference.

This manual documents only what XSAI **adds to or changes over** Kunminghu
V2R2, plus how to use its simulation, debug and software toolchains. For
everything identical to the baseline processor (privileged modes, interrupt
controller, bus interface, base memory-model semantics), see the corresponding
chapters of the _XiangShan Open-Source Processor User Guide_; the same baseline
chapters are kept at the end of this manual for convenience.

## Conventions {.unnumbered .unlisted}

* The manual is written as a delta against Kunminghu V2R2.
* Instruction encodings, CSR numbers and register fields follow the latest ISA
  specification and the RTL implementation.
* Example commands assume the `xsai-env` workspace; see
  [Environment Setup](verification/environment.md#sec:sim-environment).
* Paragraphs marked `TODO` are not finalised yet.

## Notice {.unnumbered .unlisted}

Copyright © 2024 - 2026 The XiangShan Team, Beijing Institute of Open Source Chip

This document is released under the
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
license. You may use, modify and redistribute it provided that you give
appropriate credit, indicate the license and note any changes. The full legal
text published by Creative Commons prevails.

This document provides status information only and may be updated from time to
time. Unless otherwise agreed, nothing herein constitutes any express or implied
warranty.

## Version history {.unnumbered .unlisted}

| Date       | Version | Notes                                  |
| ---------- | ------- | -------------------------------------- |
| 2026-10-13 | draft1  | First framework: delta and usage chapters |
