---
file_authors_:
- zengjinhong <zengjinhong21@mails.ucas.ac.cn>
- Xu Zefan <xuzefan@mail.ustc.edu.cn>
- Tang Haojin <tanghaojin@outlook.com>
---

# Privilege Modes and Control and Status Registers (CSRs) {#sec:mode-and-csr}

## Processor mode

{{processor_name}} supports the following six privilege modes as specified in
the RISC-V Privileged Architecture Manual.

Table: List of privilege modes supported by {{processor_name}}

| Name                    | Abbreviation | PRV |  V  |
| ----------------------- | :----------: | :-: | :-: |
| Machine mode            |      M       |  3  |  0  |
| Supervisor mode         |     HS/S     |  1  |  0  |
| User mode               |      U       |  0  |  0  |
| Virtual Supervisor Mode |      VS      |  1  |  1  |
| Virtual user mode       |      VU      |  0  |  1  |
| Debug Mode              |      D       |     |     |

The {{processor_name}} initializes in M mode. For general scenarios, the
privilege hierarchy is M > S > U; for virtualization scenarios, the hierarchy is
M > HS > VS > VU.

### Machine mode

Machine mode (M-mode), defined by the machine-level ISA, possesses the highest
privilege level. M-mode is typically used for machine firmware and exhibits the
following characteristics:

* In M-mode, all M, S, H, VS, and U CSRs are accessible, but some debug-mode
  CSRs remain inaccessible.
* Machine mode typically fetches instructions and accesses memory using physical
  addresses, without virtual address translation, except in the following cases:
  * `mstatus` .MPRV = 1 When MPRV is set to 1, load and store operations perform
    virtual address translation according to the mode specified by the MPP
    field.
  * When using virtual machine load/store instructions such as HLV, HLVX, and
    HSV, two-stage address translation is performed according to the virtual
    mode (VS or VU) specified by the SPVP field in `hstatus`.
* M-mode instruction fetch and memory access typically do not undergo PMP checks
  and have permissions by default, except in the following cases:
  * When load/store operations are executed in other privilege modes under the
    above conditions, PMP checks are performed according to their respective
    privilege modes.
  * When a PMP entry is locked, both instruction fetch and memory access
    operations must check the permissions of this PMP entry.

### Supervisor mode

Supervisor mode (S-mode) is defined by the supervisor-level ISA, and the
virtualization extension expands it into Hypervisor-extended supervisor mode
(HS-mode). S/HS-mode is typically used for operating systems and hypervisors,
with the following characteristics:

* In S/HS mode, S, H, VS, and U CSRs are accessible, while M CSRs and debug mode
  CSRs are not.
* Fetch and memory access in S-mode typically require virtual address
  translation based on the satp register, except in the following cases:
  * When using virtual machine load/store instructions such as HLV, HLVX, and
    HSV, two-stage address translation is performed according to the virtual
    mode (VS or VU) specified by the `hstatus`.SPVP field.
* S-mode always requires PMP checks.
* S-mode cannot execute M-mode privileged instructions.

### User mode

User mode (U-mode) has the following characteristics:

* U-mode can only access non-privileged CSRs, mainly including floating-point,
  vector, and non-privileged counter CSRs.
* Fetch and memory access in U-mode typically require virtual address
  translation based on the satp register, except in the following cases:
  * When `hstatus`.HU = 1, and using virtual machine load/store instructions
    such as HLV, HLVX, and HSV, two-stage address translation is performed
    according to the virtual mode (VS or VU) specified by the SPVP field in
    `hstatus`.
* U-mode always requires PMP checks.
* U-mode typically cannot execute privileged instructions, with some exceptions
  under specific circumstances.

### Virtual Supervisor Mode

The Virtual Supervisor Mode (VS mode) introduced by virtualization extensions
has the following characteristics:

* In VS mode, S and U CSRs are accessible, but M, H, and VS CSRs are not.
* Accessing specific S-mode registers in VS mode will be redirected to the
  corresponding VS registers.
* In VS mode, instruction fetch and memory access typically require two-stage
  address translation based on the hgatp and vsatp registers.
* VS mode always requires PMP checks.
* VS mode cannot execute M-mode privileged instructions, nor H privileged
  instructions.

### Virtual user mode

Virtual user mode (VU-mode), introduced by the virtualization extension, has the
following characteristics:

* VU-mode can only access non-privileged CSRs, primarily including
  floating-point, vector, and non-privileged counter CSRs.
* Instruction fetch and memory access in VU-mode generally require two-stage
  address translation based on the hgatp and vsatp registers.
* VU mode always requires PMP checks.
* VU mode typically cannot execute privileged instructions.

### Debug mode

Debug mode (Debug mode) is introduced by the Debug extension, and its features
and details can be found in [@sec:debug] [Debug](debug.md).

## Control and Status Registers (CSRs)

We will group and introduce Control and Status Registers (CSRs) based on their
privilege levels.

### User mode readable and writable CSRs

The CSRs implemented in {{processor_name}} with User Mode Read-Write (URW)
permissions in RISC-V are shown in the following table:

Table: List of URW CSRs Supported by {{processor_name}}

|  Name  | Privilege Level | Number |                      Description                      |             Group             |
| :----: | :-------------: | :----: | :---------------------------------------------------: | :---------------------------: |
| fflags |        U        | 0x001  | Floating-point exception accumulation status register | Non-privileged Floating-point |
|  frm   |        U        | 0x002  |     Floating-Point Dynamic Rounding Mode Register     | Non-privileged Floating-point |
|  fcsr  |        U        | 0x003  |      Floating-point control and status register       | Non-privileged Floating-point |
| vstart |        U        | 0x008  |            Vector start position register             |     Non-privileged Vector     |
| vxsat  |        U        | 0x009  |          Fixed-point overflow flag register           |     Non-privileged Vector     |
|  vxrm  |        U        | 0x00A  |          Fixed-point rounding mode register           |     Non-privileged Vector     |
|  vcsr  |        U        | 0x00F  |          Vector control and status register           |     Non-privileged Vector     |
|   vl   |        U        | 0xC20  |                Vector Length Register                 |     Non-privileged Vector     |
| vtype  |        U        | 0xC21  |               Vector Data Type Register               |     Non-privileged Vector     |
| vlenb  |        U        | 0xC22  |          Vector register byte count register          |     Non-privileged Vector     |

### User-mode read-only CSRs

The RISC-V CSRs implemented in {{processor_name}} with user-mode read-only (URO)
permissions are listed in the following table:

Table: List of URO CSRs Supported by {{processor_name}}

|     Name     | Privilege Level | Number |              Description              |       Group       |
| :----------: | :-------------: | :----: | :-----------------------------------: | :---------------: |
|    cycle     |        U        | 0xC00  |        User mode cycle counter        | User mode counter |
|     time     |        U        | 0xC01  |        User-mode time counter         | User mode counter |
|   instret    |        U        | 0xC02  | User-mode retired instruction counter | User mode counter |
| hpmcounter3  |        U        | 0xC03  |          User Mode Counter 3          | User mode counter |
|     ...      |       ...       |  ...   |                  ...                  |        ...        |
| hpmcounter31 |        U        | 0xC1F  |         User-mode Counter 31          | User mode counter |

### Supervisor mode readable/writable CSRs

The RISC-V CSRs implemented in {{processor_name}} with supervisor mode
read-write (SRW) permissions are listed in the table below:

Table: List of SRW CSRs supported by {{processor_name}}

|    Name    | Privilege Level | Number |                             Description                             |                    Group                    |
| :--------: | :-------------: | :----: | :-----------------------------------------------------------------: | :-----------------------------------------: |
|  sstatus   |        S        | 0x100  |              Supervisor Mode Processor Status Register              |                Trap setting                 |
|    sie     |        S        | 0x104  |          Supervisor mode interrupt enable control register          |                Trap setting                 |
|   stvec    |        S        | 0x105  |          Supervisor mode trap vector base address register          |                Trap setting                 |
| scounteren |        S        | 0x106  |           Supervisor Mode Counter Enable Control Register           |                Trap setting                 |
|  senvcfg   |        S        | 0x10A  |         Supervisor mode environment configuration register          |    Supervisor Environment Configuration     |
|  sscratch  |        S        | 0x140  |         Supervisor mode trap temporary data backup register         |                Trap handling                |
|    sepc    |        S        | 0x141  |            Supervisor-mode Trap Reserved Program Counter            |                Trap handling                |
|   scause   |        S        | 0x142  |                 Supervisor mode trap cause register                 |                Trap handling                |
|   stval    |        S        | 0x143  |                   Supervisor Trap Vector Register                   |                Trap handling                |
|    sip     |        S        | 0x144  |             Supervisor mode event wait status register              |                Trap handling                |
|  stimecmp  |        S        | 0x14D  |       Supervisor-mode timer interrupt compare value register        |                Trap setting                 |
|  siselect  |        S        | 0x150  |      Supervisor Mode Indirect Register Select Signal Register       |     Supervisor indirect access register     |
|   sireg    |        S        | 0x151  |          Supervisor Mode Indirect Register Alias Register           |     Supervisor indirect access register     |
|   stopei   |        S        | 0x15C  |           Supervisor mode top external interrupt register           |            Supervisor interrupt             |
|    satp    |        S        | 0x180  | Supervisor mode virtual address translation and protection register |    Supervisor Protection and Translation    |
|  scontext  |     S/Debug     | 0x5A8  |                  Supervisor Mode Context Register                   |               Debug register                |
|   sbpctl   |        S        | 0x5C0  |        Speculative State Branch Prediction Control Register         | Prediction status branch prediction control |
|   spfctl   |        S        | 0x5C1  |             Speculative state prefetch control register             | Prediction status branch prediction control |
| slvpredctl |        S        | 0x5C2  |    Speculative state LOAD violation prediction control register     | Prediction status branch prediction control |
| smblockctl |        S        | 0x5C3  |           Speculative State Memory Block Control Register           | Prediction status branch prediction control |
|   srnctl   |        S        | 0x5C4  |             Speculative State Runtime Control Register              |      Speculative state runtime control      |

### Supervisor-mode read-only CSRs

The RISC-V CSRs implemented in {{processor_name}} with Supervisor Read-Only
(SRO) privilege are listed in the following table:

Table: List of SRO CSRs supported by {{processor_name}}

| Name  | Privilege Level | Number |             Description              |        Group         |
| :---: | :-------------: | :----: | :----------------------------------: | :------------------: |
| stopi |        S        | 0xDB0  | Supervisor-level top-level interrupt | Supervisor interrupt |

### Virtual Supervisor-mode Read-Write CSRs

The CSRs implemented in {{processor_name}} with Virtual Supervisor Mode
read-write (HRW) permissions are listed in the table below:

Table: List of HRW CSRs Supported by {{processor_name}}

|    Name    | Privilege Level | Number |                                 Description                                 |                    Group                    |
| :--------: | :-------------: | :----: | :-------------------------------------------------------------------------: | :-----------------------------------------: |
|  vsstatus  |       VS        | 0x200  |              Virtual Supervisor-mode Processor Status Register              |             virtual supervisor              |
|    vsie    |       VS        | 0x204  |          Virtual Supervisor Mode Interrupt Enable Control Register          |             virtual supervisor              |
|   vstvec   |       VS        | 0x205  |          Virtual supervisor mode trap vector base address register          |             virtual supervisor              |
| vsscratch  |       VS        | 0x240  |         Virtual Supervisor Mode Trap Temporary Data Backup Register         |             virtual supervisor              |
|   vsepc    |       VS        | 0x241  |            Virtual Supervisor Mode Trap Reserved Program Counter            |             virtual supervisor              |
|  vscause   |       VS        | 0x242  |                 Virtual Supervisor Mode Trap Cause Register                 |             virtual supervisor              |
|   vstval   |       VS        | 0x243  |                Virtual Supervisor Mode Trap Vector Register                 |             virtual supervisor              |
|    vsip    |       VS        | 0x244  |           Virtual supervisor mode trap event wait status register           |             virtual supervisor              |
| vstimecmp  |       VS        | 0x24D  |       Virtual supervisor-mode timer interrupt compare value register        |             virtual supervisor              |
| vsiselect  |       VS        | 0x250  |     Virtual supervisor mode indirect register selection signal register     | virtual supervisor indirect access register |
|   vsireg   |       VS        | 0x251  |             Virtual Supervisor Indirect Register Alias Register             | virtual supervisor indirect access register |
|  vstopei   |       VS        | 0x25C  |           Virtual supervisor mode top external interrupt register           |        Virtual supervisor interrupt         |
|   vsatp    |       VS        | 0x280  | Virtual Supervisor Mode Virtual Address Translation and Protection Register |             virtual supervisor              |
|  hstatus   |       HS        | 0x600  |                  Virtual Machine Processor State Register                   |         virtual machine trap setup          |
|  hedeleg   |       HS        | 0x602  |             Virtual machine mode trap demotion control register             |         virtual machine trap setup          |
|  hideleg   |       HS        | 0x603  |         Virtual Machine Mode Interrupt Delegation Control Register          |         virtual machine trap setup          |
|    hie     |       HS        | 0x604  |               Virtual machine-mode interrupt enable register                |         virtual machine trap setup          |
| htimedelta |       HS        | 0x605  |                   Virtual Machine Mode Virtualized Timer                    |            Virtual Machine Timer            |
| hcounteren |       HS        | 0x606  |                Virtual Machine Mode Counter Enable Register                 |         virtual machine trap setup          |
|   hgeie    |       HS        | 0x607  |          Virtual Machine Guest External Interrupt Enable Register           |         virtual machine trap setup          |
|   hvien    |       HS        | 0x608  |           Virtual machine mode virtual interrupt enable register            |         virtual machine trap setup          |
|   hvictl   |       HS        | 0x609  |           Virtual machine mode virtual interrupt control register           |         virtual machine trap setup          |
|  henvcfg   |       HS        | 0x60A  |           Virtual machine mode environment configuration register           |        Virtual machine configuration        |
|   htval    |       HS        | 0x643  |               Virtual machine mode trap event vector register               |        virtual machine trap handling        |
|    hip     |       HS        | 0x644  |            Virtual Machine Mode Trap Event Wait Status Register             |        virtual machine trap handling        |
|    hvip    |       HS        | 0x645  |           Virtual Machine Mode Virtual Interrupt Pending Register           |        virtual machine trap handling        |
|  hviprio1  |       HS        | 0x646  |         Virtual machine mode VS-Level interrupt priority register 1         |        virtual machine trap handling        |
|  hviprio2  |       HS        | 0x647  |         Virtual Machine Mode VS-Level Interrupt Priority Register 2         |        virtual machine trap handling        |
|   htinst   |       HS        | 0x64A  |                  Virtual Machine Trap Instruction Register                  |        virtual machine trap handling        |
|   hgatp    |       HS        | 0x680  |   Virtual Machine Mode Guest Address Translation and Protection Register    | Virtual Machine Protection and Translation  |
|  hcontext  |    HS/Debug     | 0x6A8  |                    Virtual machine mode context register                    |               Debug register                |

### Virtual supervisor mode read-only CSRs

The RISC-V CSRs implemented in {{processor_name}} with virtual supervisor-mode
read-only (HRO) permissions are listed in the table below:

Table: List of HRO CSRs supported by {{processor_name}}

|  Name  | Privilege Level | Number |                          Description                           |               Group                |
| :----: | :-------------: | :----: | :------------------------------------------------------------: | :--------------------------------: |
| hgeip  |       HS        | 0xE12  | Virtual Machine Mode Guest External Interrupt Pending Register |   virtual machine trap handling    |
| vstopi |       VS        | 0xEB0  |          Virtual supervisor mode top-level interrupt           | Virtual supervisor-level interrupt |

### Machine-mode readable/writable CSRs

The RISC-V CSRs implemented in {{processor_name}} with machine-mode read-write
(MRW) permissions are listed in the following table:

Table: List of MRW CSRs Supported by {{processor_name}}

|     Name      | Privilege Level | Number |                            Description                             |                  Group                  |
| :-----------: | :-------------: | :----: | :----------------------------------------------------------------: | :-------------------------------------: |
|    mstatus    |        M        | 0x300  |               Machine mode processor status register               |           Machine Trap Setup            |
|     misa      |        M        | 0x301  |          Machine-mode processor instruction set register           |           Machine Trap Setup            |
|    medeleg    |        M        | 0x302  |           Machine Mode Trap Delegation Control Register            |           Machine Trap Setup            |
|    mideleg    |        M        | 0x303  |         Machine mode interrupt delegation control register         |           Machine Trap Setup            |
|      mie      |        M        | 0x304  |               Machine Mode Interrupt Enable Register               |           Machine Trap Setup            |
|     mtvec     |        M        | 0x305  |           Machine Mode Trap Vector Base Address Register           |           Machine Trap Setup            |
|  mcounteren   |        M        | 0x306  |                Machine mode counter enable register                |           Machine Trap Setup            |
|     mvien     |        M        | 0x308  |           Machine-mode Virtual Interrupt Enable Register           |           Machine Trap Setup            |
|     mvip      |        M        | 0x309  |          Machine-mode Virtual Interrupt Pending Register           |           Machine Trap Setup            |
|    menvcfg    |        M        | 0x30A  |          Machine Mode Environment Configuration Register           |          Machine Configuration          |
|   mstateen0   |        M        | 0x30C  |                Machine Mode Status Enable Register                 |     Machine State Enable Extension      |
| mcountinhibit |        M        | 0x320  |               Machine mode counter inhibit register                |          Machine Counter Setup          |
|  mhpmevent3   |        M        | 0x323  |    Machine Mode Performance Monitoring Event Select Register 3     |          Machine Counter Setup          |
|      ...      |       ...       |  ...   |                                ...                                 |                   ...                   |
|  mhpmevent31  |        M        | 0x33F  |    Machine-mode performance monitoring event select register 31    |          Machine Counter Setup          |
|   mscratch    |        M        | 0x340  |          Machine-mode trap temporary data backup register          |          Machine Trap Handling          |
|     mepc      |        M        | 0x341  |             Machine Mode Trap Reserved Program Counter             |          Machine Trap Handling          |
|    mcause     |        M        | 0x342  |                  Machine-mode trap cause register                  |          Machine Trap Handling          |
|     mtval     |        M        | 0x343  |                 Machine-mode Trap Vector Register                  |          Machine Trap Handling          |
|      mip      |        M        | 0x344  |            Machine mode trap event wait state register             |          Machine Trap Handling          |
|    mtinst     |        M        | 0x34A  |               Machine-mode trap instruction register               |          Machine Trap Handling          |
|    mtval2     |        M        | 0x34B  |                Machine-mode Trap Vector Register 2                 |          Machine Trap Handling          |
|   miselect    |        M        | 0x350  |       Machine Mode Indirect Register Select Signal Register        |    Machine Indirect Access Register     |
|     mireg     |        M        | 0x351  |           Machine-mode indirect register alias register            |    Machine Indirect Access Register     |
|    mtopei     |        M        | 0x35C  |            Machine mode top external interrupt register            |            Machine Interrupt            |
|    pmpcfg0    |        M        | 0x3A0  |        Physical Memory Protection Configuration Register 0         |        Machine Memory Protection        |
|    pmpcfg2    |        M        | 0x3A2  |        Physical Memory Protection Configuration Register 2         |        Machine Memory Protection        |
|      ...      |       ...       |  ...   |                                ...                                 |                   ...                   |
|   pmpcfg14    |        M        | 0x3AE  |        Physical Memory Protection Configuration Register 14        |        Machine Memory Protection        |
|   pmpaddr0    |        M        | 0x3B0  |         Physical Memory Protection Base Address Register 0         |        Machine Memory Protection        |
|      ...      |       ...       |  ...   |                                ...                                 |                   ...                   |
|   pmpaddr63   |        M        | 0x3EF  |        Physical Memory Protection Base Address Register 63         |        Machine Memory Protection        |
|   mnscratch   |        M        | 0x740  | Machine-mode non-maskable interrupt temporary data backup register | Machine Non-Maskable Interrupt Handling |
|     mnepc     |        M        | 0x741  |    Machine-mode non-maskable interrupt reserved program counter    | Machine Non-Maskable Interrupt Handling |
|    mncause    |        M        | 0x742  |         Machine mode non-maskable interrupt cause register         | Machine Non-Maskable Interrupt Handling |
|   mnstatus    |        M        | 0x744  |        Machine mode non-maskable processor status register         | Machine Non-Maskable Interrupt Handling |
|    mseccfg    |        M        | 0x747  |            Machine-mode security configuration register            |          Machine Configuration          |
|    tselect    |     M/Debug     | 0x7A0  |                Debug/Trace Trigger Select Register                 |             Debug register              |
|    tdata1     |     M/Debug     | 0x7A1  |              First Debug/Trace trigger data register               |             Debug register              |
|    tdata2     |     M/Debug     | 0x7A2  |              Second Debug/Trace Trigger Data Register              |             Debug register              |
|    tdata3     |     M/Debug     | 0x7A3  |            The third Debug/Trace Trigger Data Register             |             Debug register              |
|     tinfo     |     M/Debug     | 0x7A4  |              Debug/Trace Trigger Information Register              |             Debug register              |
|   tcontrol    |     M/Debug     | 0x7A2  |                Machine mode trigger enable register                |             Debug register              |
|   mcontext    |     M/Debug     | 0x7A3  |                   Machine-mode context register                    |             Debug register              |
|    pmacfg0    |        M        | 0x7C0  |                    PMA Configuration Register 0                    |            PMA Configuration            |
|    pmacfg2    |        M        | 0x7C2  |                    PMA Configuration Register 2                    |            PMA Configuration            |
|   pmaaddr0    |        M        | 0x7C8  |                       PMA address register 0                       |               PMA Address               |
|      ...      |       ...       |  ...   |                                ...                                 |                   ...                   |
|   pmaaddr15   |        M        | 0x7D7  |                      PMA Address Register 15                       |               PMA Address               |
|    mcycle     |        M        | 0xB00  |                     Machine-mode cycle counter                     |             Machine Counter             |
|   minstret    |        M        | 0xB02  |              Machine Mode Retired Instruction Counter              |             Machine Counter             |
| mhpmcounter3  |        M        | 0xB03  |           Machine Mode Performance Monitoring Counter 3            |             Machine Counter             |
|      ...      |       ...       |  ...   |                                ...                                 |                   ...                   |
| mhpmcounter31 |        M        | 0xB1F  |           Machine-mode performance monitoring counter 31           |             Machine Counter             |

### Machine-mode read-only CSRs

The RISC-V CSRs implemented in {{processor_name}} with machine-mode read-only
(MRO) permissions are listed in the table below:

Table: List of MRO CSRs supported by {{processor_name}}

|    Name    | Privilege Level | Number |                   Description                    |        Group        |
| :--------: | :-------------: | :----: | :----------------------------------------------: | :-----------------: |
| mvendorid  |        M        | 0xF11  |                Vendor ID register                | Machine Information |
|  marchid   |        M        | 0xF12  |             Architecture ID Register             | Machine Information |
|   mimpid   |        M        | 0xF13  | Machine mode hardware implementation ID register | Machine Information |
|  mhartid   |        M        | 0xF14  |    Machine-mode logical core number register     | Machine Information |
| mconfigptr |        M        | 0xF15  |       Configuration Data Structure Pointer       | Machine Information |
|   mtopi    |        M        | 0xFB0  |         Machine mode top-level interrupt         | Machine Trap Setup  |

### Debug-mode readable/writable CSRs

The RISC-V CSRs implemented in {{processor_name}} with debug mode read-write
(DRW) permissions are listed in the following table:

Table: List of DRW CSRs Supported by {{processor_name}}

|   Name    | Privilege Level | Number |              Description               |        Group        |
| :-------: | :-------------: | :----: | :------------------------------------: | :-----------------: |
|   dcsr    |      Debug      | 0x7B0  | Debug mode control and status register | Debug mode register |
|    dpc    |      Debug      | 0x7B1  |       Debug mode program counter       | Debug mode register |
| dscratch0 |      Debug      | 0x7B2  |     Debug-mode Scratch Register 0      | Debug mode register |
| dscratch1 |      Debug      | 0x7B3  |    Debug mode temporary register 1     | Debug mode register |

## Custom CSRs

In the control status register table of the aforementioned implementation, it
can be observed that {{processor_name}} extends the CSRs of RISC-V, implementing
some CSRs not defined in the RISC-V manual. The following will introduce these
CSRs.

### sbpctl

The address of sbpctl is 0x5C0, with its initial value set to the default in the
table below. Each bit's function is described in the following table.

Table: Bit Functions of sbpctl

| Bit  |                            Feature                            | Default value |
| :--: | :-----------------------------------------------------------: | :-----------: |
|  0   |               UBTB_ENABLE set to 1 enables uftb               |       1       |
|  1   |    BTB_ENABLE set to 1 indicates the main FTB is enabled.     |       1       |
|  2   | BIM_ENABLE Set to 1 to enable the bim predictor[^sbpctl-bim]  |       1       |
|  3   |       TAGE_ENABLE set to 1 enables the TAGE predictor.        |       1       |
|  4   |           SC_ENABLE Set to 1 to enable SC predictor           |       1       |
|  5   |           RAS_ENABLE Set to 1 enables RAS predictor           |       1       |
|  6   | LOOP_ENABLE set to 1 enables the loop predictor[^sbpctl-loop] |       1       |
| 7-31 |                             WARL                              |       0       |


[^sbpctl-bim]: The current bim has been removed, this bit has no actual
function.

[^sbpctl-loop]: The current Loop predictor has not yet been merged into the
mainline; this bit has no actual functionality.


### spfctl

The address of spfctl is 0x5C1, with its initial value set to the default values
in the table below. The function of each bit is as follows:

Table: spfctl Bit Functions

|       Bit       |                                                                         Feature                                                                          | Default value |
| :-------------: | :------------------------------------------------------------------------------------------------------------------------------------------------------: | :-----------: |
|        0        |                                     Control switch of the L1 instruction prefetcher: set to 1 to enable prefetching.                                     |       1       |
|        1        | Control switch of the L2 prefetcher, including prefetches from the L1 prefetcher directly sent to L2 cache, V/PBOP, TP: set to 1 to enable prefetching.  |       1       |
|        2        |                           Control switch of the L1 prefetcher, including Stream, Stride, SMS: set to 1 to enable prefetching.                            |       1       |
|        3        |            Controls whether the SMS prefetcher accepts training on hits: set to 1 to train on hits as well, set to 0 to train only on misses.            |       0       |
|        4        |                         Control switch of the SMS prefetcher's agt table prefetching: set to 1 to enable agt table prefetching.                          |       1       |
|        5        |                         Control switch of the SMS prefetcher's pht table prefetching: set to 1 to enable pht table prefetching.                          |       1       |
|       6-9       |                                  Controls the prefetch activation threshold for the active page of the SMS prefetcher.                                   |      12       |
|      10-15      |                                         Controls the prefetch stride for the active page of the SMS prefetcher.                                          |      30       |
|       16        |                         Control switch for Stream and Stride in the L1 prefetcher: set to 1 to enable the respective prefetcher.                         |       1       |
|       17        |                           Controls whether the L2 prefetcher only trains on received store L1 miss requests: set to 1 for yes.                           |       0       |
|       18        |         Control switch for prefetches from the L1 prefetcher directly sent to L2 cache in the L2 prefetcher: set to 1 to enable such prefetches.         |       1       |
|       19        |                                    Control switch for PBOP in the L2 prefetcher: set to 1 to enable this prefetcher.                                     |       1       |
|       20        |                                      Switch to control VBOP in the L2 prefetcher: set to 1 to enable this prefetch                                       |       1       |
|       21        |                                       Switch to control TP in the L2 prefetcher: set to 1 to enable this prefetch                                        |       1       |
|      22-31      | Delay for deferred request updates of V/PBOP in the L2 prefetcher: set to 0 to use the system default (currently 300), set to non-zero to use this delay |       0       |
| High-order bits |                                                                      Reserved bits                                                                       |       0       |

### slvpredctl

The address of slvpredctl is 0x5C2, with its initial value set to the default
values in the table below, and the function of each bit is as shown in the
following table

Table: Bit functions of slvpredctl

|    Bit     |                                                             Feature                                                              | Default value |
| :--------: | :------------------------------------------------------------------------------------------------------------------------------: | :-----------: |
|     0      |                     Controls whether the memory access violation predictor is disabled. Set to 1 to disable.                     |       0       |
|     1      | Controls whether the memory violation predictor prohibits speculative execution of load instructions. Setting to 1 prohibits it. |       0       |
|     2      |           Controls whether the memory access violation predictor blocks store instructions, where 1 indicates blocking           |       0       |
|    4-8     |           Memory access violation predictor reset interval. If the value of this field is x, the interval is 2^(10+x)            |       6       |
| Other bits |                                              Other bits currently have no function                                               |       0       |

### smblockctl

The address of smblockctl is 0x5C3, with its initial value set to the default
values in the table below. Each bit's function is as shown in the following
table.

Table: Bit functions of smblockctl

|    Bit     |                                            Feature                                            | Default value |
| :--------: | :-------------------------------------------------------------------------------------------: | :-----------: |
|    0-3     |                          Controls the flush threshold of the sbuffer                          |       7       |
|     4      |         Controls whether to enable ld-ld violation checking, setting 1 means enabled          |       1       |
|     5      |              Controls whether soft prefetch is enabled. Setting to 1 enables it.              |       1       |
|     6      | Controls whether to report ECC errors occurring in the cache. Setting to 1 enables reporting. |       1       |
|     7      |       Controls whether uncache outstanding accesses are supported. Set to 1 to enable.        |       0       |
| Other bits |                             Other bits currently have no function                             |       0       |

### srnctl

The address of srnctl is 0x5C4, with its initial value set to the default values
in the table below. The functionality of each bit is as described in the
following table.

Table: Bit Functions of srnctl

|    Bit     |                       Feature                        | Default value |
| :--------: | :--------------------------------------------------: | :-----------: |
|     0      | Whether the fusion decoder is enabled, 1 for enabled |       1       |
|     1      |  Whether speculative virtual address inv is enabled  |       1       |
|     2      |        Whether the wfi instruction is enabled        |       1       |
| Other bits |        Other bits currently have no function         |       0       |
