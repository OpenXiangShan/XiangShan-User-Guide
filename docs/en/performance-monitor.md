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
* Number of instructions committed by the hardware thread (minstret)
* Hardware Timer (time)
* Performance Event Statistics of Processor Key Components (hpmcounter3 -
  hpmcounter31, countovf)

## PMU Programming Model

### Basic Usage of PMU

The basic usage of PMU is as follows:

* Disable all performance event monitoring via the mcountinhibit register.
* Initialize performance event counters for each monitoring unit, including:
  mcycle, minstret, mhpmcounter3 - mhpmcounter31.
* Configure each performance event selector for monitoring units, including:
  mhpmcounter3 - mhpmcounter31. {{processor_name}} allows up to four event
  combinations per event selector. After writing the event index value, event
  combination method, and sampling privilege level into the event selector,
  normal counting of configured events can proceed under the specified sampling
  privilege level, with results accumulated into the event counter based on the
  combined outcome.
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
| Name | Bitfield | R/W | Behavior | Reset Value |
+========+========+=======+============================================+==========+
| HPMx | 31:4 | RW | mhpmcounterx register count disable bit: | 0 | | | | | | |
| | | | 0: Normal counting | | | | | | | | | | | | 1: Counting disabled | |
+--------+--------+-------+--------------------------------------------+----------+
| IR | 3 | RW | minstret register count disable bit: | 0 | | | | | | | | | | |
0: Normal counting | | | | | | | | | | | | 1: Counting disabled | |
+--------+--------+-------+--------------------------------------------+----------+
| -- | 2 | RO 0 | Reserved | 0 |
+--------+--------+-------+--------------------------------------------+----------+
| CY | 1 | RW | mcycle register count disable bit: | 0 | | | | | | | | | | | 0:
Normal counting | | | | | | | | | | | | 1: Counting disabled | |
+--------+--------+-------+--------------------------------------------+----------+

### Machine-mode Performance Counter Event Access Enable Register (MCOUNTEREN)

The Machine-mode Performance Event Counter Access Enable Register (mcounteren)
is a 32-bit WARL register primarily used to control access permissions for
user-mode performance monitoring counters at privilege levels below machine mode
(HS-mode/VS-mode/HU-mode/VU-mode).

Table: Machine Mode Performance Event Counter Access Authorization Register
Description

+--------+--------+-------+------------------------------------------------+----------+
| Name | Bits | R/W | Behavior | Reset |
+========+========+=======+================================================+==========+
| HPMx | 31:4 | RW | hpmcounterenx register M-mode lower privilege access bits:
| 0 | | | | | | | | | | | 0: Accessing hpmcounterx raises illegal instruction
exception | | | | | | | | | | | | 1: Allows normal access to hpmcounterx | |
+--------+--------+-------+------------------------------------------------+----------+
| IR | 3 | RW | instret register M-mode lower privilege access bit: | 0 | | | |
| | | | | | | 0: Accessing instret raises illegal instruction exception | | | |
| | | | | | | | 1: Allows normal access | |
+--------+--------+-------+------------------------------------------------+----------+
| TM | 2 | RW | time/stimecmp register M-mode lower privilege access bit: | 0 |
| | | | | | | | | | 0: Accessing time raises illegal instruction exception | | |
| | | | | | | | | 1: Allows normal access | |
+--------+--------+-------+------------------------------------------------+----------+
| CY | 1 | RW | cycle register M-mode lower privilege access bit: | 0 | | | | |
| | | | | | 0: Accessing cycle raises illegal instruction exception | | | | | |
| | | | | | 1: Allows normal access | |
+--------+--------+-------+------------------------------------------------+----------+

### Supervisor-mode Performance Counter Access Enable Register (SCOUNTEREN)

Supervisor-mode Performance Counter Access Enable Register (scounteren) is a
32-bit WARL register primarily used to control user-mode access permissions for
performance monitoring counters in HU-mode/VU-mode.

Table: Supervisor Mode Performance Event Counter Access Authorization Register
Description

+--------+--------+-------+------------------------------------------------+----------+
| Name | Bits | R/W | Behavior | Reset |
+========+========+=======+================================================+==========+
| HPMx | 31:4 | RW | hpmcounterenx register user-mode access bit: | 0 | | | | |
| | | | | | 0: Accessing hpmcounterx raises illegal instruction exception | | |
| | | | | | | | | 1: Normal access to hpmcounterx allowed | |
+--------+--------+-------+------------------------------------------------+----------+
| IR | 3 | RW | instret register user-mode access bit: | 0 | | | | | | | | | | |
0: Accessing instret raises illegal instruction exception | | | | | | | | | | |
| 1: Normal access allowed | |
+--------+--------+-------+------------------------------------------------+----------+
| TM | 2 | RW | time register user-mode access bit: | 0 | | | | | | | | | | | 0:
Accessing time raises illegal instruction exception | | | | | | | | | | | | 1:
Normal access allowed | |
+--------+--------+-------+------------------------------------------------+----------+
| CY | 1 | RW | cycle register user-mode access bit: | 0 | | | | | | | | | | |
0: Accessing cycle raises illegal instruction exception | | | | | | | | | | | |
1: Normal access allowed | |
+--------+--------+-------+------------------------------------------------+----------+

### Virtualization Mode Performance Event Counter Access Authorization Register (HCOUNTEREN)

The Virtualization Mode Performance Event Counter Access Authorization Register
(hcounteren) is a 32-bit WARL register primarily used to control user-mode
performance monitoring counter access permissions in guest virtual machines
(VS-mode/VU-mode).

Table: Supervisor Mode Performance Event Counter Access Authorization Register
Description

+--------+--------+-------+------------------------------------------------+----------+
| Name | Bitfield | R/W | Behavior | Reset Value |
+========+========+=======+================================================+==========+
| HPMx | 31:4 | RW | hpmcounterenx register guest VM access permission bit: | 0
| | | | | | | | | | | 0: Accessing hpmcounterx raises illegal instruction
exception | | | | | | | | | | | | 1: Normal access to hpmcounterx is permitted |
|
+--------+--------+-------+------------------------------------------------+----------+
| IR | 3 | RW | instret register guest VM access permission bit: | 0 | | | | | |
| | | | | 0: Accessing instret raises illegal instruction exception | | | | | |
| | | | | | 1: Normal access is permitted | |
+--------+--------+-------+------------------------------------------------+----------+
| TM | 2 | RW | time/vstimecmp(via stimecmp) register guest VM | 0 | | | | |
access permission bit: | | | | | | | | | | | | 0: Accessing time raises illegal
instruction exception | | | | | | | | | | | | 1: Normal access is permitted | |
+--------+--------+-------+------------------------------------------------+----------+
| CY | 1 | RW | cycle register guest VM access permission bit: | 0 | | | | | | |
| | | | 0: Accessing cycle raises illegal instruction exception | | | | | | | |
| | | | 1: Normal access is permitted | |
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

| Index | Event                   |
| ----- | ----------------------- |
| 0     | noEvent                 |
| 1     | frontendFlush           |
| 2     | ifu_req                 |
| 3     | ifu_miss                |
| 4     | ifu_req_cacheline_0     |
| 5     | ifu_req_cacheline_1     |
| 6     | ifu_req_cacheline_0_hit |
| 7     | ifu_req_cacheline_1_hit |
| 8     | only_0_hit              |
| 9     | only_0_miss             |
| 10    | hit_0_hit_1             |
| 11    | hit_0_miss_1            |
| 12    | miss_0_hit_1            |
| 13    | miss_0_miss_1           |
| 14    | IBuffer_Flushed         |
| 15    | IBuffer_hungry          |
| 16    | IBuffer_1_4_valid       |
| 17    | IBuffer_2_4_valid       |
| 18    | IBuffer_3_4_valid       |
| 19    | IBuffer_4_4_valid       |
| 20    | IBuffer_full            |
| 21    | Front_Bubble            |
| 22    | icache_miss_cnt         |
| 23    | icache_miss_penalty     |
| 24    | bpu_s2_redirect         |
| 25    | bpu_s3_redirect         |
| 26    | bpu_to_ftq_stall        |
| 27    | mispredictRedirect      |
| 28    | replayRedirect          |
| 29    | predecodeRedirect       |
| 30    | to_ifu_bubble           |
| 31    | from_bpu_real_bubble    |
| 32    | BpInstr                 |
| 33    | BpBInstr                |
| 34    | BpRight                 |
| 35    | BpWrong                 |
| 36    | BpBRight                |
| 37    | BpBWrong                |
| 38    | BpJRight                |
| 39    | BpJWrong                |
| 40    | BpIRight                |
| 41    | BpIWrong                |
| 42    | BpCRight                |
| 43    | BpCWrong                |
| 44    | BpRRight                |
| 45    | BpRWrong                |
| 46    | ftb_false_hit           |
| 47    | ftb_hit                 |
| 48    | fauftb_commit_hit       |
| 49    | fauftb_commit_miss      |
| 50    | tage_tht_hit            |
| 51    | sc_update_on_mispred    |
| 52    | sc_update_on_unconf     |
| 53    | ftb_commit_hits         |
| 54    | ftb_commit_misses       |

Table: {{processor_name}} Backend Performance Event Index Table

| Index | Event                                                        |
| ----- | ------------------------------------------------------------ |
| 0     | noEvent                                                      |
| 1     | decoder_fused_instr                                          |
| 2     | decoder_waitInstr                                            |
| 3     | decoder_stall_cycle                                          |
| 4     | decoder_utilization                                          |
| 5     | rename_in                                                    |
| 6     | rename_waitinstr                                             |
| 7     | rename_stall                                                 |
| 8     | rename_stall_cycle_walk                                      |
| 9     | rename_stall_cycle_dispatch                                  |
| 10    | rename_stall_cycle_int                                       |
| 11    | rename_stall_cycle_fp                                        |
| 12    | rename_stall_cycle_vec                                       |
| 13    | rename_stall_cycle_v0                                        |
| 14    | rename_stall_cycle_vl                                        |
| 15    | me_freelist_1_4_valid                                        |
| 16    | me_freelist_2_4_valid                                        |
| 17    | me_freelist_3_4_valid                                        |
| 18    | me_freelist_4_4_valid                                        |
| 19    | std_freelist_1_4_valid                                       |
| 20    | std_freelist_2_4_valid                                       |
| 21    | std_freelist_3_4_valid                                       |
| 22    | std_freelist_4_4_valid                                       |
| 23    | std_freelist_1_4_valid                                       |
| 24    | std_freelist_2_4_valid                                       |
| 25    | std_freelist_3_4_valid                                       |
| 26    | std_freelist_4_4_valid                                       |
| 27    | std_freelist_1_4_valid                                       |
| 28    | std_freelist_2_4_valid                                       |
| 29    | std_freelist_3_4_valid                                       |
| 30    | std_freelist_4_4_valid                                       |
| 31    | std_freelist_1_4_valid                                       |
| 32    | std_freelist_2_4_valid                                       |
| 33    | std_freelist_3_4_valid                                       |
| 34    | std_freelist_4_4_valid                                       |
| 35    | dispatch_in                                                  |
| 36    | dispatch_empty                                               |
| 37    | dispatch_utili                                               |
| 38    | dispatch_waitinstr                                           |
| 39    | dispatch_stall_cycle_lsq                                     |
| 40    | dispatch_stall_cycle_rob                                     |
| 41    | dispatch_stall_cycle_int_dq                                  |
| 42    | dispatch_stall_cycle_fp_dq                                   |
| 43    | dispatch_stall_cycle_ls_dq                                   |
| 44    | dispatchq1_in                                                |
| 45    | dispatchq1_out                                               |
| 46    | dispatchq1_out_try                                           |
| 47    | dispatchq1_fake_block                                        |
| 48    | dispatchq1_1_4_valid                                         |
| 49    | dispatchq1_2_4_valid                                         |
| 50    | dispatchq1_3_4_valid                                         |
| 51    | dispatchq1_4_4_valid                                         |
| 52    | dispatchq2_in                                                |
| 53    | dispatchq2_out                                               |
| 54    | dispatchq2_out_try                                           |
| 55    | dispatchq2_fake_block                                        |
| 56    | dispatchq2_1_4_valid                                         |
| 57    | dispatchq2_2_4_valid                                         |
| 58    | dispatchq2_3_4_valid                                         |
| 59    | dispatchq2_4_4_valid                                         |
| 60    | dispatchq3_in                                                |
| 61    | dispatchq3_out                                               |
| 62    | dispatchq3_out_try                                           |
| 63    | dispatchq3_fake_block                                        |
| 64    | dispatchq3_1_4_valid                                         |
| 65    | dispatchq3_2_4_valid                                         |
| 66    | dispatchq3_3_4_valid                                         |
| 67    | dispatchq3_4_4_valid                                         |
| 68    | dispatchq4_in                                                |
| 69    | dispatchq4_out                                               |
| 70    | dispatchq4_out_try                                           |
| 71    | dispatchq4_fake_block                                        |
| 72    | dispatchq4_1_4_valid                                         |
| 73    | dispatchq4_2_4_valid                                         |
| 74    | dispatchq4_3_4_valid                                         |
| 75    | dispatchq4_4_4_valid                                         |
| 76    | rob_interrupt_num                                            |
| 77    | rob_exception_num                                            |
| 78    | rob_flush_pipe_num                                           |
| 79    | rob_replay_inst_num                                          |
| 80    | rob_commitUop                                                |
| 81    | rob_commitInstr                                              |
| 82    | rob_commitInstrMove                                          |
| 83    | rob_commitInstrFused                                         |
| 84    | rob_commitInstrLoad                                          |
| 85    | rob_commitInstrBranch                                        |
| 86    | rob_commitInstrLoadWait                                      |
| 87    | rob_commitInstrStore                                         |
| 88    | rob_walkInstr                                                |
| 89    | rob_walkCycle                                                |
| 90    | rob_1_4_valid                                                |
| 91    | rob_2_4_valid                                                |
| 92    | rob_3_4_valid                                                |
| 93    | rob_4_4_valid                                                |
| 94    | dispatch2Iq1_out_fire_cnt                                    |
| 95    | issueQueue_enq_fire_cnt                                      |
| 96    | IssueQueueAluMulBkuBrhJmp_full                               |
| 97    | IssueQueueAluMulBkuBrhJmp_full                               |
| 98    | IssueQueueAluBrhJmpI2fVsetriwiVsetriwvf_full                 |
| 99    | IssueQueueAluCsrFenceDiv_full                                |
| 100   | dispatch2Iq2_out_fire_cnt                                    |
| 101   | issueQueue_enq_fire_cnt                                      |
| 102   | IssueQueueFaluFcvtF2vFmac_full                               |
| 103   | IssueQueueFaluFmac_full                                      |
| 104   | IssueQueueFaluFmac_full                                      |
| 105   | IssueQueueFaluFmac_full                                      |
| 106   | IssueQueueFdiv_full                                          |
| 107   | dispatch2Iq3_out_fire_cnt                                    |
| 108   | issueQueue_enq_fire_cnt                                      |
| 109   | IssueQueueVfmaVialuFixVimacVppuVfaluVfcvtVipuVsetrvfwvf_full |
| 110   | IssueQueueVfmaVialuFixVfaluVfcvt_full                        |
| 111   | IssueQueueVfdivVidiv_full                                    |
| 112   | dispatch2Iq4_out_fire_cnt                                    |
| 113   | issueQueue_enq_fire_cnt                                      |
| 114   | IssueQueueStaMou_full                                        |
| 115   | IssueQueueStaMou_full                                        |
| 116   | IssueQueueLdu_full                                           |
| 117   | IssueQueueLdu_full                                           |
| 118   | IssueQueueLdu_full                                           |
| 119   | IssueQueueVlduVstuVseglduVsegstu_full                        |
| 120   | IssueQueueVlduVstu_full                                      |
| 121   | IssueQueueStdMoud_full                                       |
| 122   | IssueQueueStdMoud_full                                       |
| 123   | bt_std_freelist_1_4_valid                                    |
| 124   | bt_std_freelist_2_4_valid                                    |
| 125   | bt_std_freelist_3_4_valid                                    |
| 126   | bt_std_freelist_4_4_valid                                    |
| 127   | bt_std_freelist_1_4_valid                                    |
| 128   | bt_std_freelist_2_4_valid                                    |
| 129   | bt_std_freelist_3_4_valid                                    |
| 130   | bt_std_freelist_4_4_valid                                    |
| 131   | bt_std_freelist_1_4_valid                                    |
| 132   | bt_std_freelist_2_4_valid                                    |
| 133   | bt_std_freelist_3_4_valid                                    |
| 134   | bt_std_freelist_4_4_valid                                    |
| 135   | bt_std_freelist_1_4_valid                                    |
| 136   | bt_std_freelist_2_4_valid                                    |
| 137   | bt_std_freelist_3_4_valid                                    |
| 138   | bt_std_freelist_4_4_valid                                    |
| 139   | bt_std_freelist_1_4_valid                                    |
| 140   | bt_std_freelist_2_4_valid                                    |
| 141   | bt_std_freelist_3_4_valid                                    |
| 142   | bt_std_freelist_4_4_valid                                    |

Table: {{processor_name}} Memory Access Performance Event Index Table

| Index | Event                             |
| ----- | --------------------------------- |
| 0     | noEvent                           |
| 1     | load_s0_in_fire                   |
| 2     | load_to_load_forward              |
| 3     | stall_dcache                      |
| 4     | load_s1_in_fire                   |
| 5     | load_s1_tlb_miss                  |
| 6     | load_s2_in_fire                   |
| 7     | load_s2_dcache_miss               |
| 8     | load_s0_in_fire (LoadUnit_1)      |
| 9     | load_to_load_forward (LoadUnit_1) |
| 10    | stall_dcache (LoadUnit_1)         |
| 11    | load_s1_in_fire (LoadUnit_1)      |
| 12    | load_s1_tlb_miss (LoadUnit_1)     |
| 13    | load_s2_in_fire (LoadUnit_1)      |
| 14    | load_s2_dcache_miss (LoadUnit_1)  |
| 15    | load_s0_in_fire (LoadUnit_2)      |
| 16    | load_to_load_forward (LoadUnit_2) |
| 17    | stall_dcache (LoadUnit_2)         |
| 18    | load_s1_in_fire (LoadUnit_2)      |
| 19    | load_s1_tlb_miss (LoadUnit_2)     |
| 20    | load_s2_in_fire (LoadUnit_2)      |
| 21    | load_s2_dcache_miss (LoadUnit_2)  |
| 22    | sbuffer_req_valid                 |
| 23    | sbuffer_req_fire                  |
| 24    | sbuffer_merge                     |
| 25    | sbuffer_newline                   |
| 26    | dcache_req_valid                  |
| 27    | dcache_req_fire                   |
| 28    | sbuffer_idle                      |
| 29    | sbuffer_flush                     |
| 30    | sbuffer_replace                   |
| 31    | mpipe_resp_valid                  |
| 32    | replay_resp_valid                 |
| 33    | coh_timeout                       |
| 34    | sbuffer_1_4_valid                 |
| 35    | sbuffer_2_4_valid                 |
| 36    | sbuffer_3_4_valid                 |
| 37    | sbuffer_full_valid                |
| 38    | enq (LsqWrapper)                  |
| 39    | ld_ld_violation (LsqWrapper)      |
| 40    | enq (LsqWrapper)                  |
| 41    | stld_rollback (LsqWrapper)        |
| 42    | enq (LsqWrapper)                  |
| 43    | deq (LsqWrapper)                  |
| 44    | deq_block (LsqWrapper)            |
| 45    | replay_full (LsqWrapper)          |
| 46    | replay_rar_nack (LsqWrapper)      |
| 47    | replay_raw_nack (LsqWrapper)      |
| 48    | replay_nuke (LsqWrapper)          |
| 49    | replay_mem_amb (LsqWrapper)       |
| 50    | replay_tlb_miss (LsqWrapper)      |
| 51    | replay_bank_conflict (LsqWrapper) |
| 52    | replay_dcache_replay (LsqWrapper) |
| 53    | replay_forward_fail (LsqWrapper)  |
| 54    | replay_dcache_miss (LsqWrapper)   |
| 55    | full_mask_000 (LsqWrapper)        |
| 56    | full_mask_001 (LsqWrapper)        |
| 57    | full_mask_010 (LsqWrapper)        |
| 58    | full_mask_011 (LsqWrapper)        |
| 59    | full_mask_100 (LsqWrapper)        |
| 60    | full_mask_101 (LsqWrapper)        |
| 61    | full_mask_110 (LsqWrapper)        |
| 62    | full_mask_111 (LsqWrapper)        |
| 63    | nuke_rollback (LsqWrapper)        |
| 64    | nack_rollback (LsqWrapper)        |
| 65    | mmioCycle (LsqWrapper)            |
| 66    | mmioCnt (LsqWrapper)              |
| 67    | mmio_wb_success (LsqWrapper)      |
| 68    | mmio_wb_blocked (LsqWrapper)      |
| 69    | stq_1_4_valid (LsqWrapper)        |
| 70    | stq_2_4_valid (LsqWrapper)        |
| 71    | stq_3_4_valid (LsqWrapper)        |
| 72    | stq_4_4_valid (LsqWrapper)        |
| 73    | dcache_wbq_req                    |
| 74    | dcache_wbq_1_4_valid              |
| 75    | dcache_wbq_2_4_valid              |
| 76    | dcache_wbq_3_4_valid              |
| 77    | dcache_wbq_4_4_valid              |
| 78    | dcache_mp_req                     |
| 79    | dcache_mp_total_penalty           |
| 80    | dcache_missq_req                  |
| 81    | dcache_missq_1_4_valid            |
| 82    | dcache_missq_2_4_valid            |
| 83    | dcache_missq_3_4_valid            |
| 84    | dcache_missq_4_4_valid            |
| 85    | dcache_probq_req                  |
| 86    | dcache_probq_1_4_valid            |
| 87    | dcache_probq_2_4_valid            |
| 88    | dcache_probq_3_4_valid            |
| 89    | dcache_probq_4_4_valid            |
| 90    | load_req                          |
| 91    | load_replay                       |
| 92    | load_replay_for_data_nack         |
| 93    | load_replay_for_no_mshr           |
| 94    | load_replay_for_conflict          |
| 95    | load_req                          |
| 96    | load_replay                       |
| 97    | load_replay_for_data_nack         |
| 98    | load_replay_for_no_mshr           |
| 99    | load_replay_for_conflict          |
| 100   | load_req                          |
| 101   | load_replay                       |
| 102   | load_replay_for_data_nack         |
| 103   | load_replay_for_no_mshr           |
| 104   | load_replay_for_conflict          |
| 105   | tlbllptw_incount                  |
| 106   | tlbllptw_inblock                  |
| 107   | tlbllptw_memcount                 |
| 108   | tlbllptw_memcycle                 |
| 109   | pagetablecache_access             |
| 110   | pagetablecache_l2_hit             |
| 111   | pagetablecache_l1_hit             |
| 112   | pagetablecache_l0_hit             |
| 113   | pagetablecache_sp_hit             |
| 114   | pagetablecache_pte_hit            |
| 115   | pagetablecache_rwHarzad           |
| 116   | pagetablecache_out_blocked        |
| 117   | fsm_count                         |
| 118   | fsm_busy                          |
| 119   | fsm_idle                          |
| 120   | resp_blocked                      |
| 121   | mem_count                         |
| 122   | mem_cycle                         |
| 123   | out_blocked                       |
| 124   | ldDeqCount (MemBlockInlined)      |
| 125   | stDeqCount (MemBlockInlined)      |

Table: {{processor_name}} Cache Performance Event Index Table

| Index | Event               |
| ----- | ------------------- |
| 0     | noEvent             |
| 1     | req_buffer_merge    |
| 2     | req_buffer_flow     |
| 3     | req_buffer_alloc    |
| 4     | req_buffer_full     |
| 5     | recv_prefetch       |
| 6     | recv_normal         |
| 7     | nrWorkingABCmshr    |
| 8     | nrWorkingBmshr      |
| 9     | nrWorkingCmshr      |
| 10    | conflictA           |
| 11    | conflictByPrefetch  |
| 12    | conflictB           |
| 13    | conflictC           |
| 14    | client_dir_conflict |
| 15    | selfdir_A_req       |
| 16    | selfdir_A_hit       |
| 17    | selfdir_B_req       |
| 18    | selfdir_B_hit       |
| 19    | selfdir_C_req       |
| 20    | selfdir_C_hit       |
| 21    | selfdir_dirty       |
| 22    | selfdir_TIP         |
| 23    | selfdir_BRANCH      |
| 24    | selfdir_TRUNK       |
| 25    | selfdir_INVALID     |



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
