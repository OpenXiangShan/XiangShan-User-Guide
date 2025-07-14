---
file_authors_:
- XiaoFeibao <some@example.com>
- WangZhiZun <some@example.com>
---

# Vector {#sec:vector}

## Supported Version

Compatible with RISC-V "V" Vector Extension, Version 1.0.

## Vector programming model

The vector extension supports the following features:

* There are 32 independent vector architectural registers v0-v31. The vector
  registers have a bit width of 128 bits.
* For vector floating-point instructions, the supported element types are FP16,
  FP32, and FP64 (i.e., SEW = 16/32/64).
* For vector integer instructions, supported element types are INT8, INT16,
  INT32, and INT64 (i.e., SEW = 8/16/32/64).
* Support for vector register grouping to enhance the efficiency of vector
  operations. Four grouping modes are supported: groups containing 1/2/4/8
  vector registers, divided into 32/16/8/4 groups.

## Vector control register

There are 7 non-privileged CSRs:

* vstart

  The vector start position register specifies the starting element position
  when executing vector instructions. The vstart register is cleared to zero
  after each vector instruction execution. In most cases, software does not need
  to modify vstart. Only vector store instructions support a non-zero vstart;
  all vector arithmetic instructions require vstart = 0, otherwise, an illegal
  instruction exception will be raised.

* vxsat

  Fixed-point overflow flag register, where only bit0 is valid, indicating
  whether a fixed-point instruction has produced an overflow result.

* vxrm

  Fixed-point rounding mode register supports four rounding modes: round toward
  positive infinity, round to nearest even, round toward zero, and round to
  nearest odd.

* vcsr

  Vector Control and Status Registers.

* vl

  The Vector Length Register (vl) specifies the element range updated by vector
  instructions in the destination register. Generally, vector instructions
  update elements in the destination register with indices less than vl.
  Elements with indices greater than or equal to vl are either set to all 1s or
  retain their original values based on the vta setting.

* vtype

  Vector data type register, which sets the basic data attributes for vector
  calculations, including: vill, vsew, vlmul, vta, and vma.

* vlenb

  Vector Length Register (VLEN), expressed in bytes to indicate vector width.
* Additionally, vector state maintenance functionality is supported. The VS bits
  are defined at mstatus[10:9], which can be used to determine whether
  vector-related registers need to be saved during context switches.

## Vector-related exceptions

Vector instructions can be categorized into three major types:

* Vector operations
* Vector load
* Vector store

Vector operations do not trigger exceptions.

Vector Load and Vector Store are collectively referred to as vector memory
access.

Vector memory access can trigger exceptions as specified in the manual.

Vector Load may trigger:

* 3 BreakPoint
* 4 Load address misaligned
* 5 Load access fault
* 13 Load page fault
* 21 Load guest page fault

Vector Store may trigger:

* 3 BreakPoint
* 6 Store address misaligned
* 7 Store access fault
* 15 Store page fault
* 23 Store guest page fault

In the implementation, vector memory access is not permitted for MMIO. Vector
memory access to MMIO will trigger a Load/Store access fault exception.

In vector memory access that triggers an exception, the implementation follows
the specifications outlined in the manual:

1. For non-fault-only-first instructions, the vstart register is set to the
   element position where the exception was triggered. The exception-triggering
   element retains its original value, while elements following the exception
   are processed according to Tail and Mask configurations.
2. Fault-only-first instruction: if the exception occurs at the first element,
   an exception will be triggered. Otherwise, the vl register will be set to the
   position of the element causing the exception, and no exception will be
   triggered. The element triggering the exception retains its original value,
   while elements after the exception are processed according to the Tail and
   Mask configurations.
3. Segment instructions trigger exceptions per segment. After an exception
   occurs within a segment, the vstart register is set to the segment position
   where the exception was triggered. Elements preceding the
   exception-triggering element in the segment are accessed and executed
   normally.
