# Differential Verification {#sec:debug-difftest}

Differential verification compares XSAI execution against a reference model
instruction by instruction and is the main guarantee of functional correctness for
the matrix extension. This chapter covers what the reference models can and cannot
judge, and how to use them when something goes wrong.

## Reference models

| Reference model | Role |
| --- | --- |
| CPU reference model | the default path |
| GPU reference model | used alongside the CPU path, to rule out implementation differences on the reference side |

Comparison for matrix instructions supports batching, backpressure and ordering
checks.

The reference model treats the following as errors rather than passing them
silently: reading matrix register regions that were never written, missing
`mfence`, and out-of-bounds access before `macquire`.

## How matrix registers are compared

The early implementation transferred every matrix register element and compared
them, which cost a lot of communication. There are now two modes:

| Instruction type | Comparison | Why |
| --- | --- | --- |
| operations with a unique result (`mzero`, arithmetic) | each side hashes, then the hashes are compared | low communication; identical inputs always give identical hashes |
| multiply-type instructions with tolerance (`mma`) | element-by-element | the result is not unique, so hashing does not apply |

## How to use it

1. Differential checking is on by default (`DIFF` defaults to 1 for `make run-emu`).
2. On a mismatch, first run once with `DIFF=0` to separate a problem in the difftest
   interface from one in the RTL or the reference model.
3. The reference model and the DUT must use the **same configuration**; different
   configurations produce systematic false positives.

For the symptoms matrix failures usually present, see
[Troubleshooting](troubleshooting.md#sec:debug-troubleshooting).
