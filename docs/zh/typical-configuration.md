## 典型配置
以下是昆明湖 V2 核心的典型配置：

| Feature                | KUNMINGHU (XiangShan-3)        |
| ---------------------- | ------------------------------ |
| 流水级数               | 13                             |
| 译码宽度               | 6                              |
| 重命名宽度             | 6                              |
| 提交宽度               | 8                              |
| ROB                    | 160                            |
| RAB                    | 256                            |
| 物理寄存器宽度(整数)   | 224                            |
| 物理寄存器宽度(浮点)   | 192                            |
| 物理寄存器宽度(向量)   | 128                            |
| Load 队列              | 72                             |
| Store 队列             | 56                             |
| 发射队列(整数)         | 24 entries x 4                 |
| 发射队列(浮点)         | 18 entries x 3                 |
| 发射队列(内存)         | 16 entries                     |
| L1 ICache              | 64KB/128KB (configurable)      |
| L1 DCache              | 64KB/128KB (configurable)      |
| L2 Cache               | 512KB~1MB, 8-way, inclusive    |
| L3 Cache               | 2MB~16MB, 8-way, non inclusive |
| 物理寄存器堆大小(整数) | 224x64 bits                    |
| 物理寄存器堆大小(浮点) | 192x64 bits                    |
| 分支预测错误惩罚       | 13 cycles                      |
| ECC支持                | Y                              |
| 虚拟内存支持           | Y (Sv39/Sv48)                  |
| 物理内存保护           | Y                              |
| 虚拟化                 | Y                              |
| 向量                   | Y                              |

## 指令延迟

绝大部分算术指令都是单周期指令（延迟为 1）。多周期指令在下表中列出：

### 整数操作

| 指令/操作      | 延迟 | 描述                    |
| -------------- | ---- | ----------------------- |
| `LD`           | 4    | 取数操作（load-to-use） |
| `MUL`          | 3    | 整数乘法                |
| `DIV` (32-bit) | 4~11 | 整数除法（SRT16）       |
| `DIV` (64-bit) | 4~19 | 整数除法（SRT16）       |

### 浮点操作

| 指令/操作                             | 延迟 | 描述                                |
| ------------------------------------- | ---- | ----------------------------------- |
| `FMUL`                                | 4    | 浮点乘法运算                        |
| `FMA`                                 | 4    | 浮点乘法加法指令                    |
| `FDIV` (32-bit)                       | 3~9  | 浮点除法运算                        |
| `FDIV` (64-bit)                       | 3~14 | 浮点除法运算                        |
| `FSQRT` (32-bit)                      | 3~10 | 浮点平方根运算                      |
| `FSQRT` (64-bit)                      | 3~16 | 浮点平方根运算                      |
| `FCVT` (F2I, F2F)                     | 3    | 浮点转换运算                        |
| `FCVT` (I2F)                          | 3    | 整数转浮点运算                      |
| `FMV` (I2F)                           | 1    | 整数到浮点移动操作                  |
| `FMV` (F2I)                           | 3    | 浮点到整数移动操作                  |
| `FCMP`, `FMIN/MAX`, `FCLASS`, `FSGNJ` | 2    | 浮点比较/最小最大/分类/符号注入操作 |

###  位操作

| 指令/操作                                      | 延迟 | 描述                    |
| ---------------------------------------------- | ---- | ----------------------- |
| `CLZ(W)`, `CTZ(W)`, `CPOP(W)`                  | 3    | 前导零/尾零计数，位计数 |
| `CLMUL(H/R)`                                   | 3    | 无进位乘法              |
| `XPERM`                                        | 3    | 交叉排列                |
| `AES64*`, `SHA256*`, `SHA512*`, `SM3*`, `SM4*` | 3    | 标量加密操作            |

### 存储操作

| 指令/操作 | 延迟 | 描述     |
| --------- | ---- | -------- |
| `ST`      | 4    | 存储操作 |

### 执行单元配置

昆明湖 V2 具有以下执行单元：

**整数执行单元 (4 发射队列, 每个队列 24 项):**
- ALU0: ALU + MUL + BKU
- ALU1: ALU + MUL + BKU
- ALU2: ALU
- ALU3: ALU
- BJU0: BRU + JMP
- BJU1: BRU + JMP
- BJU2: BRU + JMP + I2F + I2V + VSet
- BJU3: CSR + Fence + DIV

**浮点执行单元 (3 发射队列, 每个队列 18 项):**
- FEX0: FALU + FMA + FCVT + F2V
- FEX1: FDIV
- FEX2: FALU + FMA
- FEX3: FDIV
- FEX4: FALU + FMA

**访存单元:**
- 3 Load Units (LDU)
- 2 Store Address Units (STA)
- 2 Store Data Units (STD)

**向量执行单元:**
- VFEX0: VFMA + VIALU + VIMAC + VPPU
- VFEX1: VFALU + VFCVT + VIPU + VSet
- VFEX2: VFMA + VIALU
- VFEX3: VFALU
- VFEX4: VFDIV + VIDIV
