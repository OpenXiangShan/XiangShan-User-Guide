# VCS Simulation and Test Suites {#sec:sim-vcs}

VCS covers module-level and system-level verification of the matrix unit and the
L2, coverage collection, and cross-checking against Verilator. This chapter covers
what each suite verifies, how to run them, and how they work with Verilator.

## Test suites

| Suite | Verifies | Notes |
| --- | --- | --- |
| CUTE-Test | matrix unit | compares step by step against the NEMU reference model; built and run inside the CUTE project, not through the top-level `make test` (that one is an environment self-check) |
| CUTE-CTRL | control path | test cases and a debug entry point |
| TestTopWithL2 | matrix unit + L2 | storage side switched to a coherent interface (no snoop subset), with a purpose-built SN-side functional model plus transaction legality and timeout checks |
| CUTE-UVM | matrix unit | UVM layered environment organised as core compute, dataflow control, memory load and register file |

## Cross-checking against Verilator

Run the same set of tests on both Verilator and VCS, then compare the **pass/fail
sets** and the **timeout signatures**. Only when the two agree item by item can you
attribute a failure to the design rather than to a simulator difference.

## Running

Get Verilator working first with ChiselDB and DRAMsim3 disabled, then move to VCS:

```bash
make -C XSAI emu -j8 CONFIG=DefaultMatrixConfig \
  WITH_DRAMSIM3=0 WITH_CHISELDB=0 WITH_CONSTANTIN=0 \
  EMU_THREADS=8 EMU_TRACE=fst
```

## Coverage

Use Verilator line and branch coverage as the daily baseline. When coverage falls
short, first separate two causes: a hung test case meant the downstream paths never
ran, or there is a genuine coverage hole. The former means fixing the test case
first.

VCS is used for supplementary confirmation and for timing-related checks.
