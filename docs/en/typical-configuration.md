## Typical Configurations
Below is the typical Kunminghu V2 core configurations:

|                            | Configuration                  |
| -------------------------- | ------------------------------ |
| Pipeline stage             | 13                             |
| Decoder width              | 6                              |
| Rename width               | 6                              |
| Commit width               | 8                              |
| ROB                        | 160                            |
| RAB                        | 256                            |
| Physical register (Int)    | 224                            |
| Physical register (FP)     | 192                            |
| Physical register (Vector) | 128                            |
| Load Queue                 | 72                             |
| Store Queue                | 56                             |
| Issue Queue (Int)          | 24 entries x 4                 |
| Issue Queue (FP)           | 18 entries x 3                 |
| Issue Queue (Mem)          | 16 entries                     |
| L1 Instruction Cache       | 64KB/128KB (configurable)      |
| L1 Data Cache              | 64KB/128KB (configurable)      |
| L2 Cache                   | 512KB~1MB, 8-way, inclusive    |
| L3 Cache                   | 2MB~16MB, 8-way, non inclusive |
| Physical RF size (Int)     | 224x64 bits                    |
| Physical RF size (FP)      | 192x64 bits                    |
| Mispredict Penalty         | 13 cycles                      |
| ECC Support                | Y                              |
| Virtual Memory Support     | Y (Sv39/Sv48)                  |
| Physical memory protection | Y                              |
| Virtualization             | Y                              |
| Vector                     | Y                              |

## 指令延迟

Most arithmetic instructions are single-cycle (Latency = 1). Multi-cycle
instructions are listed as follows.

### 整数操作

| Instruction(s) / Operations | Latency      | Descriptions             |
| --------------------------- | ------------ | ------------------------ |
| `LD`                        | 4 (to use)   | Load operations (to use) |
| `MUL`                       | 3 (pipeline) | Integer multiplier       |
| `DIV` (32-bit)              | 4~11         | 整数除法（SRT16）              |
| `DIV` (64-bit)              | 4~19         | 整数除法（SRT16）              |

### Floating-Point Operations

| Instruction(s) / Operations           | Latency      | Descriptions                                                |
| ------------------------------------- | ------------ | ----------------------------------------------------------- |
| `FMUL`                                | 4 (to use)   | Floating-point multiply operations                          |
| `FMA`                                 | 4 (to use)   | Floating-point multiply-add instruction                     |
| `FDIV` (32-bit)                       | 3~9          | 浮点除法运算                                                      |
| `FDIV` (64-bit)                       | 3~14         | 浮点除法运算                                                      |
| `FSQRT` (32-bit)                      | 3~10         | 浮点平方根运算                                                     |
| `FSQRT` (64-bit)                      | 3~16         | 浮点平方根运算                                                     |
| `FCVT` (F2I, F2F)                     | 3 (pipeline) | Floating-point convert operations                           |
| `FCVT` (I2F)                          | 3 (pipeline) | Integer to float convert operations                         |
| `FMV` (I2F)                           | 1            | Integer to float move operations                            |
| `FMV` (F2I)                           | 3 (pipeline) | Float to integer move operations                            |
| `FCMP`, `FMIN/MAX`, `FCLASS`, `FSGNJ` | 2            | Floating-point compare/min/max/class/sign-inject operations |

### Bit Manipulation Operations

| Instruction(s) / Operations                    | Latency      | Descriptions                                   |
| ---------------------------------------------- | ------------ | ---------------------------------------------- |
| `CLZ(W)`, `CTZ(W)`, `CPOP(W)`                  | 3 (pipeline) | Count leading/trailing zeros, population count |
| `CLMUL(H/R)`                                   | 3 (pipeline) | Carry-less multiplication                      |
| `XPERM`                                        | 3 (pipeline) | Crossbar permutation                           |
| `AES64*`, `SHA256*`, `SHA512*`, `SM3*`, `SM4*` | 3 (pipeline) | Scalar crypto operations                       |

### Store Operations

| Instruction(s) / Operations | Latency    | Descriptions     |
| --------------------------- | ---------- | ---------------- |
| `ST`                        | 4 (to use) | Store Operations |

### Execution Units Configuration

Kunminghu V2 features the following execution units:

**Integer Execution Units (4 Issue Queues, 24 entries each):**

- ALU0: ALU + MUL + BKU
- ALU1: ALU + MUL + BKU
- ALU2: ALU
- ALU3: ALU
- BJU0: BRU + JMP
- BJU1: BRU + JMP
- BJU2: BRU + JMP + I2F + I2V + VSet
- BJU3: CSR + Fence + DIV

**Floating-Point Execution Units (3 Issue Queues, 18 entries each):**

- FEX0: FALU + FMA + FCVT + F2V
- FEX1: FDIV
- FEX2: FALU + FMA
- FEX3: FDIV
- FEX4: FALU + FMA

**Memory Execution Units:**

- 3 Load Units (LDU)
- 2 Store Address Units (STA)
- 2 Store Data Units (STD)

**Vector Execution Units:**

- VFEX0: VFMA + VIALU + VIMAC + VPPU
- VFEX1: VFALU + VFCVT + VIPU + VSet
- VFEX2: VFMA + VIALU
- VFEX3: VFALU
- VFEX4: VFDIV + VIDIV
