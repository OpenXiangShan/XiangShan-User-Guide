---
file_authors_:
- zehao Liu <liuzehao19@mails.ucas.ac.cn>
---

# Critical Error {#sec:critical-error}

## Overview

{{processor_name}} supports the RISC-V double trap series extensions, including
ssdbltrp and smdbltrp extensions, to handle system-level unrecoverable errors,
i.e., critical errors: where the processor enters a state that cannot be
repaired through conventional exception handling processes.

The RISC-V Privileged Specification defines a critical error as a new exception
or interrupt occurring during an exception handler (non-reentrant phase), known
as a double trap. Such nested traps may result in:

* Context register content lost or overwritten
* Conventional exception return paths are no longer reliable
* Unable to restore the execution context of the initial exception

Therefore, the RISC-V Privileged Specification introduces the double trap
extension, additionally defining critical error exception handlers to manage
certain recoverable critical errors.

## Recoverable critical errors

The double trap extension defines double traps occurring in supervisor mode
(HS/S), virtual supervisor mode (VS), and certain machine mode (M) scenarios as
recoverable critical errors.

### (Virtual) Supervisor mode recoverable critical error

Response flow for (virtual) supervisor-mode recoverable critical errors:

First step, determine whether a double trap occurred in (virtual) supervisor
mode based on the SDT bit in the vs/sstatus register;

Step two: If a double trap occurs, delegate the handling of the second trap to a
higher privilege level (machine mode) to protect the current privilege level and
existing privilege registers, context registers, and other information;

Step three: Machine mode handles the second trap:

* Mark mcause as 16 (double trap);
* Mark mtval2 as the second trap type;

Fourth step, jump to the double trap handler pre-configured by system software
based on mtvec to handle the second trap.

Return process for recoverable critical errors in (virtual) supervisor mode:

Machine mode uses the mret instruction to return to the first trapped exception
handler and privilege level, clears the SDT bit in the corresponding vs/sstatus
to mark the completion of the second trap handling, and finally proceeds to
complete the subsequent first trap handling.

### Machine-mode recoverable critical errors

Since {{processor_name}} supports the RISC-V recoverable non-maskable interrupt
extension, namely the smrnmi extension, it enables recovery from critical errors
in machine mode.

Response flow for machine-mode recoverable critical errors:

First step, determine whether a double trap occurred in machine mode based on
the MDT bit in the mstatus register;

Step two: If a double trap occurs, check whether a higher privilege level exists
to handle the second trap:

* If the mnstatus.nmie bit in the non-maskable interrupt status register is set,
  it indicates that recoverable non-maskable interrupt handling is currently
  supported and can be delegated;
* If the nmie bit is cleared, it indicates that recoverable non-maskable
  interrupt handling is not currently supported or is in progress, and
  delegation is not possible;

Step three: Non-maskable interrupt handling for the second trap.

Return process for recoverable critical errors in machine mode:

Machine mode uses the mnret instruction to return to the first trapped exception
handler and privilege level, clears the MDT bit in the corresponding mstatus to
mark the completion of the second trap handling, and finally proceeds to
complete the subsequent first trap handling.

## Unrecoverable critical error (critical error state)

The double trap extension defines the following critical errors as
non-recoverable critical errors:

* When recoverable non-maskable interrupt handling is not supported, a critical
  error occurs in machine mode
* When a recoverable non-maskable interrupt is being processed, a critical error
  occurs in machine mode.

Simply put, the above scenarios all involve traps occurring when mnstatus.nmie
is pulled low. At this point, there is no higher privilege level available for
delegation, making it impossible to handle the critical error. The double trap
extension defines this state as a critical error state: even after supporting
double trap behavior, the processor core cannot handle the current state,
leading to unknown subsequent behavior that requires external platform
intervention.

Additionally, the current {{processor_name}} defines processor core hang as a
critical error state, serving as an important means for post-silicon hang
determination.

### Critical error state handling

After collecting information about a non-recoverable critical error, the
processor enters a critical error state, which is a special halt state. The
RISC-V manual specifies that this state must be observable and debuggable by the
external platform:

- The processor core provides a top-level interface riscv_critical_error for
  external platform monitoring;
- Depending on the dcsr.cetrig field in the debug mode configuration register,
  optionally enter debug mode handling during a critical error state;
    - cetrig = 1: Does not externally signal a critical error, enters debug mode
      for handling, and configures the entry reason as a critical error state:
      dcsr.cause = 7, dcsr.extcause = 0;
    - cetrig = 0: Deliver a critical error signal, allowing the external
      platform to perform a reset or other error reporting/fault tolerance
      mechanisms.
