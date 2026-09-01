---
file_authors_:
- zehao Liu <liuzehao19@mails.ucas.ac.cn> 
---

# 性能监测单元 {#sec:performance-monitor}

{{processor_name}} 性能监测单元（PMU）根据 RISC-V 特权手册实现了基本的硬件性能监测功能，并额外支持 sstc 以及
sscofpmf 拓展，用于统计处理器运行中的部分硬件信息和线程信息，供软件开发人员进行程序优化。

性能监测单元统计的软硬件信息主要分为以下几种：

* 硬件线程执行的时钟周期数 (cycle)
* 硬件线程已提交的指令数 (minstret)
* 硬件定时器 (time)
* 处理器关键部件性能事件统计 (hpmcounter3 - hpmcouonter31，countovf)

## PMU 的编程模型

### PMU 的基本用法

PMU 的基本用法如下：

* 通过 mcountinhibit 寄存器关闭所有性能事件监测。
* 初始化各个监测单元性能事件计数器，包括：mcycle, minstret, mhpmcounter3 - mhpmcounter31。
* 配置各个监测单元性能事件选择器，包括: mhpmevent3 - mhpmevent31。 {{processor_name}}
  对每个事件选择器可以配置最多四种事件组合，将事件索引值、事件组合方法、采样特权级写入事件选择器后，即可在规定的采样特权级下对配置的事件正常计数，并根据组合后结果累加到事件计数器中。
* 配置 xcounteren 进行访问权限授权
* 通过 mcountinhibit 寄存器开启所有性能事件监测，开始计数。

### PMU 事件溢出中断

{{processor_name}} 性能监测单元发起的溢出中断 LCOFIP，统一中断向量号为12，中断的使能以及处理过程与普通私有中断一致，详见
[异常与中断](./exception-and-interrupt.md)

## PMU 相关的控制寄存器

### 机器模式性能事件计数禁止寄存器 (MCOUNTINHIBIT)

机器模式性能事件计数禁止寄存器 (mcountinhibit)，是32位 WARL
寄存器，主要用与控制硬件性能监测计数器是否计数。在不需要性能分析的场景下，可以关闭计数器，以降低处理器功耗。

Table: 机器模式性能事件计数禁止寄存器说明

+--------+--------+-------+--------------------------------------------+----------+
| 名称 | 位域 | 读写 | 行为 | 复位值 |
+========+========+=======+============================================+==========+
| HPMx | 31:3 | RW | mhpmcounterx 寄存器禁止计数位: | 0 | | | | | | | | | | | 0: 正常计数 |
| | | | | | | | | | | 1: 禁止计数 | |
+--------+--------+-------+--------------------------------------------+----------+
| IR | 2 | RW | minstret 寄存器禁止计数位: | 0 | | | | | | | | | | | 0: 正常计数 | | | | | |
| | | | | | 1: 禁止计数 | |
+--------+--------+-------+--------------------------------------------+----------+
| -- | 1 | RO 0 | 保留位 | 0 |
+--------+--------+-------+--------------------------------------------+----------+
| CY | 0 | RW | mcycle 寄存器禁止计数位: | 0 | | | | | | | | | | | 0: 正常计数 | | | | | | |
| | | | | 1: 禁止计数 | |
+--------+--------+-------+--------------------------------------------+----------+

### 机器模式性能事件计数器访问授权寄存器 (MCOUNTEREN)

机器模式性能事件计数器访问授权寄存器 (mcounteren)，是32位 WARL 寄存器，主要用于控制用户态性能监测计数器在机器模式以下特权级模式
(HS-mode/VS-mode/HU-mode/VU-mode) 中的访问权限。

Table: 机器模式性能事件计数器访问授权寄存器说明

+--------+--------+-------+------------------------------------------------+----------+
| 名称 | 位域 | 读写 | 行为 | 复位值 |
+========+========+=======+================================================+==========+
| HPMx | 31:3 | RW | hpmcounterenx 寄存器 M-mode 以下访问权限位: | 0 | | | | | | | | | | |
0: 访问 hpmcounterx 报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 hpmcounterx | |
+--------+--------+-------+------------------------------------------------+----------+
| IR | 2 | RW | instret 寄存器 M-mode 以下访问权限位: | 0 | | | | | | | | | | | 0: 访问
instret 报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+
| TM | 1 | RW | time/stimecmp 寄存器 M-mode 以下访问权限位: | 0 | | | | | | | | | | | 0:
访问 time 报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+
| CY | 0 | RW | cycle 寄存器 M-mode 以下访问权限位: | 0 | | | | | | | | | | | 0: 访问 cycle
报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+

### 监督模式性能事件计数器访问授权寄存器 (SCOUNTEREN)

监督模式性能事件计数器访问授权寄存器 (scounteren)，是32位 WARL 寄存器，主要用于控制用户态性能监测计数器在用户模式
(HU-mode/VU-mode) 中的访问权限。

Table: 监督模式性能事件计数器访问授权寄存器说明

+--------+--------+-------+------------------------------------------------+----------+
| 名称 | 位域 | 读写 | 行为 | 复位值 |
+========+========+=======+================================================+==========+
| HPMx | 31:3 | RW | hpmcounterenx 寄存器 用户模式访问权限位: | 0 | | | | | | | | | | | 0:
访问 hpmcounterx 报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 hpmcounterx | |
+--------+--------+-------+------------------------------------------------+----------+
| IR | 2 | RW | instret 寄存器 用户模式访问权限位: | 0 | | | | | | | | | | | 0: 访问 instret
报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+
| TM | 1 | RW | time 寄存器 用户模式访问权限位: | 0 | | | | | | | | | | | 0: 访问 time 报非法指令异常
| | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+
| CY | 0 | RW | cycle 寄存器 用户模式访问权限位: | 0 | | | | | | | | | | | 0: 访问 cycle
报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+

### 虚拟化模式性能事件计数器访问授权寄存器 (HCOUNTEREN)

虚拟化模式性能事件计数器访问授权寄存器 (hcounteren)，是32位 WARL 寄存器，主要用于控制用户态性能监测计数器在客户虚拟机
(VS-mode/VU-mode) 中的访问权限。

Table: 监督模式性能事件计数器访问授权寄存器说明

+--------+--------+-------+------------------------------------------------+----------+
| 名称 | 位域 | 读写 | 行为 | 复位值 |
+========+========+=======+================================================+==========+
| HPMx | 31:3 | RW | hpmcounterenx 寄存器 客户虚拟机访问权限位: | 0 | | | | | | | | | | | 0:
访问 hpmcounterx 报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 hpmcounterx | |
+--------+--------+-------+------------------------------------------------+----------+
| IR | 2 | RW | instret 寄存器 客户虚拟机访问权限位: | 0 | | | | | | | | | | | 0: 访问 instret
报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+
| TM | 1 | RW | time/vstimecmp(via stimecmp) 寄存器 客户虚拟机 | 0 | | | | | 访问权限位: | |
| | | | | | | | | | 0: 访问 time 报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+
| CY | 0 | RW | cycle 寄存器 客户虚拟机访问权限位: | 0 | | | | | | | | | | | 0: 访问 cycle
报非法指令异常 | | | | | | | | | | | | 1: 允许正常访问 | |
+--------+--------+-------+------------------------------------------------+----------+

### 监督模式时间比较寄存器 (STIMECMP)

监督模式时间比较寄存器 (stimecmp)， 是64位 WARL 寄存器，主要用于管理监督模式下的定时器中断 (STIP)。

STIMECMP 寄存器行为说明：

* 复位值为64位无符号数 64'hffff_ffff_ffff_ffff。
* 在 menvcfg.STCE 为 0 且当前特权级低于 M-mode (HS-mode/VS-mode/HU-mode/VU-mode) 时，访问
  stimecmp 寄存器产生非法指令异常，且不产生 STIP 中断。
* stimecmp 寄存器是 STIP 中断产生源头：在进行无符号整数比较 time ≥ stimecmp 时，拉高STIP中断等待信号。
* 监督模式软件可以通过写 stimecmp 控制定时器中断的产生。

### 客户虚拟机监督模式时间比较寄存器 (VSTIMECMP)

客户虚拟机监督模式时间比较寄存器 (vstimecmp)，是64位 WARL 寄存器，主要用于管理客户虚拟机监督模式下的定时器中断 (STIP)。

VSTIMECMP 寄存器行为说明：

* 复位值为64位无符号数 64'hffff_ffff_ffff_ffff。
* 在 henvcfg.STCE 为 0 或者 hcounteren.TM 时，通过 stimecmp 寄存器访问 vstimecmp 寄存器产生
  虚拟非法指令异常，且不产生 VSTIP 中断。
* vstimecmp 寄存器是 VSTIP 中断产生源头：在进行无符号整数比较 time + htimedelta ≥ vstimecmp
  时，拉高VSTIP中断等待信号。
* 客户虚拟机监督模式软件可以通过写 vstimecmp 控制 VS-mode 下定时器中断的产生。

## PMU 相关的性能事件选择器

机器模式性能事件选择器 (mhpmevent3 - 31)，是64为 WARL 寄存器，用于选择每个性能事件计数器对应的性能事件。在
{{processor_name}}
中，每个计数器可以配置最多四个性能事件进行组合计数。用户将事件索引值、事件组合方法、采样特权级写入指定事件选择器后，该事件选择器所匹配的事件计数器开始正常计数。

Table: 机器模式性能事件选择器说明

+----------------+--------+-------+-----------------------------------------------+----------+
| 名称 | 位域 | 读写 | 行为 | 复位值 |
+================+========+=======+===============================================+==========+
| OF | 63 | RW | 性能计数上溢标志位: | 0 | | | | | | | | | | | 0: 对应性能计数器溢出时置1，产生溢出中断 | |
| | | | | | | | | | 1: 对应性能计数器溢出时值不变，不产生溢出中断 | |
+----------------+--------+-------+-----------------------------------------------+----------+
| MINH | 62 | RW | 置1时，禁止 M 模式采样计数 | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| SINH | 61 | RW | 置1时，禁止 S 模式采样计数 | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| UINH | 60 | RW | 置1时，禁止 U 模式采样计数 | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| VSINH | 59 | RW | 置1时，禁止 VS 模式采样计数 | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| VUINH | 58 | RW | 置1时，禁止 VU 模式采样计数 | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| -- | 57:55 | RW | -- | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| | | | 计数器事件组合方法控制位: | | | | | | | | | | | | 5'b00000: 采用 or 操作组合 | | |
OP_TYPE2 | 54:50 | | | | | OP_TYPE1 | 49:45 | RW | 5'b00001: 采用 and 操作组合 | 0 | |
OP_TYPE0 | 44:40 | | | | | | | | 5'b00010: 采用 xor 操作组合 | | | | | | | | | | | |
5'b00100: 采用 add 操作组合 | |
+----------------+--------+-------+-----------------------------------------------+----------+
| | | | 计数器性能事件索引值: | | | EVENT3 | 39:30 | | | | | EVENT2 | 29:20 | RW | 0:
对应的事件计数器不计数 | -- | | EVENT1 | 19:10 | | | | | EVENT0 | 9:0 | | 1: 对应的事件计数器对事件计数
| | | | | | | |
+----------------+--------+-------+-----------------------------------------------+----------+

其中，计数器事件的组合方法为：

* EVENT0 和 EVENT1 事件计数采用 OP_TYPE0 操作组合为 RESULT0。
* EVENT2 和 EVENT3 事件计数采用 OP_TYPE1 操作组合为 RESULT1。
* RESULT0 和 RESULT1 组合记过采用 OP_TYPE2 操作组合为 RESULT2。
* RESULT2 累加到对应事件计数器。

对性能事件选择器中事件索引值部分复位值规定如下：

* 由于目前 {{processor_name}} 定义的各个性能事件集合大小不超过150，因此规定 EVENTx 高两位复位固定值：
* 对于mhpmevent 3-10: 40'h0000000000
* 对于mhpmevent11-18: 40'h4010040100
* 对于mhpmevent19-26: 40'h8020080200
* 对于mhpmevent27-31: 40'hc0300c0300

{{processor_name}}
将提供的性能事件根据来源分为四类，包括：前端，后端，访存，缓存，同时将计数器分为四部分，分别记录来自上述四个源头的性能事件：

* 前端：mhpmevent 3-10
* 后端：mhpmevent11-18
* 访存：mhpmevent19-26
* 缓存：mhpmevent27-31

Table: {{processor_name}} 前端性能事件索引表

| 索引  | 事件                      |
| --- | ----------------------- |
| 0   | noEvent                 |
| 1   | frontendFlush           |
| 2   | ifu_req                 |
| 3   | ifu_miss                |
| 4   | ifu_req_cacheline_0     |
| 5   | ifu_req_cacheline_1     |
| 6   | ifu_req_cacheline_0_hit |
| 7   | ifu_req_cacheline_1_hit |
| 8   | only_0_hit              |
| 9   | only_0_miss             |
| 10  | hit_0_hit_1             |
| 11  | hit_0_miss_1            |
| 12  | miss_0_hit_1            |
| 13  | miss_0_miss_1           |
| 14  | IBuffer_Flushed         |
| 15  | IBuffer_hungry          |
| 16  | IBuffer_1_4_valid       |
| 17  | IBuffer_2_4_valid       |
| 18  | IBuffer_3_4_valid       |
| 19  | IBuffer_4_4_valid       |
| 20  | IBuffer_full            |
| 21  | Front_Bubble            |
| 22  | Fetch_Latency_Bound     |
| 23  | icache_miss_bubble      |
| 24  | icache_miss_penalty     |
| 25  | bpu_s2_redirect         |
| 26  | bpu_s3_redirect         |
| 27  | bpu_to_ftq_stall        |
| 28  | mispredictRedirect      |
| 29  | replayRedirect          |
| 30  | predecodeRedirect       |
| 31  | to_ifu_bubble           |
| 32  | from_bpu_real_bubble    |
| 33  | BpInstr                 |
| 34  | BpBInstr                |
| 35  | BpRight                 |
| 36  | BpWrong                 |
| 37  | BpBRight                |
| 38  | BpBWrong                |
| 39  | BpJRight                |
| 40  | BpJWrong                |
| 41  | BpIRight                |
| 42  | BpIWrong                |
| 43  | BpCRight                |
| 44  | BpCWrong                |
| 45  | BpRRight                |
| 46  | BpRWrong                |
| 47  | ftb_false_hit           |
| 48  | ftb_hit                 |
| 49  | fauftb_commit_hit       |
| 50  | fauftb_commit_miss      |
| 51  | tage_tht_hit            |
| 52  | sc_update_on_mispred    |
| 53  | sc_update_on_unconf     |
| 54  | ftb_commit_hits         |
| 55  | ftb_commit_misses       |
| 56  | itlb_access             |
| 57  | itlb_miss               |

Table: {{processor_name}} 后端性能事件索引表

| 索引  | 事件                                                           |
| --- | ------------------------------------------------------------ |
| 0   | noEvent                                                      |
| 1   | decoder_fused_instr                                          |
| 2   | decoder_waitInstr                                            |
| 3   | decoder_stall_cycle                                          |
| 4   | decoder_utilization                                          |
| 5   | frontend_stall_cycle                                         |
| 6   | backend_stall_cycle                                          |
| 7   | INST_SPEC                                                    |
| 8   | RECOVERY_BUBBLE                                              |
| 9   | rename_in                                                    |
| 10  | rename_waitinstr                                             |
| 11  | rename_stall                                                 |
| 12  | rename_stall_cycle_walk                                      |
| 13  | rename_stall_cycle_dispatch                                  |
| 14  | rename_stall_cycle_int                                       |
| 15  | rename_stall_cycle_fp                                        |
| 16  | rename_stall_cycle_vec                                       |
| 17  | rename_stall_cycle_v0                                        |
| 18  | rename_stall_cycle_vl                                        |
| 19  | me_freelist_1_4_valid                                        |
| 20  | me_freelist_2_4_valid                                        |
| 21  | me_freelist_3_4_valid                                        |
| 22  | me_freelist_4_4_valid                                        |
| 23  | std_freelist_1_4_valid                                       |
| 24  | std_freelist_2_4_valid                                       |
| 25  | std_freelist_3_4_valid                                       |
| 26  | std_freelist_4_4_valid                                       |
| 27  | std_freelist_1_4_valid                                       |
| 28  | std_freelist_2_4_valid                                       |
| 29  | std_freelist_3_4_valid                                       |
| 30  | std_freelist_4_4_valid                                       |
| 31  | std_freelist_1_4_valid                                       |
| 32  | std_freelist_2_4_valid                                       |
| 33  | std_freelist_3_4_valid                                       |
| 34  | std_freelist_4_4_valid                                       |
| 35  | std_freelist_1_4_valid                                       |
| 36  | std_freelist_2_4_valid                                       |
| 37  | std_freelist_3_4_valid                                       |
| 38  | std_freelist_4_4_valid                                       |
| 39  | dispatch_in                                                  |
| 40  | dispatch_empty                                               |
| 41  | dispatch_utili                                               |
| 42  | dispatch_waitinstr                                           |
| 43  | dispatch_stall_cycle_lsq                                     |
| 44  | dispatch_stall_cycle_rob                                     |
| 45  | dispatch_stall_cycle_int_dq                                  |
| 46  | dispatch_stall_cycle_fp_dq                                   |
| 47  | dispatch_stall_cycle_ls_dq                                   |
| 48  | rob_interrupt_num                                            |
| 49  | rob_exception_num                                            |
| 50  | rob_flush_pipe_num                                           |
| 51  | rob_replay_inst_num                                          |
| 52  | rob_commitUop                                                |
| 53  | rob_commitInstr                                              |
| 54  | rob_commitInstrFused                                         |
| 55  | rob_commitInstrLoad                                          |
| 56  | rob_commitInstrBranch                                        |
| 57  | rob_commitInstrStore                                         |
| 58  | rob_walkInstr                                                |
| 59  | rob_walkCycle                                                |
| 60  | rob_1_4_valid                                                |
| 61  | rob_2_4_valid                                                |
| 62  | rob_3_4_valid                                                |
| 63  | rob_4_4_valid                                                |
| 64  | BRANCH_JUMP                                                  |
| 65  | BR_MIS_PRED                                                  |
| 66  | TOTAL_FLUSH                                                  |
| 67  | EXEC_STALL_CYCLE                                             |
| 68  | MEMSTALL_ANY_LOAD                                            |
| 69  | MEMSTALL_STORE                                               |
| 70  | MEMSTALL_L1MISS                                              |
| 71  | MEMSTALL_L2MISS                                              |
| 72  | MEMSTALL_L3MISS                                              |
| 73  | issueQueue_enq_fire_cnt                                      |
| 74  | IssueQueueAluMulBkuBrhJmp_full                               |
| 75  | IssueQueueAluMulBkuBrhJmp_full                               |
| 76  | IssueQueueAluBrhJmpI2fVsetriwiVsetriwvfI2v_full              |
| 77  | IssueQueueAluCsrFenceDiv_full                                |
| 78  | issueQueue_enq_fire_cnt                                      |
| 79  | IssueQueueFaluFcvtF2vFmacFdiv_full                           |
| 80  | IssueQueueFaluFmacFdiv_full                                  |
| 81  | IssueQueueFaluFmac_full                                      |
| 82  | issueQueue_enq_fire_cnt                                      |
| 83  | IssueQueueVfmaVialuFixVimacVppuVfaluVfcvtVipuVsetrvfwvf_full |
| 84  | IssueQueueVfmaVialuFixVfalu_full                             |
| 85  | IssueQueueVfdivVidiv_full                                    |
| 86  | issueQueue_enq_fire_cnt                                      |
| 87  | IssueQueueStaMou_full                                        |
| 88  | IssueQueueStaMou_full                                        |
| 89  | IssueQueueLdu_full                                           |
| 90  | IssueQueueLdu_full                                           |
| 91  | IssueQueueLdu_full                                           |
| 92  | IssueQueueVlduVstuVseglduVsegstu_full                        |
| 93  | IssueQueueVlduVstu_full                                      |
| 94  | IssueQueueStdMoud_full                                       |
| 95  | IssueQueueStdMoud_full                                       |
| 96  | cpu_cycle                                                    |
| 97  | ref_cpu_cycle                                                |

Table: {{processor_name}} 访存性能事件索引表

| 索引  | 事件                        |
| --- | ------------------------- |
| 0   | noEvent                   |
|     | **LoadUnit 0**            |
| 1   | load_s0_in_fire           |
| 2   | load_to_load_forward      |
| 3   | stall_dcache              |
| 4   | load_s1_in_fire           |
| 5   | load_s1_tlb_miss          |
| 6   | load_s2_in_fire           |
| 7   | load_s2_dcache_miss       |
| 8   | l1D_load_hw_prf_access    |
| 9   | l1D_load_hw_prf_miss      |
|     | **LoadUnit 1**            |
| 10  | load_s0_in_fire           |
| 11  | load_to_load_forward      |
| 12  | stall_dcache              |
| 13  | load_s1_in_fire           |
| 14  | load_s1_tlb_miss          |
| 15  | load_s2_in_fire           |
| 16  | load_s2_dcache_miss       |
| 17  | l1D_load_hw_prf_access    |
| 18  | l1D_load_hw_prf_miss      |
|     | **LoadUnit 2**            |
| 19  | load_s0_in_fire           |
| 20  | load_to_load_forward      |
| 21  | stall_dcache              |
| 22  | load_s1_in_fire           |
| 23  | load_s1_tlb_miss          |
| 24  | load_s2_in_fire           |
| 25  | load_s2_dcache_miss       |
| 26  | l1D_load_hw_prf_access    |
| 27  | l1D_load_hw_prf_miss      |
| 28  | sbuffer_req_valid         |
| 29  | sbuffer_req_fire          |
| 30  | sbuffer_merge             |
| 31  | sbuffer_newline           |
| 32  | dcache_req_valid          |
| 33  | dcache_req_fire           |
| 34  | sbuffer_idle              |
| 35  | sbuffer_flush             |
| 36  | sbuffer_replace           |
| 37  | mpipe_resp_valid          |
| 38  | replay_resp_valid         |
| 39  | coh_timeout               |
| 40  | sbuffer_1_4_valid         |
| 41  | sbuffer_2_4_valid         |
| 42  | sbuffer_3_4_valid         |
| 43  | sbuffer_full_valid        |
| 44  | enq                       |
| 45  | ld_ld_violation           |
| 46  | enq                       |
| 47  | stld_rollback             |
| 48  | enq                       |
| 49  | deq                       |
| 50  | deq_block                 |
| 51  | replay_full               |
| 52  | replay_rar_nack           |
| 53  | replay_raw_nack           |
| 54  | replay_nuke               |
| 55  | replay_mem_amb            |
| 56  | replay_tlb_miss           |
| 57  | replay_bank_conflict      |
| 58  | replay_dcache_replay      |
| 59  | replay_forward_fail       |
| 60  | replay_dcache_miss        |
| 61  | full_mask_000             |
| 62  | full_mask_001             |
| 63  | full_mask_010             |
| 64  | full_mask_011             |
| 65  | full_mask_100             |
| 66  | full_mask_101             |
| 67  | full_mask_110             |
| 68  | full_mask_111             |
| 69  | nuke_rollback             |
| 70  | nack_rollback             |
| 71  | mmioCycle                 |
| 72  | mmioCnt                   |
| 73  | mmio_wb_success           |
| 74  | mmio_wb_blocked           |
| 75  | stq_1_4_valid             |
| 76  | stq_2_4_valid             |
| 77  | stq_3_4_valid             |
| 78  | stq_4_4_valid             |
| 79  | dcache_wbq_req            |
| 80  | dcache_wbq_1_4_valid      |
| 81  | dcache_wbq_2_4_valid      |
| 82  | dcache_wbq_3_4_valid      |
| 83  | dcache_wbq_4_4_valid      |
| 84  | l1D_write_dcache_access   |
| 85  | l1D_write_dcache_miss     |
| 86  | dcache_mp_req             |
| 87  | dcache_mp_total_penalty   |
| 88  | dcache_missq_req          |
| 89  | dcache_missq_1_4_valid    |
| 90  | dcache_missq_2_4_valid    |
| 91  | dcache_missq_3_4_valid    |
| 92  | dcache_missq_4_4_valid    |
| 93  | dcache_probq_req          |
| 94  | dcache_probq_1_4_valid    |
| 95  | dcache_probq_2_4_valid    |
| 96  | dcache_probq_3_4_valid    |
| 97  | dcache_probq_4_4_valid    |
|     | **DCache LoadPipe 0**     |
| 98  | load_req                  |
| 99  | load_replay               |
| 100 | load_replay_for_data_nack |
| 101 | load_replay_for_no_mshr   |
| 102 | load_replay_for_conflict  |
| 103 | l1D_read_dcache_access    |
| 104 | l1D_read_dcache_miss      |
|     | **DCache LoadPipe 1**     |
| 105 | load_req                  |
| 106 | load_replay               |
| 107 | load_replay_for_data_nack |
| 108 | load_replay_for_no_mshr   |
| 109 | load_replay_for_conflict  |
| 110 | l1D_read_dcache_access    |
| 111 | l1D_read_dcache_miss      |
|     | **DCache LoadPipe 2**     |
| 112 | load_req                  |
| 113 | load_replay               |
| 114 | load_replay_for_data_nack |
| 115 | load_replay_for_no_mshr   |
| 116 | load_replay_for_conflict  |
| 117 | l1D_read_dcache_access    |
| 118 | l1D_read_dcache_miss      |
| 119 | dtlb_ld_access            |
| 120 | dtlb_ld_miss              |
| 121 | dtlb_st_access            |
| 122 | dtlb_st_miss              |
| 123 | PTW_tlbllptw_incount      |
| 124 | PTW_tlbllptw_inblock      |
| 125 | PTW_tlbllptw_memcount     |
| 126 | PTW_tlbllptw_memcycle     |
| 127 | PTW_access                |
| 128 | PTW_l2_hit                |
| 129 | PTW_l1_hit                |
| 130 | PTW_l0_hit                |
| 131 | PTW_sp_hit                |
| 132 | PTW_pte_hit               |
| 133 | PTW_rwHarzad              |
| 134 | PTW_out_blocked           |
| 135 | PTW_fsm_count             |
| 136 | PTW_fsm_busy              |
| 137 | PTW_fsm_idle              |
| 138 | PTW_resp_blocked          |
| 139 | PTW_mem_count             |
| 140 | PTW_mem_cycle             |
| 141 | PTW_mem_blocked           |
| 142 | ldDeqCount                |
| 143 | stDeqCount                |

Table: {{processor_name}} 缓存性能事件索引表

| 索引  | 事件                              |
| --- | ------------------------------- |
| 0   | noEvent                         |
| 1   | Slice0_l2_cache_refill          |
| 2   | Slice0_l2_cache_rd_refill       |
| 3   | Slice0_l2_cache_wr_refill       |
| 4   | Slice0_l2_cache_long_miss       |
| 5   | Slice0_l2_cache_hit             |
| 6   | Slice0_l2_cache_miss            |
| 7   | Slice0_l2_cache_access          |
| 8   | Slice0_l2_cache_l2wb            |
| 9   | Slice0_l2_cache_l1wb            |
| 10  | Slice0_l2_cache_wb_victim       |
| 11  | Slice0_l2_cache_wb_cleaning_coh |
| 12  | Slice0_l2_cache_prefetch_access |
| 13  | Slice0_l2_cache_prefetch_miss   |
| 14  | Slice0_l2_cache_access_rd       |
| 15  | Slice0_l2_cache_access_wr       |
| 16  | Slice0_l2_cache_miss_rd         |
| 17  | Slice0_l2_cache_inv             |
| 18  | Slice1_l2_cache_refill          |
| 19  | Slice1_l2_cache_rd_refill       |
| 20  | Slice1_l2_cache_wr_refill       |
| 21  | Slice1_l2_cache_long_miss       |
| 22  | Slice1_l2_cache_hit             |
| 23  | Slice1_l2_cache_miss            |
| 24  | Slice1_l2_cache_access          |
| 25  | Slice1_l2_cache_l2wb            |
| 26  | Slice1_l2_cache_l1wb            |
| 27  | Slice1_l2_cache_wb_victim       |
| 28  | Slice1_l2_cache_wb_cleaning_coh |
| 29  | Slice1_l2_cache_prefetch_access |
| 30  | Slice1_l2_cache_prefetch_miss   |
| 31  | Slice1_l2_cache_access_rd       |
| 32  | Slice1_l2_cache_access_wr       |
| 33  | Slice1_l2_cache_miss_rd         |
| 34  | Slice1_l2_cache_inv             |
| 35  | Slice2_l2_cache_refill          |
| 36  | Slice2_l2_cache_rd_refill       |
| 37  | Slice2_l2_cache_wr_refill       |
| 38  | Slice2_l2_cache_long_miss       |
| 39  | Slice2_l2_cache_hit             |
| 40  | Slice2_l2_cache_miss            |
| 41  | Slice2_l2_cache_access          |
| 42  | Slice2_l2_cache_l2wb            |
| 43  | Slice2_l2_cache_l1wb            |
| 44  | Slice2_l2_cache_wb_victim       |
| 45  | Slice2_l2_cache_wb_cleaning_coh |
| 46  | Slice2_l2_cache_prefetch_access |
| 47  | Slice2_l2_cache_prefetch_miss   |
| 48  | Slice2_l2_cache_access_rd       |
| 49  | Slice2_l2_cache_access_wr       |
| 50  | Slice2_l2_cache_miss_rd         |
| 51  | Slice2_l2_cache_inv             |
| 52  | Slice3_l2_cache_refill          |
| 53  | Slice3_l2_cache_rd_refill       |
| 54  | Slice3_l2_cache_wr_refill       |
| 55  | Slice3_l2_cache_long_miss       |
| 56  | Slice3_l2_cache_hit             |
| 57  | Slice3_l2_cache_miss            |
| 58  | Slice3_l2_cache_access          |
| 59  | Slice3_l2_cache_l2wb            |
| 60  | Slice3_l2_cache_l1wb            |
| 61  | Slice3_l2_cache_wb_victim       |
| 62  | Slice3_l2_cache_wb_cleaning_coh |
| 63  | Slice3_l2_cache_prefetch_access |
| 64  | Slice3_l2_cache_prefetch_miss   |
| 65  | Slice3_l2_cache_access_rd       |
| 66  | Slice3_l2_cache_access_wr       |
| 67  | Slice3_l2_cache_miss_rd         |
| 68  | Slice3_l2_cache_inv             |



## PMU 相关的性能事件计数器

{{processor_name}} 的性能事件计数器共分为两组，分别是：机器模式事件计数器、监督模式事件计数器、用户模式事件计数器

Table: 机器模式事件计数器列表

| 名称              | 索引          | 读写  | 介绍          | 复位值 |
| --------------- | ----------- | --- | ----------- | --- |
| MCYCLE          | 0xB00       | RW  | 机器模式时钟周期计数器 | -   |
| MINSTRET        | 0xB02       | RW  | 机器模式退休指令计数器 | -   |
| MHPMCOUNTER3-31 | 0XB03-0XB1F | RW  | 机器模式性能事件计数器 | 0   |

其中 MHPMCOUNTERx 计数器相应由 MHPMEVENTx控制，指定计数相应的性能事件。

监督模式事件计数器包括监督模式计数器上溢中断标志寄存器(SCOUNTOVF)

Table: 监督模式计数器上溢中断标志寄存器(SCOUNTOVF)说明

+------------+--------+-------+-----------------------------------------------+--------+
| 名称 | 位域 | 读写 | 行为 | 复位值 |
+============+========+=======+===============================================+========+
| OFVEC | 31:3 | RO | mhpmcounterx 寄存器上溢标志位: | 0 | | | | | | | | | | | 1： 发生上溢 |
| | | | | | | | | | | 0： 没有发生上溢 | |
+------------+--------+-------+-----------------------------------------------+--------+
| -- | 2:0 | RO 0 | -- | 0 |
+------------+--------+-------+-----------------------------------------------+--------+

scountovf 作为 mhpmcounter 寄存器 OF 位的只读映射，受 xcounteren 控制:

* M-mode 访问 scountovf 可读正确值。
* HS-mode 访问 scountovf ：mcounteren.HPMx 为1时，对应 OFVECx 可读正确值；否则只读0。
* VS-mode 访问 scountovf : mcounteren.HPMx 以及 hcounteren.HPMx 均为1时，对应 OFVECx
  可读正确值；否则只读0。

Table: 用户模式事件计数器列表

| 名称             | 索引          | 读写  | 介绍                          | 复位值 |
| -------------- | ----------- | --- | --------------------------- | --- |
| CYCLE          | 0xC00       | RO  | mcycle 寄存器用户模式只读副本          | -   |
| TIME           | 0xC01       | RO  | 内存映射寄存器 mtime 用户模式只读副本      | -   |
| INSTRET        | 0xC02       | RO  | minstret 寄存器用户模式只读副本        | -   |
| HPMCOUNTER3-31 | 0XC03-0XC1F | RO  | mhpmcounter3-31 寄存器用户模式只读副本 | 0   |
