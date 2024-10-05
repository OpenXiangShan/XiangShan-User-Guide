---
file_authors_:
- ZHANG Jian <zhangjian@bosc.ac.cn>
---

## 指令集
如[概述]所述，XS-K220支持RVA23部分特性和Server SOC spec部分特性。本节着重描述CPU core部分。debug和中断部分分别详见[]和[]。

### RISC-V指令集介绍
RISC-V服务器规范——Server platform specification——包括如下四个方面
- RVA profile;
- Server SOC spec;
- BRS(Boot and Runtime Services);
- RISC-V security platform model.

其中每个规范簇还包括制定中的验证规范。RVA隶属于RVx profile，分为RVA，RVB和RVM三个规范，这一系列规范的目标是在ISA之上统一RISC-V的指令集组合（TODO 加上RVI相应基金会charter的内容）。相关工作组包括TSC下面的profile和ACT，以及和TSC平级的CSC(Certification Steering Commitee)。其中RVA profile是针对应用处理器的规范。

#### RVA23 profile简介
RVA23 profile共包含80个指令集，其中包括53个必选（32个U必选和21个S必选），27个可选中还包括5个服务器必选特性。对于一个服务器场景的CPU，目标是支持前述55个指令集。
#### XS-K220指令集支持情况
TODO 表格? 序号需要修正
序	指令集
1	A
2	C
3	D
4	F
5	H
6	M
7	debug
8	Sdext
9	Sdtrig
10	Shcounterenw
11	Shgatpa
12	Shtvala
13	Shvsatpa
14	Shvstvala
15	Shvstvecd
18	Ss1p13
19	Ssccptr
20	Sscofpmf
21	Sscounterenw
22	Ssstateen
23	Sstc
24	Sstvala
25	Sstvecd
26	Ssu64xl
27	Sv39
28	Sv48
29	Svade
30	Svbare
31	Svinval
32	Svnapot
33	Svpbmt
34	V
35	Za64rs
36	Zba
37	Zbb
38	Zbc
39	Zbs
40	Zcmop
41	Zfa
42	Zfhmin
43	Zicbom
44	Zicbop
45	Zicboz
46	Ziccamoa
47	Ziccif
48	Zicclsm（支持标量）
49	Ziccrse
50	Zicntr
51	Zicond
52	Zicsr
53	Zifencei
54	Zihpm
55	Zkt
56	Zvbb
57	Zvfhmin
58	Zvkt

### 指令集支持情况
#### 非特权指令
TODO 表格? 序号需要修正
序	指令集
1	A
2	C
3	D
4	F
5	H
6	M
34	V
35	Za64rs
36	Zba
37	Zbb
38	Zbc
39	Zbs
40	Zcmop
41	Zfa
42	Zfhmin
43	Zicbom
44	Zicbop
45	Zicboz
46	Ziccamoa
47	Ziccif
48	Zicclsm（支持标量）
49	Ziccrse
50	Zicntr
51	Zicond
52	Zicsr
53	Zifencei
54	Zihpm
55	Zkt
56	Zvbb
57	Zvfhmin
58	Zvkt

#### 特权指令
TODO 表格? 序号需要修正
序	| 指令集        | 所属章节
7	| debug         | debug.md
8	| Sdext         | debug.md
9	| Sdtrig        | debug.md
10	| Shcounterenw  | performance-monitor.md
11	| Shgatpa       |
12	| Shtvala       |
13	| Shvsatpa      |
14	| Shvstvala     |
15	| Shvstvecd     |
18	| Ss1p13        |
19	| Ssccptr       | performance-monitor.md
20	| Sscofpmf      | performance-monitor.md
21	| Sscounterenw  | performance-monitor.md
22	| Ssstateen     |
23	| Sstc          |
24	| Sstvala       |
25	| Sstvecd       |
26	| Ssu64xl       |
27	| Sv39          |
28	| Sv48          |
29	| Svade         |
30	| Svbare        |
31	| Svinval       |
32	| Svnapot       |
33	| Svpbmt        |

### 非指令集支持情况
debug和中断部分分别详见[]和[]。

