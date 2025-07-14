---
file_authors_:
- zengjinhong <zengjinhong21@mails.ucas.ac.cn>
---
# Registers {#sec:registers}

## General Purpose Registers

{{processor_name}} has 32 general-purpose 64-bit registers, whose functions can
be referred to in the RISC-V Unprivileged Specification, as shown in the
following table

Table: General-purpose registers

| Register | ABI Name | Description                       | Preserved |
| -------- | -------- | --------------------------------- | --------- |
| x0       | zero     | Hardwired to 0                    | \         |
| x1       | ra       | Return Address                    | Caller    |
| x2       | sp       | stack pointer                     | callee    |
| x3       | gp       | Global Pointer                    | \         |
| x4       | tp       | Thread pointer                    | \         |
| x5       | t0       | Temporary/Alternate Link Register | Caller    |
| x6-7     | t1-2     | Temporary registers               | Caller    |
| x8       | s0/fp    | Reserved Register/Frame Pointer   | callee    |
| x9       | s1       | reserved register                 | callee    |
| x10-11   | a0-1     | Function parameters/return values | Caller    |
| x12-17   | a2-7     | function parameters               | Caller    |
| x18-27   | s2-11    | reserved register                 | callee    |
| x28-31   | t3-6     | Temporary registers               | Caller    |

## Floating-Point Registers

{{processor_name}} supports the RV64 F and D extensions, featuring 32 64-bit
floating-point registers. Their functionality can be referenced in the RISC-V
manual definitions, as outlined in the following table:

Table: Floating-Point Registers

| Register | ABI Name | Description                            | Preserved |
| -------- | -------- | -------------------------------------- | --------- |
| f0-7     | ft0-7    | Floating-point Temporary Register      | Caller    |
| f8-9     | fs0-1    | Floating-point saved registers         | callee    |
| f10-11   | fa0-1    | Floating-Point Arguments/Return Values | Caller    |
| f12-17   | fa2-7    | Floating-point Argument                | Caller    |
| f18-27   | fs2-11   | Floating-point saved registers         | callee    |
| f28-31   | ft8-11   | Floating-point Temporary Register      | Caller    |

The {{processor_name}} supports both single-precision and double-precision
floating-point operations. When performing single-precision floating-point
operations, only the lower 32 bits of the floating-point registers are utilized.
Additionally, the {{processor_name}} supports half-precision operations from the
zfa extension, which exclusively use the lower 16 bits of the floating-point
registers.

### Data transfer between floating-point registers and general-purpose registers

Data transfer between general-purpose registers and floating-point registers is
possible with single-precision accuracy, achieved through transfer instructions.

General-purpose registers to floating-point registers:

1. FMV.W.X
2. FCVT.S.W
3. FCVT.S.WU
4. FCVT.S.L
5. FCVT.S.LU

Floating-point Register to General-purpose Register:

1. FMV.X.W
2. FCVT.W.S
3. FCVT.WU.S
4. FCVT.L.S
5. FCVT.LU.S

## Vector Register

{{processor_name}} supports the RV64 V extension, featuring 32 128-bit vector
architectural registers.

### Data Transfer Between Vector and General-Purpose Registers

Data transfer between vector registers and general-purpose registers is enabled
by the VMV instruction, as shown below:

1. VMV.V.X Transfer Value from General-Purpose Register to Vector Register
2. VMV.S.X transfers the value from a general-purpose register to the first
   element of a vector register
3. VMV.X.S Transfer First Element of Vector Register to General-Purpose Register

### Data transfer between vector registers and floating-point registers

Data can be transferred between vector registers and floating-point registers,
implemented by the VFMV instruction as shown below:

1. VFMV.V.F transfers the value from a floating-point register to a vector
   register
2. VFMV.S.F transfers the value from a floating-point register to the first
   element of a vector register
3. VFMV.F.S transfers the first element of a vector register to a floating-point
   register
