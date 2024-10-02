---
file_authors_:
- zehao Liu <liuzehao19@mails.ucas.ac.cn> 
---

## 性能监测单元

{{var_processor_name}} 性能监测单元（PMU）根据 RISC-V 特权手册实现了基本的硬件性能监测功能，并额外支持 sstc 以及 sscofpmf 拓展，用于统计处理器运行中的部分硬件信息和线程信息，供软件开发人员进行程序优化。

性能监测单元统计的软硬件信息主要分为以下几种：

* 硬件线程执行的时钟周期数 (cycle)
* 硬件线程已提交的指令数 (minstret)
* 硬件定时器 (time)
* 处理器关键部件性能事件统计 (hpmcounter3 - hpmcouonter31，countovf)

### PMU 的编程模型

#### PMU 的基本用法

PMU 的基本用法如下：

* 通过 mcountinhibit 寄存器关闭所有性能事件监测。
* 初始化各个监测单元性能事件计数器，包括：mcycle, minstret, mhpmcounter3 - mhpmcounter31。
* 配置各个监测单元性能事件选择器，包括: mhpmcounter3 - mhpmcounter31。香山昆明湖架构对每个事件选择器可以配置最多四种事件组合，将事件索引值、事件组合方法、采样特权级写入事件选择器后，即可在规定的采样特权级下对配置的事件正常计数，并根据组合后结果累加到事件计数器中。
* 配置 xcounteren 进行访问权限授权
* 通过 mcountinhibit 寄存器开启所有性能事件监测，开始计数。

#### PMU 事件溢出中断

昆明湖性能监测单元发起的溢出中断 LCOFIP，统一中断向量号为12，中断的使能以及处理过程与普通私有中断一致，详见 [异常与中断](./exception-and-interrupt.md)

### PMU 相关的控制寄存器

#### 机器模式性能事件计数禁止寄存器 (MCOUNTINHIBIT)

机器模式性能事件计数禁止寄存器 (mcountinhibit)，是32位 WARL 寄存器，主要用与控制硬件性能监测计数器是否计数。在不需要性能分析的场景下，可以关闭计数器，以降低处理器功耗。

Table: 机器模式性能事件计数禁止寄存器说明  

| 名称   | 位域   | 读写  | 行为                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| HPMx  | 31:4   | RW  | mhpmcounterx 寄存器禁止计数位: <br>0: 正常计数 <br>1: 禁止计数| 0 |
| IR    | 3      | RW  | minstret 寄存器禁止计数位 <br>0: 正常计数 <br>1: 禁止计数 | 0 |
| -     | 2      | RO 0| 保留位                      | 0 |
| CY    | 1      | RW  | mcycle 寄存器禁止计数位 <br>0: 正常计数 <br>1: 禁止计数    | 0 |

#### 机器模式性能事件计数器访问授权寄存器 (MCOUNTEREN)

机器模式性能事件计数器访问授权寄存器 (mcounteren)，是32位 WARL 寄存器，主要用于控制用户态性能监测计数器在机器模式以下特权级模式 (HS-mode/VS-mode/HU-mode/VU-mode) 中的访问权限。

Table: 机器模式性能事件计数器访问授权寄存器说明

| 名称   | 位域   | 读写  | 行为                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| HPMx  | 31:4   | RW  | hpmcounterenx 寄存器 M-mode 以下访问权限位: <br>0: 访问 hpmcounterx 报非法指令异常 <br>1: 允许正常访问 hpmcounterx | 0 |
| IR    | 3      | RW  | instret 寄存器 M-mode 以下访问权限位 <br>0: 访问 instret 报非法指令异常 <br>1: 允许正常访问 | 0 |
| TM    | 2      | RW  | time/stimecmp 寄存器 M-mode 以下访问权限位 <br>0: 访问 time 报非法指令异常 <br>1: 允许正常访问 | 0 |
| CY    | 1      | RW  | cycle 寄存器 M-mode 以下访问权限位 <br>0: 访问 cycle 报非法指令异常 <br>1: 允许正常访问 | 0 |

#### 监督模式性能事件计数器访问授权寄存器 (SCOUNTEREN)

监督模式性能事件计数器访问授权寄存器 (scounteren)，是32位 WARL 寄存器，主要用于控制用户态性能监测计数器在用户模式 (HU-mode/VU-mode) 中的访问权限。

Table: 监督模式性能事件计数器访问授权寄存器说明

| 名称   | 位域   | 读写  | 行为                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| HPMx  | 31:4   | RW  | hpmcounterenx 寄存器 用户模式访问权限位: <br>0: 访问 hpmcounterx 报非法指令异常 <br>1: 允许正常访问 hpmcounterx | 0 |
| IR    | 3      | RW  | instret 寄存器 用户模式访问权限位 <br>0: 访问 instret 报非法指令异常 <br>1: 允许正常访问 | 0 |
| TM    | 2      | RW  | time 寄存器 用户模式访问权限位 <br>0: 访问 time 报非法指令异常 <br>1: 允许正常访问 | 0 |
| CY    | 1      | RW  | cycle 寄存器 用户模式访问权限位 <br>0: 访问 cycle 报非法指令异常 <br>1: 允许正常访问 | 0 |

#### 虚拟化模式性能事件计数器访问授权寄存器 (HCOUNTEREN)

虚拟化模式性能事件计数器访问授权寄存器 (hcounteren)，是32位 WARL 寄存器，主要用于控制用户态性能监测计数器在客户虚拟机 (VS-mode/VU-mode) 中的访问权限。

Table: 监督模式性能事件计数器访问授权寄存器说明

| 名称   | 位域   | 读写  | 行为                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| HPMx  | 31:4   | RW  | hpmcounterenx 寄存器 客户虚拟机访问权限位: <br>0: 访问 hpmcounterx 报非法指令异常 <br>1: 允许正常访问 hpmcounterx | 0 |
| IR    | 3      | RW  | instret 寄存器 客户虚拟机访问权限位 <br>0: 访问 instret 报非法指令异常 <br>1: 允许正常访问 | 0 |
| TM    | 2      | RW  | time/vstimecmp(via stimecmp) 寄存器 客户虚拟机访问权限位 <br>0: 访问 time 报非法指令异常 <br>1: 允许正常访问 | 0 |
| CY    | 1      | RW  | cycle 寄存器 客户虚拟机访问权限位 <br>0: 访问 cycle 报非法指令异常 <br>1: 允许正常访问 | 0 |

#### 监督模式时间比较寄存器 (STIMECMP)

监督模式时间比较寄存器 (stimecmp)， 是64位 WARL 寄存器，主要用于管理监督模式下的定时器中断 (STIP)。

STIMECMP 寄存器行为说明：

* 复位值为64位无符号数 64'hffff_ffff_ffff_ffff。
* 在 menvcfg.STCE 为 0 且当前特权级低于 M-mode (HS-mode/VS-mode/HU-mode/VU-mode) 时，访问 stimecmp 寄存器产生非法指令异常，且不产生 STIP 中断。
* stimecmp 寄存器是 STIP 中断产生源头：在进行无符号整数比较 time ≥ stimecmp 时，拉高STIP中断等待信号。
* 监督模式软件可以通过写 stimecmp 控制定时器中断的产生。

#### 客户虚拟机监督模式时间比较寄存器 (VSTIMECMP)

客户虚拟机监督模式时间比较寄存器 (vstimecmp)，是64位 WARL 寄存器，主要用于管理客户虚拟机监督模式下的定时器中断 (STIP)。

VSTIMECMP 寄存器行为说明：

* 复位值为64位无符号数 64'hffff_ffff_ffff_ffff。
* 在 henvcfg.STCE 为 0 或者 hcounteren.TM 时，通过 stimecmp 寄存器访问 vstimecmp 寄存器产生 虚拟非法指令异常，且不产生 VSTIP 中断。
* vstimecmp 寄存器是 VSTIP 中断产生源头：在进行无符号整数比较 time + htimedelta ≥ vstimecmp 时，拉高VSTIP中断等待信号。
* 客户虚拟机监督模式软件可以通过写 vstimecmp 控制 VS-mode 下定时器中断的产生。

### PMU 相关的性能事件选择器

机器模式性能事件选择器 (mhpmevent3 - 31)，是64为 WARL 寄存器，用于选择每个性能事件计数器对应的性能事件。在香山昆明湖架构中，每个计数器可以配置最多四个性能事件进行组合计数。用户将事件索引值、事件组合方法、采样特权级写入指定事件选择器后，该事件选择器所匹配的事件计数器开始正常计数。

Table: 机器模式性能事件选择器说明

| 名称   | 位域   | 读写  | 行为                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| OF  | 63 | RW  | 性能计数上溢标志位:<br> 0: 对应性能计数器溢出时置1，产生溢出中断 <br> 0 对应性能计数器溢出时值不变，不产生溢出中断| 0 |
| -     | 62:55   | RW  | - | 0 |
| OP_TYPE2 | 54:50 | RW  | 计数器事件组合方法控制位 <br>5'b00000: 采用 or 操作组合 <br>5'b00001: 采用 and 操作组合  <br>5'b00010: 采用 xor 操作组合 <br>5'b00100: 采用 add 操作组合 | 0 |
| OP_TYPE1 | 49:45 | RW  | 计数器事件组合方法控制位 <br>5'b00000: 采用 or 操作组合 <br>5'b00001: 采用 and 操作组合  <br>5'b00010: 采用 xor 操作组合 <br>5'b00100: 采用 add 操作组合 | 0 |
| OP_TYPE0 | 44:40 | RW  | 计数器事件组合方法控制位 <br>5'b00000: 采用 or 操作组合 <br>5'b00001: 采用 and 操作组合  <br>5'b00010: 采用 xor 操作组合 <br>5'b00100: 采用 add 操作组合 | 0 |
| EVENT3 | 39:30 | RW  | 计数器性能事件索引值 <br>0: 对应的事件计数器不计数 <br>1: 对应的事件计数器对事件 EVENT3 计数 | - |
| EVENT2 | 29:20 | RW  | 计数器性能事件索引值 <br>0: 对应的事件计数器不计数 <br>1: 对应的事件计数器对事件 EVENT2 计数 | - |
| EVENT1 | 19:10 | RW  | 计数器性能事件索引值 <br>0: 对应的事件计数器不计数 <br>1: 对应的事件计数器对事件 EVENT1 计数 | - |
| EVENT0 |  9: 0 | RW  | 计数器性能事件索引值 <br>0: 对应的事件计数器不计数 <br>1: 对应的事件计数器对事件 EVENT0 计数 | - |

其中，计数器事件的组合方法为：

* EVENT0 和 EVENT1 事件计数采用 OP_TYPE0 操作组合为 RESULT0。
* EVENT2 和 EVENT3 事件计数采用 OP_TYPE1 操作组合为 RESULT1。
* RESULT0 和 RESULT1 组合记过采用 OP_TYPE2 操作组合为 RESULT2。
* RESULT2 累加到对应事件计数器。

对性能事件选择器中事件索引值部分复位值规定如下：

* 由于目前昆明湖架构定义的各个性能事件集合大小不超过150，因此规定 EVENTx 高两位复位固定值：
* 对于mhpmevent 3-10: 40'h0000000000
* 对于mhpmevent11-18: 40'h4010040100
* 对于mhpmevent19-26: 40'h8020080200
* 对于mhpmevent27-31: 40'hc0300c0300

昆明湖架构将提供的性能事件根据来源分为四类，包括：前端，后端，访存，缓存，同时将计数器分为四部分，分别记录来自上述四个源头的性能事件：

* 前端：mhpmevent 3-10
* 后端：mhpmevent11-18
* 访存：mhpmevent19-26
* 缓存：mhpmevent27-31

Table: 昆明湖前端性能事件索引表

| 索引  | 事件                        |
|-------|-----------------------------|
| 0     | noEvent                     |
| 1     | frontendFlush               |
| 2     | ifu_req                     |
| 3     | ifu_miss                    |
| 4     | ifu_req_cacheline_0         |
| 5     | ifu_req_cacheline_1         |
| 6     | ifu_req_cacheline_0_hit     |
| 7     | ifu_req_cacheline_1_hit     |
| 8     | only_0_hit                  |
| 9     | only_0_miss                 |
| 10    | hit_0_hit_1                 |
| 11    | hit_0_miss_1                |
| 12    | miss_0_hit_1                |
| 13    | miss_0_miss_1               |
| 14    | IBuffer_Flushed             |
| 15    | IBuffer_hungry              |
| 16    | IBuffer_1_4_valid           |
| 17    | IBuffer_2_4_valid           |
| 18    | IBuffer_3_4_valid           |
| 19    | IBuffer_4_4_valid           |
| 20    | IBuffer_full                |
| 21    | Front_Bubble                |
| 22    | icache_miss_cnt             |
| 23    | icache_miss_penalty         |
| 24    | bpu_s2_redirect             |
| 25    | bpu_s3_redirect             |
| 26    | bpu_to_ftq_stall            |
| 27    | mispredictRedirect          |
| 28    | replayRedirect              |
| 29    | predecodeRedirect           |
| 30    | to_ifu_bubble               |
| 31    | from_bpu_real_bubble        |
| 32    | BpInstr                     |
| 33    | BpBInstr                    |
| 34    | BpRight                     |
| 35    | BpWrong                     |
| 36    | BpBRight                    |
| 37    | BpBWrong                    |
| 38    | BpJRight                    |
| 39    | BpJWrong                    |
| 40    | BpIRight                    |
| 41    | BpIWrong                    |
| 42    | BpCRight                    |
| 43    | BpCWrong                    |
| 44    | BpRRight                    |
| 45    | BpRWrong                    |
| 46    | ftb_false_hit               |
| 47    | ftb_hit                     |
| 48    | fauftb_commit_hit           |
| 49    | fauftb_commit_miss          |
| 50    | tage_tht_hit                |
| 51    | sc_update_on_mispred        |
| 52    | sc_update_on_unconf         |
| 53    | ftb_commit_hits             |
| 54    | ftb_commit_misses           |

Table: 昆明湖后端性能事件索引表

| 索引  | 事件                                     |
|-------|------------------------------------------|
| 0     | noEvent                                  |
| 1     | decoder_fused_instr                      |
| 2     | decoder_waitInstr                        |
| 3     | decoder_stall_cycle                      |
| 4     | decoder_utilization                      |
| 5     | rename_in                                |
| 6     | rename_waitinstr                         |
| 7     | rename_stall                             |
| 8     | rename_stall_cycle_walk                  |
| 9     | rename_stall_cycle_dispatch              |
| 10    | rename_stall_cycle_int                   |
| 11    | rename_stall_cycle_fp                    |
| 12    | rename_stall_cycle_vec                   |
| 13    | rename_stall_cycle_v0                    |
| 14    | rename_stall_cycle_vl                    |
| 15    | me_freelist_1_4_valid                    |
| 16    | me_freelist_2_4_valid                    |
| 17    | me_freelist_3_4_valid                    |
| 18    | me_freelist_4_4_valid                    |
| 19    | std_freelist_1_4_valid                   |
| 20    | std_freelist_2_4_valid                   |
| 21    | std_freelist_3_4_valid                   |
| 22    | std_freelist_4_4_valid                   |
| 23    | std_freelist_1_4_valid                   |
| 24    | std_freelist_2_4_valid                   |
| 25    | std_freelist_3_4_valid                   |
| 26    | std_freelist_4_4_valid                   |
| 27    | std_freelist_1_4_valid                   |
| 28    | std_freelist_2_4_valid                   |
| 29    | std_freelist_3_4_valid                   |
| 30    | std_freelist_4_4_valid                   |
| 31    | std_freelist_1_4_valid                   |
| 32    | std_freelist_2_4_valid                   |
| 33    | std_freelist_3_4_valid                   |
| 34    | std_freelist_4_4_valid                   |
| 35    | dispatch_in                              |
| 36    | dispatch_empty                           |
| 37    | dispatch_utili                           |
| 38    | dispatch_waitinstr                       |
| 39    | dispatch_stall_cycle_lsq                 |
| 40    | dispatch_stall_cycle_rob                 |
| 41    | dispatch_stall_cycle_int_dq              |
| 42    | dispatch_stall_cycle_fp_dq               |
| 43    | dispatch_stall_cycle_ls_dq               |
| 44    | dispatchq1_in                            |
| 45    | dispatchq1_out                           |
| 46    | dispatchq1_out_try                       |
| 47    | dispatchq1_fake_block                    |
| 48    | dispatchq1_1_4_valid                     |
| 49    | dispatchq1_2_4_valid                     |
| 50    | dispatchq1_3_4_valid                     |
| 51    | dispatchq1_4_4_valid                     |
| 52    | dispatchq2_in                            |
| 53    | dispatchq2_out                           |
| 54    | dispatchq2_out_try                       |
| 55    | dispatchq2_fake_block                    |
| 56    | dispatchq2_1_4_valid                     |
| 57    | dispatchq2_2_4_valid                     |
| 58    | dispatchq2_3_4_valid                     |
| 59    | dispatchq2_4_4_valid                     |
| 60    | dispatchq3_in                            |
| 61    | dispatchq3_out                           |
| 62    | dispatchq3_out_try                       |
| 63    | dispatchq3_fake_block                    |
| 64    | dispatchq3_1_4_valid                     |
| 65    | dispatchq3_2_4_valid                     |
| 66    | dispatchq3_3_4_valid                     |
| 67    | dispatchq3_4_4_valid                     |
| 68    | dispatchq4_in                            |
| 69    | dispatchq4_out                           |
| 70    | dispatchq4_out_try                       |
| 71    | dispatchq4_fake_block                    |
| 72    | dispatchq4_1_4_valid                     |
| 73    | dispatchq4_2_4_valid                     |
| 74    | dispatchq4_3_4_valid                     |
| 75    | dispatchq4_4_4_valid                     |
| 76    | rob_interrupt_num                        |
| 77    | rob_exception_num                        |
| 78    | rob_flush_pipe_num                       |
| 79    | rob_replay_inst_num                      |
| 80    | rob_commitUop                            |
| 81    | rob_commitInstr                          |
| 82    | rob_commitInstrMove                      |
| 83    | rob_commitInstrFused                     |
| 84    | rob_commitInstrLoad                      |
| 85    | rob_commitInstrBranch                    |
| 86    | rob_commitInstrLoadWait                  |
| 87    | rob_commitInstrStore                     |
| 88    | rob_walkInstr                            |
| 89    | rob_walkCycle                            |
| 90    | rob_1_4_valid                            |
| 91    | rob_2_4_valid                            |
| 92    | rob_3_4_valid                            |
| 93    | rob_4_4_valid                            |
| 94    | dispatch2Iq1_out_fire_cnt                |
| 95    | issueQueue_enq_fire_cnt                  |
| 96    | IssueQueueAluMulBkuBrhJmp_full           |
| 97    | IssueQueueAluMulBkuBrhJmp_full           |
| 98    | IssueQueueAluBrhJmpI2fVsetriwiVsetriwvf_full |
| 99    | IssueQueueAluCsrFenceDiv_full            |
| 100   | dispatch2Iq2_out_fire_cnt                |
| 101   | issueQueue_enq_fire_cnt                  |
| 102   | IssueQueueFaluFcvtF2vFmac_full           |
| 103   | IssueQueueFaluFmac_full                  |
| 104   | IssueQueueFaluFmac_full                  |
| 105   | IssueQueueFaluFmac_full                  |
| 106   | IssueQueueFdiv_full                      |
| 107   | dispatch2Iq3_out_fire_cnt                |
| 108   | issueQueue_enq_fire_cnt                  |
| 109   | IssueQueueVfmaVialuFixVimacVppuVfaluVfcvtVipuVsetrvfwvf_full |
| 110   | IssueQueueVfmaVialuFixVfaluVfcvt_full    |
| 111   | IssueQueueVfdivVidiv_full                |
| 112   | dispatch2Iq4_out_fire_cnt                |
| 113   | issueQueue_enq_fire_cnt                  |
| 114   | IssueQueueStaMou_full                    |
| 115   | IssueQueueStaMou_full                    |
| 116   | IssueQueueLdu_full                       |
| 117   | IssueQueueLdu_full                       |
| 118   | IssueQueueLdu_full                       |
| 119   | IssueQueueVlduVstuVseglduVsegstu_full    |
| 120   | IssueQueueVlduVstu_full                  |
| 121   | IssueQueueStdMoud_full                   |
| 122   | IssueQueueStdMoud_full                   |
| 123   | bt_std_freelist_1_4_valid                |
| 124   | bt_std_freelist_2_4_valid                |
| 125   | bt_std_freelist_3_4_valid                |
| 126   | bt_std_freelist_4_4_valid                |
| 127   | bt_std_freelist_1_4_valid                |
| 128   | bt_std_freelist_2_4_valid                |
| 129   | bt_std_freelist_3_4_valid                |
| 130   | bt_std_freelist_4_4_valid                |
| 131   | bt_std_freelist_1_4_valid                |
| 132   | bt_std_freelist_2_4_valid                |
| 133   | bt_std_freelist_3_4_valid                |
| 134   | bt_std_freelist_4_4_valid                |
| 135   | bt_std_freelist_1_4_valid                |
| 136   | bt_std_freelist_2_4_valid                |
| 137   | bt_std_freelist_3_4_valid                |
| 138   | bt_std_freelist_4_4_valid                |
| 139   | bt_std_freelist_1_4_valid                |
| 140   | bt_std_freelist_2_4_valid                |
| 141   | bt_std_freelist_3_4_valid                |
| 142   | bt_std_freelist_4_4_valid                |

Table: 昆明湖访存性能事件索引表

| 索引  | 事件                                |
|-------|-------------------------------------|
| 0     | noEvent                             |
| 1     | load_s0_in_fire                     |
| 2     | load_to_load_forward                |
| 3     | stall_dcache                        |
| 4     | load_s1_in_fire                     |
| 5     | load_s1_tlb_miss                    |
| 6     | load_s2_in_fire                     |
| 7     | load_s2_dcache_miss                 |
| 8     | load_s0_in_fire (LoadUnit_1)        |
| 9     | load_to_load_forward (LoadUnit_1)   |
| 10    | stall_dcache (LoadUnit_1)           |
| 11    | load_s1_in_fire (LoadUnit_1)        |
| 12    | load_s1_tlb_miss (LoadUnit_1)       |
| 13    | load_s2_in_fire (LoadUnit_1)        |
| 14    | load_s2_dcache_miss (LoadUnit_1)    |
| 15    | load_s0_in_fire (LoadUnit_2)        |
| 16    | load_to_load_forward (LoadUnit_2)   |
| 17    | stall_dcache (LoadUnit_2)           |
| 18    | load_s1_in_fire (LoadUnit_2)        |
| 19    | load_s1_tlb_miss (LoadUnit_2)       |
| 20    | load_s2_in_fire (LoadUnit_2)        |
| 21    | load_s2_dcache_miss (LoadUnit_2)    |
| 22    | sbuffer_req_valid                   |
| 23    | sbuffer_req_fire                    |
| 24    | sbuffer_merge                       |
| 25    | sbuffer_newline                     |
| 26    | dcache_req_valid                    |
| 27    | dcache_req_fire                     |
| 28    | sbuffer_idle                        |
| 29    | sbuffer_flush                       |
| 30    | sbuffer_replace                     |
| 31    | mpipe_resp_valid                    |
| 32    | replay_resp_valid                   |
| 33    | coh_timeout                         |
| 34    | sbuffer_1_4_valid                   |
| 35    | sbuffer_2_4_valid                   |
| 36    | sbuffer_3_4_valid                   |
| 37    | sbuffer_full_valid                  |
| 38    | enq (LsqWrapper)                    |
| 39    | ld_ld_violation (LsqWrapper)        |
| 40    | enq (LsqWrapper)                    |
| 41    | stld_rollback (LsqWrapper)          |
| 42    | enq (LsqWrapper)                    |
| 43    | deq (LsqWrapper)                    |
| 44    | deq_block (LsqWrapper)              |
| 45    | replay_full (LsqWrapper)            |
| 46    | replay_rar_nack (LsqWrapper)        |
| 47    | replay_raw_nack (LsqWrapper)        |
| 48    | replay_nuke (LsqWrapper)            |
| 49    | replay_mem_amb (LsqWrapper)         |
| 50    | replay_tlb_miss (LsqWrapper)        |
| 51    | replay_bank_conflict (LsqWrapper)   |
| 52    | replay_dcache_replay (LsqWrapper)   |
| 53    | replay_forward_fail (LsqWrapper)    |
| 54    | replay_dcache_miss (LsqWrapper)     |
| 55    | full_mask_000 (LsqWrapper)          |
| 56    | full_mask_001 (LsqWrapper)          |
| 57    | full_mask_010 (LsqWrapper)          |
| 58    | full_mask_011 (LsqWrapper)          |
| 59    | full_mask_100 (LsqWrapper)          |
| 60    | full_mask_101 (LsqWrapper)          |
| 61    | full_mask_110 (LsqWrapper)          |
| 62    | full_mask_111 (LsqWrapper)          |
| 63    | nuke_rollback (LsqWrapper)          |
| 64    | nack_rollback (LsqWrapper)          |
| 65    | mmioCycle (LsqWrapper)              |
| 66    | mmioCnt (LsqWrapper)                |
| 67    | mmio_wb_success (LsqWrapper)        |
| 68    | mmio_wb_blocked (LsqWrapper)        |
| 69    | stq_1_4_valid (LsqWrapper)          |
| 70    | stq_2_4_valid (LsqWrapper)          |
| 71    | stq_3_4_valid (LsqWrapper)          |
| 72    | stq_4_4_valid (LsqWrapper)          |
| 73    | dcache_wbq_req                      |
| 74    | dcache_wbq_1_4_valid                |
| 75    | dcache_wbq_2_4_valid                |
| 76    | dcache_wbq_3_4_valid                |
| 77    | dcache_wbq_4_4_valid                |
| 78    | dcache_mp_req                       |
| 79    | dcache_mp_total_penalty             |
| 80    | dcache_missq_req                    |
| 81    | dcache_missq_1_4_valid              |
| 82    | dcache_missq_2_4_valid              |
| 83    | dcache_missq_3_4_valid              |
| 84    | dcache_missq_4_4_valid              |
| 85    | dcache_probq_req                    |
| 86    | dcache_probq_1_4_valid              |
| 87    | dcache_probq_2_4_valid              |
| 88    | dcache_probq_3_4_valid              |
| 89    | dcache_probq_4_4_valid              |
| 90    | load_req                            |
| 91    | load_replay                         |
| 92    | load_replay_for_data_nack           |
| 93    | load_replay_for_no_mshr             |
| 94    | load_replay_for_conflict            |
| 95    | load_req                            |
| 96    | load_replay                         |
| 97    | load_replay_for_data_nack           |
| 98    | load_replay_for_no_mshr             |
| 99    | load_replay_for_conflict            |
| 100   | load_req                            |
| 101   | load_replay                         |
| 102   | load_replay_for_data_nack           |
| 103   | load_replay_for_no_mshr             |
| 104   | load_replay_for_conflict            |
| 105   | tlbllptw_incount                    |
| 106   | tlbllptw_inblock                    |
| 107   | tlbllptw_memcount                   |
| 108   | tlbllptw_memcycle                   |
| 109   | pagetablecache_access               |
| 110   | pagetablecache_l2_hit               |
| 111   | pagetablecache_l1_hit               |
| 112   | pagetablecache_l0_hit               |
| 113   | pagetablecache_sp_hit               |
| 114   | pagetablecache_pte_hit              |
| 115   | pagetablecache_rwHarzad             |
| 116   | pagetablecache_out_blocked          |
| 117   | fsm_count                           |
| 118   | fsm_busy                            |
| 119   | fsm_idle                            |
| 120   | resp_blocked                        |
| 121   | mem_count                           |
| 122   | mem_cycle                           |
| 123   | out_blocked                         |
| 124   | ldDeqCount (MemBlockInlined)        |
| 125   | stDeqCount (MemBlockInlined)        |

Table: 昆明湖缓存性能事件索引表

| 索引  | 事件                          |
|-------|------------------------------|
| 0     | noEvent                      |
| 1     | req_buffer_merge             |
| 2     | req_buffer_flow              |
| 3     | req_buffer_alloc             |
| 4     | req_buffer_full              |
| 5     | recv_prefetch                |
| 6     | recv_normal                  |
| 7     | nrWorkingABCmshr             |
| 8     | nrWorkingBmshr               |
| 9     | nrWorkingCmshr               |
| 10    | conflictA                    |
| 11    | conflictByPrefetch           |
| 12    | conflictB                    |
| 13    | conflictC                    |
| 14    | client_dir_conflict          |
| 15    | selfdir_A_req                |
| 16    | selfdir_A_hit                |
| 17    | selfdir_B_req                |
| 18    | selfdir_B_hit                |
| 19    | selfdir_C_req                |
| 20    | selfdir_C_hit                |
| 21    | selfdir_dirty                |
| 22    | selfdir_TIP                  |
| 23    | selfdir_BRANCH               |
| 24    | selfdir_TRUNK                |
| 25    | selfdir_INVALID              |



### PMU 相关的性能事件计数器

香山昆明湖架构的性能事件计数器共分为两组，分别是：机器模式事件计数器、监督模式事件计数器、用户模式事件计数器

Table: 机器模式事件计数器列表

| 名称   | 索引   | 读写  | 介绍                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| MCYCLE   | 0xB00   | RW  | 机器模式时钟周期计数器 | - |
| MINSTRET | 0xB02   | RW  | 机器模式退休指令计数器 | - |
| MHPMCOUNTER3-31 | 0XB03-0XB1F | RW | 机器模式性能事件计数器 | 0 |

其中 MHPMCOUNTERx 计数器相应由 MHPMEVENTx控制，指定计数相应的性能事件。

监督模式事件计数器包括监督模式计数器上溢中断标志寄存器(SCOUNTOVF)

Table: 监督模式计数器上溢中断标志寄存器(SCOUNTOVF)说明

| 名称   | 位域   | 读写  | 行为                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| OFVEC   | 31:3   | RO  | mhpmcounterx 寄存器上溢标志位: <br> 1： 发生上溢 <br> 0： 没有发生上溢 | 0 |
| - | 2:0 | RO 0  | - | 0 |

scountovf 作为 mhpmcounter 寄存器 OF 位的只读映射，受 xcounteren 控制: 

* M-mode 访问 scountovf 可读正确值。
* HS-mode 访问 scountovf ：mcounteren.HPMx 为1时，对应 OFVECx 可读正确值；否则只读0。
* VS-mode 访问 scountovf : mcounteren.HPMx 以及 hcounteren.HPMx 均为1时，对应 OFVECx 可读正确值；否则只读0。

Table: 用户模式事件计数器列表

| 名称   | 索引   | 读写  | 介绍                       | 复位值 | 
|-------|--------|-----|-----------------------------|----|
| CYCLE   | 0xC00   | RO  | mcycle 寄存器用户模式只读副本 | - |
| TIME    | 0xC01   | RO  | 内存映射寄存器 mtime 用户模式只读副本 | - |
| INSTRET | 0xC02   | RO  | minstret 寄存器用户模式只读副本 | - |
| HPMCOUNTER3-31 | 0XC03-0XC1F | RO | mhpmcounter3-31 寄存器用户模式只读副本 | 0 |
