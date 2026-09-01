---
file_authors_:
- zehao Liu <liuzehao19@mails.ucas.ac.cn> 
---

# Performance Monitor {#sec:performance-monitor}

The Performance Monitoring Unit (PMU) of {{processor_name}} implements basic
hardware performance monitoring functions according to the RISC-V Privileged
Specification and additionally supports the sstc and sscofpmf extensions. These
features are used to collect certain hardware and thread information during
processor operation, which can assist software developers in program
optimization.

The software and hardware information collected by the performance monitoring
unit can be mainly classified into the following categories:

* The clock cycles executed by the hart (cycle)
* Number of instructions committed by the hart (minstret)
* Hardware Timer (time)
* Performance Event Statistics of Processor Key Components (hpmcounter3 -
  hpmcounter31, countovf)

## PMU Programming Model

### Basic Usage of PMU

The basic usage of PMU is as follows:

* Disable all performance event monitoring via the mcountinhibit register.
* Initialize echo performance event counters, including: mcycle, minstret,
  mhpmcounter3 - mhpmcounter31.
* 配置各个监测单元性能事件选择器，包括: mhpmevent3 - mhpmevent31。 {{processor_name}}
  对每个事件选择器可以配置最多四种事件组合，将事件索引值、事件组合方法、采样特权级写入事件选择器后，即可在规定的采样特权级下对配置的事件正常计数，并根据组合后结果累加到事件计数器中。
* Configure xcounteren for access permission authorization
* Enable all performance event monitoring via mcountinhibit register and start
  counting.

### PMU event overflow interrupt

The LCOFIP overflow interrupt initiated by the {{processor_name}} performance
monitoring unit has a unified interrupt vector number of 12. The enabling and
handling process of this interrupt is consistent with ordinary private
interrupts. For details, refer to [Exceptions and
Interrupts](./exception-and-interrupt.md).

## PMU-related control registers

### Machine-mode Performance Event Count Inhibit Register (MCOUNTINHIBIT)

The Machine-Mode Performance Event Count Inhibit Register (mcountinhibit) is a
32-bit WARL register primarily used to control whether hardware performance
monitoring counters count. In scenarios where performance analysis is not
required, counters can be disabled to reduce processor power consumption.

Table: Machine Mode Performance Event Count Prohibit Register Description

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

### Machine-mode Performance Counter Event Access Enable Register (MCOUNTEREN)

The Machine-mode Performance Event Counter Access Enable Register (mcounteren)
is a 32-bit WARL register primarily used to control access permissions for
user-mode performance monitoring counters at privilege levels below machine mode
(HS-mode/VS-mode/HU-mode/VU-mode).

Table: Machine Mode Performance Event Counter Access Authorization Register
Description

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

### Supervisor-mode Performance Counter Access Enable Register (SCOUNTEREN)

Supervisor-mode Performance Counter Access Enable Register (scounteren) is a
32-bit WARL register primarily used to control user-mode access permissions for
performance monitoring counters in HU-mode/VU-mode.

Table: Supervisor Mode Performance Event Counter Access Authorization Register
Description

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

### Virtualization Mode Performance Event Counter Access Authorization Register (HCOUNTEREN)

The Virtualization Mode Performance Event Counter Access Authorization Register
(hcounteren) is a 32-bit WARL register primarily used to control user-mode
performance monitoring counter access permissions in guest virtual machines
(VS-mode/VU-mode).

Table: Supervisor Mode Performance Event Counter Access Authorization Register
Description

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

### Supervisor Mode Time Compare Register (STIMECMP)

The Supervisor Mode Timer Compare Register (stimecmp) is a 64-bit WARL register
primarily used to manage timer interrupts (STIP) in supervisor mode.

STIMECMP Register Behavior Description:

* Reset value is a 64-bit unsigned number 64'hffff_ffff_ffff_ffff.
* When menvcfg.STCE is 0 and the current privilege level is below M-mode
  (HS-mode/VS-mode/HU-mode/VU-mode), accessing the stimecmp register triggers an
  illegal instruction exception and does not generate an STIP interrupt.
* The stimecmp register is the source of STIP interrupt generation: when
  performing an unsigned integer comparison time ≥ stimecmp, it asserts the STIP
  interrupt pending signal.
* Supervisor mode software can control the generation of timer interrupts by
  writing to stimecmp.

### Guest Virtual Machine Supervisor Mode Time Compare Register (VSTIMECMP)

The Guest Supervisor Time Compare Register (vstimecmp) is a 64-bit WARL register
primarily used to manage timer interrupts (STIP) in guest supervisor mode.

VSTIMECMP Register Behavior Description:

* Reset value is a 64-bit unsigned number 64'hffff_ffff_ffff_ffff.
* When henvcfg.STCE is 0 or hcounteren.TM is set, accessing the vstimecmp
  register via the stimecmp register triggers a virtual illegal instruction
  exception without generating a VSTIP interrupt.
* The vstimecmp register is the source of VSTIP interrupt generation: when
  performing an unsigned integer comparison time + htimedelta ≥ vstimecmp, the
  VSTIP interrupt pending signal is raised.
* Guest supervisor mode software can control the generation of timer interrupts
  in VS-mode by writing to vstimecmp.

## PMU-related Performance Event Selector

Machine-mode Performance Event Selector (mhpmevent3 - 31) is a 64-bit WARL
register used to select performance events for each performance counter. In
{{processor_name}}, each counter can be configured to count up to four
performance events in combination. After writing the event index values, event
combination method, and sampling privilege levels to the designated event
selector, the corresponding event counter begins normal counting.

Table: Machine Mode Performance Event Selector Description

+----------------+--------+-------+-----------------------------------------------+----------+
| Name | Bits | R/W | Behavior | Reset |
+================+========+=======+===============================================+==========+
| OF | 63 | RW | Performance counter overflow flag: | 0 | | | | | | | | | | | 0:
Set to 1 when counter overflows, triggers interrupt | | | | | | | | | | | | 1:
Counter value remains unchanged on overflow, no interrupt | |
+----------------+--------+-------+-----------------------------------------------+----------+
| MINH | 62 | RW | When set to 1, disables M-mode sampling | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| SINH | 61 | RW | When set to 1, disables S-mode sampling | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| UINH | 60 | RW | When set to 1, disables U-mode sampling | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| VSINH | 59 | RW | When set to 1, disables VS-mode sampling | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| VUINH | 58 | RW | When set to 1, disables VU-mode sampling | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| -- | 57:55 | RW | -- | 0 |
+----------------+--------+-------+-----------------------------------------------+----------+
| | | | Counter event combination method control bits: | | | | | | | | | | | |
5'b00000: OR operation combination | | | OP_TYPE2 | 54:50 | | | | | OP_TYPE1 |
49:45 | RW | 5'b00001: AND operation combination | 0 | | OP_TYPE0 | 44:40 | | |
| | | | | 5'b00010: XOR operation combination | | | | | | | | | | | | 5'b00100:
ADD operation combination | |
+----------------+--------+-------+-----------------------------------------------+----------+
| | | | Counter performance event index values: | | | EVENT3 | 39:30 | | | | |
EVENT2 | 29:20 | RW | 0: Corresponding event counter does not count | -- | |
EVENT1 | 19:10 | | | | | EVENT0 | 9:0 | | 1: Corresponding event counter counts
the event | | | | | | | |
+----------------+--------+-------+-----------------------------------------------+----------+

The combination method for counter events is:

* EVENT0 and EVENT1 event counts use OP_TYPE0 operation combination to produce
  RESULT0.
* EVENT2 and EVENT3 event counts are combined using OP_TYPE1 operation to
  produce RESULT1.
* The combined results of RESULT0 and RESULT1 are processed using OP_TYPE2
  operation to form RESULT2.
* RESULT2 is accumulated into the corresponding event counter.

The reset value specification for the event index portion of the performance
event selector is as follows:

* Since the current performance event set size defined by {{processor_name}}
  does not exceed 150, it is stipulated that the upper two bits of EVENTx are
  fixed reset values:
* For mhpmevent 3-10: 40'h0000000000
* For mhpmevent11-18: 40'h4010040100
* For mhpmevent19-26: 40'h8020080200
* For mhpmevent27-31: 40'hc0300c0300

{{processor_name}} categorizes the provided performance events into four types
based on their sources: front-end, back-end, memory access, and cache. The
counters are divided into four sections to record performance events from these
four sources respectively:

* Frontend: mhpmevent 3-10
* Backend: mhpmevent11-18
* Memory Access: mhpmevent19-26
* Cache: mhpmevent27-31

Table: {{processor_name}} Frontend Performance Event Index Table

| Index | Event |
| ----- | ----- |
| 0 | noEvent |
| 1 | frontendFlush |
| 2 | ifu_req |
| 3 | ifu_miss |
| 4 | ifu_req_cacheline_0 |
| 5 | ifu_req_cacheline_1 |
| 6 | ifu_req_cacheline_0_hit |
| 7 | ifu_req_cacheline_1_hit |
| 8 | only_0_hit |
| 9 | only_0_miss |
| 10 | hit_0_hit_1 |
| 11 | hit_0_miss_1 |
| 12 | miss_0_hit_1 |
| 13 | miss_0_miss_1 |
| 14 | IBuffer_Flushed |
| 15 | IBuffer_hungry |
| 16 | IBuffer_1_4_valid |
| 17 | IBuffer_2_4_valid |
| 18 | IBuffer_3_4_valid |
| 19 | IBuffer_4_4_valid |
| 20 | IBuffer_full |
| 21 | Front_Bubble |
| 22 | Fetch_Latency_Bound |
| 23 | icache_miss_bubble |
| 24 | icache_miss_penalty |
| 25 | bpu_s2_redirect |
| 26 | bpu_s3_redirect |
| 27 | bpu_to_ftq_stall |
| 28 | mispredictRedirect |
| 29 | replayRedirect |
| 30 | predecodeRedirect |
| 31 | to_ifu_bubble |
| 32 | from_bpu_real_bubble |
| 33 | BpInstr |
| 34 | BpBInstr |
| 35 | BpRight |
| 36 | BpWrong |
| 37 | BpBRight |
| 38 | BpBWrong |
| 39 | BpJRight |
| 40 | BpJWrong |
| 41 | BpIRight |
| 42 | BpIWrong |
| 43 | BpCRight |
| 44 | BpCWrong |
| 45 | BpRRight |
| 46 | BpRWrong |
| 47 | ftb_false_hit |
| 48 | ftb_hit |
| 49 | fauftb_commit_hit |
| 50 | fauftb_commit_miss |
| 51 | tage_tht_hit |
| 52 | sc_update_on_mispred |
| 53 | sc_update_on_unconf |
| 54 | ftb_commit_hits |
| 55 | ftb_commit_misses |
| 56 | itlb_access |
| 57 | itlb_miss |

Table: {{processor_name}} Backend Performance Event Index Table

| Index | Event |
| ----- | ----- |
| 0 | noEvent |
| 1 | decoder_fused_instr |
| 2 | decoder_waitInstr |
| 3 | decoder_stall_cycle |
| 4 | decoder_utilization |
| 5 | frontend_stall_cycle |
| 6 | backend_stall_cycle |
| 7 | INST_SPEC |
| 8 | RECOVERY_BUBBLE |
| 9 | rename_in |
| 10 | rename_waitinstr |
| 11 | rename_stall |
| 12 | rename_stall_cycle_walk |
| 13 | rename_stall_cycle_dispatch |
| 14 | rename_stall_cycle_int |
| 15 | rename_stall_cycle_fp |
| 16 | rename_stall_cycle_vec |
| 17 | rename_stall_cycle_v0 |
| 18 | rename_stall_cycle_vl |
| 19 | me_freelist_1_4_valid |
| 20 | me_freelist_2_4_valid |
| 21 | me_freelist_3_4_valid |
| 22 | me_freelist_4_4_valid |
| 23 | std_freelist_1_4_valid |
| 24 | std_freelist_2_4_valid |
| 25 | std_freelist_3_4_valid |
| 26 | std_freelist_4_4_valid |
| 27 | std_freelist_1_4_valid |
| 28 | std_freelist_2_4_valid |
| 29 | std_freelist_3_4_valid |
| 30 | std_freelist_4_4_valid |
| 31 | std_freelist_1_4_valid |
| 32 | std_freelist_2_4_valid |
| 33 | std_freelist_3_4_valid |
| 34 | std_freelist_4_4_valid |
| 35 | std_freelist_1_4_valid |
| 36 | std_freelist_2_4_valid |
| 37 | std_freelist_3_4_valid |
| 38 | std_freelist_4_4_valid |
| 39 | dispatch_in |
| 40 | dispatch_empty |
| 41 | dispatch_utili |
| 42 | dispatch_waitinstr |
| 43 | dispatch_stall_cycle_lsq |
| 44 | dispatch_stall_cycle_rob |
| 45 | dispatch_stall_cycle_int_dq |
| 46 | dispatch_stall_cycle_fp_dq |
| 47 | dispatch_stall_cycle_ls_dq |
| 48 | rob_interrupt_num |
| 49 | rob_exception_num |
| 50 | rob_flush_pipe_num |
| 51 | rob_replay_inst_num |
| 52 | rob_commitUop |
| 53 | rob_commitInstr |
| 54 | rob_commitInstrFused |
| 55 | rob_commitInstrLoad |
| 56 | rob_commitInstrBranch |
| 57 | rob_commitInstrStore |
| 58 | rob_walkInstr |
| 59 | rob_walkCycle |
| 60 | rob_1_4_valid |
| 61 | rob_2_4_valid |
| 62 | rob_3_4_valid |
| 63 | rob_4_4_valid |
| 64 | BRANCH_JUMP |
| 65 | BR_MIS_PRED |
| 66 | TOTAL_FLUSH |
| 67 | EXEC_STALL_CYCLE |
| 68 | MEMSTALL_ANY_LOAD |
| 69 | MEMSTALL_STORE |
| 70 | MEMSTALL_L1MISS |
| 71 | MEMSTALL_L2MISS |
| 72 | MEMSTALL_L3MISS |
| 73 | issueQueue_enq_fire_cnt |
| 74 | IssueQueueAluMulBkuBrhJmp_full |
| 75 | IssueQueueAluMulBkuBrhJmp_full |
| 76 | IssueQueueAluBrhJmpI2fVsetriwiVsetriwvfI2v_full |
| 77 | IssueQueueAluCsrFenceDiv_full |
| 78 | issueQueue_enq_fire_cnt |
| 79 | IssueQueueFaluFcvtF2vFmacFdiv_full |
| 80 | IssueQueueFaluFmacFdiv_full |
| 81 | IssueQueueFaluFmac_full |
| 82 | issueQueue_enq_fire_cnt |
| 83 | IssueQueueVfmaVialuFixVimacVppuVfaluVfcvtVipuVsetrvfwvf_full |
| 84 | IssueQueueVfmaVialuFixVfalu_full |
| 85 | IssueQueueVfdivVidiv_full |
| 86 | issueQueue_enq_fire_cnt |
| 87 | IssueQueueStaMou_full |
| 88 | IssueQueueStaMou_full |
| 89 | IssueQueueLdu_full |
| 90 | IssueQueueLdu_full |
| 91 | IssueQueueLdu_full |
| 92 | IssueQueueVlduVstuVseglduVsegstu_full |
| 93 | IssueQueueVlduVstu_full |
| 94 | IssueQueueStdMoud_full |
| 95 | IssueQueueStdMoud_full |
| 96 | cpu_cycle |
| 97 | ref_cpu_cycle |

Table: {{processor_name}} Memory Access Performance Event Index Table

| Index | Event |
| ----- | ----- |
| 0 | noEvent |
| | **LoadUnit 0** |
| 1 | load_s0_in_fire |
| 2 | load_to_load_forward |
| 3 | stall_dcache |
| 4 | load_s1_in_fire |
| 5 | load_s1_tlb_miss |
| 6 | load_s2_in_fire |
| 7 | load_s2_dcache_miss |
| 8 | l1D_load_hw_prf_access |
| 9 | l1D_load_hw_prf_miss |
| | **LoadUnit 1** |
| 10 | load_s0_in_fire |
| 11 | load_to_load_forward |
| 12 | stall_dcache |
| 13 | load_s1_in_fire |
| 14 | load_s1_tlb_miss |
| 15 | load_s2_in_fire |
| 16 | load_s2_dcache_miss |
| 17 | l1D_load_hw_prf_access |
| 18 | l1D_load_hw_prf_miss |
| | **LoadUnit 2** |
| 19 | load_s0_in_fire |
| 20 | load_to_load_forward |
| 21 | stall_dcache |
| 22 | load_s1_in_fire |
| 23 | load_s1_tlb_miss |
| 24 | load_s2_in_fire |
| 25 | load_s2_dcache_miss |
| 26 | l1D_load_hw_prf_access |
| 27 | l1D_load_hw_prf_miss |
| 28 | sbuffer_req_valid |
| 29 | sbuffer_req_fire |
| 30 | sbuffer_merge |
| 31 | sbuffer_newline |
| 32 | dcache_req_valid |
| 33 | dcache_req_fire |
| 34 | sbuffer_idle |
| 35 | sbuffer_flush |
| 36 | sbuffer_replace |
| 37 | mpipe_resp_valid |
| 38 | replay_resp_valid |
| 39 | coh_timeout |
| 40 | sbuffer_1_4_valid |
| 41 | sbuffer_2_4_valid |
| 42 | sbuffer_3_4_valid |
| 43 | sbuffer_full_valid |
| 44 | enq |
| 45 | ld_ld_violation |
| 46 | enq |
| 47 | stld_rollback |
| 48 | enq |
| 49 | deq |
| 50 | deq_block |
| 51 | replay_full |
| 52 | replay_rar_nack |
| 53 | replay_raw_nack |
| 54 | replay_nuke |
| 55 | replay_mem_amb |
| 56 | replay_tlb_miss |
| 57 | replay_bank_conflict |
| 58 | replay_dcache_replay |
| 59 | replay_forward_fail |
| 60 | replay_dcache_miss |
| 61 | full_mask_000 |
| 62 | full_mask_001 |
| 63 | full_mask_010 |
| 64 | full_mask_011 |
| 65 | full_mask_100 |
| 66 | full_mask_101 |
| 67 | full_mask_110 |
| 68 | full_mask_111 |
| 69 | nuke_rollback |
| 70 | nack_rollback |
| 71 | mmioCycle |
| 72 | mmioCnt |
| 73 | mmio_wb_success |
| 74 | mmio_wb_blocked |
| 75 | stq_1_4_valid |
| 76 | stq_2_4_valid |
| 77 | stq_3_4_valid |
| 78 | stq_4_4_valid |
| 79 | dcache_wbq_req |
| 80 | dcache_wbq_1_4_valid |
| 81 | dcache_wbq_2_4_valid |
| 82 | dcache_wbq_3_4_valid |
| 83 | dcache_wbq_4_4_valid |
| 84 | l1D_write_dcache_access |
| 85 | l1D_write_dcache_miss |
| 86 | dcache_mp_req |
| 87 | dcache_mp_total_penalty |
| 88 | dcache_missq_req |
| 89 | dcache_missq_1_4_valid |
| 90 | dcache_missq_2_4_valid |
| 91 | dcache_missq_3_4_valid |
| 92 | dcache_missq_4_4_valid |
| 93 | dcache_probq_req |
| 94 | dcache_probq_1_4_valid |
| 95 | dcache_probq_2_4_valid |
| 96 | dcache_probq_3_4_valid |
| 97 | dcache_probq_4_4_valid |
| | **DCache LoadPipe 0** |
| 98 | load_req |
| 99 | load_replay |
| 100 | load_replay_for_data_nack |
| 101 | load_replay_for_no_mshr |
| 102 | load_replay_for_conflict |
| 103 | l1D_read_dcache_access |
| 104 | l1D_read_dcache_miss |
| | **DCache LoadPipe 1** |
| 105 | load_req |
| 106 | load_replay |
| 107 | load_replay_for_data_nack |
| 108 | load_replay_for_no_mshr |
| 109 | load_replay_for_conflict |
| 110 | l1D_read_dcache_access |
| 111 | l1D_read_dcache_miss |
| | **DCache LoadPipe 2** |
| 112 | load_req |
| 113 | load_replay |
| 114 | load_replay_for_data_nack |
| 115 | load_replay_for_no_mshr |
| 116 | load_replay_for_conflict |
| 117 | l1D_read_dcache_access |
| 118 | l1D_read_dcache_miss |
| 119 | dtlb_ld_access |
| 120 | dtlb_ld_miss |
| 121 | dtlb_st_access |
| 122 | dtlb_st_miss |
| 123 | PTW_tlbllptw_incount |
| 124 | PTW_tlbllptw_inblock |
| 125 | PTW_tlbllptw_memcount |
| 126 | PTW_tlbllptw_memcycle |
| 127 | PTW_access |
| 128 | PTW_l2_hit |
| 129 | PTW_l1_hit |
| 130 | PTW_l0_hit |
| 131 | PTW_sp_hit |
| 132 | PTW_pte_hit |
| 133 | PTW_rwHarzad |
| 134 | PTW_out_blocked |
| 135 | PTW_fsm_count |
| 136 | PTW_fsm_busy |
| 137 | PTW_fsm_idle |
| 138 | PTW_resp_blocked |
| 139 | PTW_mem_count |
| 140 | PTW_mem_cycle |
| 141 | PTW_mem_blocked |
| 142 | ldDeqCount |
| 143 | stDeqCount |

Table: {{processor_name}} Cache Performance Event Index Table

| Index | Event |
| ----- | ----- |
| 0 | noEvent |
| 1 | Slice0_l2_cache_refill |
| 2 | Slice0_l2_cache_rd_refill |
| 3 | Slice0_l2_cache_wr_refill |
| 4 | Slice0_l2_cache_long_miss |
| 5 | Slice0_l2_cache_hit |
| 6 | Slice0_l2_cache_miss |
| 7 | Slice0_l2_cache_access |
| 8 | Slice0_l2_cache_l2wb |
| 9 | Slice0_l2_cache_l1wb |
| 10 | Slice0_l2_cache_wb_victim |
| 11 | Slice0_l2_cache_wb_cleaning_coh |
| 12 | Slice0_l2_cache_prefetch_access |
| 13 | Slice0_l2_cache_prefetch_miss |
| 14 | Slice0_l2_cache_access_rd |
| 15 | Slice0_l2_cache_access_wr |
| 16 | Slice0_l2_cache_miss_rd |
| 17 | Slice0_l2_cache_inv |
| 18 | Slice1_l2_cache_refill |
| 19 | Slice1_l2_cache_rd_refill |
| 20 | Slice1_l2_cache_wr_refill |
| 21 | Slice1_l2_cache_long_miss |
| 22 | Slice1_l2_cache_hit |
| 23 | Slice1_l2_cache_miss |
| 24 | Slice1_l2_cache_access |
| 25 | Slice1_l2_cache_l2wb |
| 26 | Slice1_l2_cache_l1wb |
| 27 | Slice1_l2_cache_wb_victim |
| 28 | Slice1_l2_cache_wb_cleaning_coh |
| 29 | Slice1_l2_cache_prefetch_access |
| 30 | Slice1_l2_cache_prefetch_miss |
| 31 | Slice1_l2_cache_access_rd |
| 32 | Slice1_l2_cache_access_wr |
| 33 | Slice1_l2_cache_miss_rd |
| 34 | Slice1_l2_cache_inv |
| 35 | Slice2_l2_cache_refill |
| 36 | Slice2_l2_cache_rd_refill |
| 37 | Slice2_l2_cache_wr_refill |
| 38 | Slice2_l2_cache_long_miss |
| 39 | Slice2_l2_cache_hit |
| 40 | Slice2_l2_cache_miss |
| 41 | Slice2_l2_cache_access |
| 42 | Slice2_l2_cache_l2wb |
| 43 | Slice2_l2_cache_l1wb |
| 44 | Slice2_l2_cache_wb_victim |
| 45 | Slice2_l2_cache_wb_cleaning_coh |
| 46 | Slice2_l2_cache_prefetch_access |
| 47 | Slice2_l2_cache_prefetch_miss |
| 48 | Slice2_l2_cache_access_rd |
| 49 | Slice2_l2_cache_access_wr |
| 50 | Slice2_l2_cache_miss_rd |
| 51 | Slice2_l2_cache_inv |
| 52 | Slice3_l2_cache_refill |
| 53 | Slice3_l2_cache_rd_refill |
| 54 | Slice3_l2_cache_wr_refill |
| 55 | Slice3_l2_cache_long_miss |
| 56 | Slice3_l2_cache_hit |
| 57 | Slice3_l2_cache_miss |
| 58 | Slice3_l2_cache_access |
| 59 | Slice3_l2_cache_l2wb |
| 60 | Slice3_l2_cache_l1wb |
| 61 | Slice3_l2_cache_wb_victim |
| 62 | Slice3_l2_cache_wb_cleaning_coh |
| 63 | Slice3_l2_cache_prefetch_access |
| 64 | Slice3_l2_cache_prefetch_miss |
| 65 | Slice3_l2_cache_access_rd |
| 66 | Slice3_l2_cache_access_wr |
| 67 | Slice3_l2_cache_miss_rd |
| 68 | Slice3_l2_cache_inv |



## PMU-related performance event counters

The performance event counters of {{processor_name}} are divided into three
groups: machine-mode event counters, supervisor-mode event counters, and
user-mode event counters.

Table: Machine Mode Event Counter List

| Name            | Index       | Read/Write | Introduction                             | Reset value |
| --------------- | ----------- | ---------- | ---------------------------------------- | ----------- |
| MCYCLE          | 0xB00       | RW         | Machine Mode Clock Cycle Counter         | -           |
| MINSTRET        | 0xB02       | RW         | Machine-mode retired instruction counter | -           |
| MHPMCOUNTER3-31 | 0XB03-0XB1F | RW         | Machine-mode Performance Event Counter   | 0           |

The MHPMCOUNTERx counters are controlled by MHPMEVENTx, specifying the
performance events to count.

Supervisor mode event counters include the supervisor mode counter overflow
interrupt flag register (SCOUNTOVF)

Table: Supervisor Mode Counter Overflow Interrupt Flag Register (SCOUNTOVF)
Description

+------------+--------+-------+-----------------------------------------------+--------+
| Name | Bits | R/W | Behavior | Reset |
+============+========+=======+===============================================+========+
| OFVEC | 31:3 | RO | mhpmcounterx register overflow flag: | 0 | | | | | | | | |
| | 1: Overflow occurred | | | | | | | | | | | | 0: No overflow occurred | |
+------------+--------+-------+-----------------------------------------------+--------+
| -- | 2:0 | RO 0 | -- | 0 |
+------------+--------+-------+-----------------------------------------------+--------+

scountovf serves as a read-only mapping of the OF bit in the mhpmcounter
register, controlled by xcounteren:

* M-mode can read the correct value when accessing scountovf.
* HS-mode access to scountovf: When mcounteren.HPMx is 1, the corresponding
  OFVECx can read the correct value; otherwise, it only reads 0.
* When accessing scountovf in VS-mode: When both mcounteren.HPMx and
  hcounteren.HPMx are 1, the corresponding OFVECx can be read correctly;
  otherwise, it only reads 0.

Table: User Mode Event Counter List

| Name           | Index       | Read/Write | Introduction                                          | Reset value |
| -------------- | ----------- | ---------- | ----------------------------------------------------- | ----------- |
| CYCLE          | 0xC00       | RO         | User-mode read-only copy of mcycle register           | -           |
| TIME           | 0xC01       | RO         | Memory-mapped register mtime user-mode read-only copy | -           |
| INSTRET        | 0xC02       | RO         | User-mode read-only copy of minstret register         | -           |
| HPMCOUNTER3-31 | 0XC03-0XC1F | RO         | User-mode read-only copy of mhpmcounter3-31 registers | 0           |
