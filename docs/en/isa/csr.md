# Matrix CSRs {#sec:xsai-csr}

This chapter lists only the CSRs that XSAI adds over, or changes the semantics of
relative to, Kunminghu V2R2. Read [Data Registers](registers.md#sec:xsai-registers)
and [Instruction Set Extensions](instruction-set.md#sec:xsai-instruction-set)
first.

## Matrix-related CSRs

The Kunminghu V2R2 baseline has no systematic definition of matrix state, matrix
tile state or matrix dirty state. XSAI adds a group of matrix CSRs and
architectural state.

**The RTL and QEMU currently disagree on these addresses**, so confirm which side
you are targeting before reading them:

| CSR (assembly-visible name) | RTL address | QEMU address | Kind | Meaning |
| --- | --- | --- | --- | --- |
| `mcsr` | `0x802` | `0x802` | read-write | matrix control state |
| `mxrm` | `0x806` | `0x806` | read-write | matrix rounding mode |
| `msat` | `0x807` | `0x807` | read-write | matrix saturation flag |
| `mfflags` | `0x808` | `0x808` | read-write | matrix floating-point flags |
| `mfrm` | `0x809` | `0x809` | read-write | matrix floating-point rounding mode |
| `msaten` | `0x80A` | — | read-write | matrix state enable |
| `xmisa` | **does not exist** | `0xcc0` | read-only constant | matrix ISA capability description |
| `tlenb` | `0xcc1` | `0xcc1` | read-only constant | tile register length in bytes, the `TLEN / 8` |
| `trlenb` | `0xcc2` | `0xcc2` | read-only constant | tile row width in bytes, the `TRLEN / 8` |
| `alenb` | `0xcc3` | `0xcc3` | read-only constant | accumulator length in bytes, the `ALEN / 8` |
| `mtilem` | **`0xcc4`** | `0xcc5` | read-write | current M-dimension tile shape |
| `mtilen` | **`0xcc5`** | `0xcc6` | read-write | current N-dimension tile shape |
| `mtilek` | **`0xcc6`** | `0xcc7` | read-write | current K-dimension tile shape |
| `msync` | **`0xcc7`** | undefined | read-only | sync register count |

**Three differences matter**:

1. **there are two naming schemes**: the RTL symbols carry no `x` prefix (`mxrm`,
   `msat`, `mfflags`, `mfrm`, `msaten`, `tlenb`, ...), while the specification
   documents and the QEMU macros use one (`xmxrm`, `CSR_XTLENB`, ...). They denote
   the same CSRs, so pick one convention for documents and code.
2. `mtilem` / `mtilen` / `mtilek` are `0xcc4` – `0xcc6` in the RTL but `0xcc5` –
   `0xcc7` in QEMU, **shifted by one**; moreover `0xcc7` is `msync` in the RTL and
   `mtilek` in QEMU, so **the same address means different things on the two
   sides**.
3. `xmisa` (`0xcc0`) exists only in QEMU; the RTL has no `0xcc0` and its matrix
   CSRs start at `0xcc1`.

Do not assume the RTL and QEMU behave identically for these CSRs; cases involving
`mtile*`, `msync` or the name prefix must be verified on both sides.

The firmware probe shows the usage — it reads the first three length CSRs by raw
address:

```c
__asm__ volatile("csrr %0, 0xcc1" : "=r"(tlenb));   /* tlenb  */
__asm__ volatile("csrr %0, 0xcc2" : "=r"(trlenb));  /* trlenb */
__asm__ volatile("csrr %0, 0xcc3" : "=r"(alenb));   /* alenb  */
```

### Access permissions

The matrix CSRs fall into two custom address ranges:

| Range | Name | Kind |
| --- | --- | --- |
| `[0x800, 0x8ff]` | XMCSR | unprivileged custom CSR (read-write), such as `mcsr`, `mxrm`, `msat` |
| `[0xcc0, 0xcff]` | XMINFO | unprivileged custom CSR (read-only), such as `xmisa`, `tlenb`, `mtile*` |

**Do not infer the privilege level from the `m` prefix**: although `mcsr`, `mxrm`
and `msat` start with `m`, they still sit in the unprivileged custom range, so
accessibility below M mode is governed by state enables such as `mstateen0.C`
rather than being unconditionally forbidden "because it is an M-mode CSR".

## Reading the tile shape {#sec:matrix-probe}

Before enabling the matrix path, software should read the current hart's native
tile shape through the CSRs and generate kernels from what it reads: **the shape
parameters in the configuration registers are only guaranteed correct within the
native shape**, and the probe is the only source.

From the three length CSRs, the row count follows as `rows = tlenb / trlenb`, which
is the limit on M and N. The native shape is M128 × N128 × K64, but **do not
hard-code that number and do not assume every hart matches** — the three length
CSRs are the only reliable source, and a wrong shape raises no error, it just
computes wrong results. For the expected values and how to use the tile parameters
see [Data Registers](registers.md#sec:xsai-registers).

## Precision capability description

Matrix precision capability is not expressed in a CSR bitmap; the device tree
describes the input / output type combinations using `riscv,isa-extensions` entries
together with the `xmisa` CSR. The two matrix entries are:

| String | Meaning |
| --- | --- |
| `zame` | Attached Matrix Extension |
| `zammai8i32` | i8 × i8 → i32 matrix multiply-accumulate |

Firmware appends extension names to the device tree through
`XSAI_EXTRA_ISA_EXTENSIONS`:

```make
XSAI_EXTRA_ISA_EXTENSIONS ?= zame zammai8i32
```

The full `riscv,isa-extensions` string is in
[System Software and Runtime](../software/system.md#sec:sw-system).

### Parsing example

Multi-letter extensions occupy no `misa` bit; they are reported as a list of
lowercase extension-name strings, so discovery is a string match over the
NUL-separated list:

```c
/* the device-tree property is given as a NUL-separated string sequence */
static bool dt_has_extension(const char *list, size_t len, const char *want)
{
    for (const char *p = list; p < list + len; p += strlen(p) + 1) {
        if (strcmp(p, want) == 0)
            return true;
    }
    return false;
}

/* usage */
if (!dt_has_extension(isa_ext, isa_ext_len, "zame"))
    return -ENODEV;                 /* no matrix extension: disable the whole path */
```

**Do not use `RISCV_ISA_EXT_SUPM` (`CONFIG_RISCV_ISA_SUPM`) to detect matrix
capability**: it denotes the userspace pointer-masking extension (`SMNPM` / `SSNPM`)
and has nothing to do with the matrix extension; using it as a gate enables the
matrix path on machines that only have pointer masking. Judge matrix capability
from the [shape probe](#sec:matrix-probe) CSR reads instead.

**The capability string and the tile shape are two different things**: the string
says only that the matrix extension exists, while the native shape must still be
read from the length CSRs.

## Extension enablement and state

`mstatus`, `sstatus` and `vsstatus` gain an **`MS` state field** expressing matrix
state. `MS` is folded into the `SD` dirty-state aggregation alongside the existing
floating-point and vector state, and hence into architectural dirty-state
management. The encoding of `MS` and the first-use trap behaviour are in
[Exceptions and Interrupts](exception.md#sec:xsai-exception).

### Save and restore

Matrix architectural state and how to save it:

| State | How to save it |
| --- | --- |
| `tr0` – `tr3`, `acc0` – `acc3` | whole-register transfer (`msa.whole` / `mla.whole`), which moves the full register without interpreting the element type |
| `mcfg0` – `mcfg7` | read and written with `msetcfg` / `mgetcfg`; the raw value has to be rebuilt on restore |
| `mcsr` and the remaining configuration bits (`mxrm`, `msat`, `mfflags`, `mfrm`, `msaten`) | ordinary CSR reads and writes |
| `mstatus.MS` | saved with `mstatus`; when `MS` is `Off` the matrix register contents are discardable, so a full save is unnecessary |

**What the kernel actually does is not save them**: it sets `MS` to `Off` when a
task is switched out and relies on the first-use trap to re-enable on next use,
avoiding the cost of saving the matrix register file. See
[System Software and Runtime](../software/system.md#sec:sw-system).

## Interface to the operating system and firmware

| Stage | Convention |
| --- | --- |
| Capability reporting | the device tree's `riscv,isa-extensions` is generated from `XSAI_EXTRA_ISA_EXTENSIONS` and **must match the actual RTL configuration** |
| Custom CSR enablement | OpenSBI sets `mstateen0.C` / `sstateen0.C`; otherwise access to the matrix CSRs below M mode is rejected |
| Kernel patches | applied by `firmware/patches/apply-matrix-patch.sh`; `0001` provides the matrix first-use trap |
| Checkpoint restore | the `gcpt_restore` restore list contains **no matrix CSR**; only the `mstatus.MS` bit is restored along with `mstatus` |

Operating-system-side notes:

* matrix state is managed isomorphically to vector state, using the first-use trap
  to avoid saving it; the kernel only maintains the `MS` bit at the CSR level;
* the kernel's range check for matrix CSRs includes `0xcc0`, but the current RTL
  has no such CSR (see the address differences above); trust the actual hart
  behaviour.
