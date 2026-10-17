# Verilator Simulation {#sec:sim-verilator}

Verilator is the RTL simulation path used for functional re-verification before committing. This chapter gives the three-stage flow, the build steps and the pass criteria.

## Simulation flow

Verilator simulation for XSAI always follows this flow:

1. `make xsai` builds the emulator `XSAI/build/emu`;
2. `make run-emu` / `make run-emu-debug` act as top-level entry points;
3. `scripts/run-emu.sh` translates top-level variables into `build/emu`
   arguments and loads the payload;
4. pass/fail is decided from console output, logs, waveforms, ChiselDB and
   difftest results.

## Build

```bash
make xsai
```

The top-level wrapper expands to:

```plain
$(MAKE) -C XSAI emu -j<host cpus> \
  CONFIG=DefaultMatrixConfig LLC=ZhuJiang \
  WITH_DRAMSIM3=0 WITH_CHISELDB=1 WITH_CONSTANTIN=0 \
  EMU_THREADS=8 EMU_TRACE=fst OPT_FAST=-O3 ...
```

| Variable | Default | Meaning |
| --- | --- | --- |
| `XSAI_SIM_CONFIG` | `DefaultMatrixConfig` | Matrix configuration (not the minimal one) |
| `XSAI_SIM_LLC` | `ZhuJiang` | Last-level cache configuration |
| `XSAI_SIM_WITH_DRAMSIM3` | `0` | DRAMsim3 memory model off by default; enabling it also requires `DRAMSIM3_HOME` |
| `XSAI_SIM_WITH_CHISELDB` | `1` | Enable ChiselDB support at compile time |
| `XSAI_SIM_BUILD_JOBS` | host CPU count | Build parallelism |
| `EMU_THREADS` | `8` | Number of Verilator threads |
| `EMU_TRACE` | `fst` | **Compile-time** FST support; required for runtime wave dumping |
| `XSAI_SIM_RTC_CLOCK_DIV` | `100` | RTC divider; affects guest time and simulation duration (see [Troubleshooting](troubleshooting.md#sec:debug-troubleshooting)) |

All of them can be overridden on the command line, for example
`make xsai XSAI_SIM_BUILD_DIR=build-fast`.

How the three lower-level targets relate:

| Target | Artifact | Notes |
| --- | --- | --- |
| `make verilog` | `build/rtl/XSTop.sv` | Synthesis top (`top.TopMain`) |
| `make sim-verilog` | `build/rtl/SimTop.sv` | Simulation-only top (`top.XiangShanSim`) |
| `make emu` | `build/emu` | Verilator emulator built on `sim-verilog` |

So `make xsai` uses the **simulation RTL** (`SimTop.sv`), not the synthesis RTL.

## Entry points

| Entry | Behaviour |
| --- | --- |
| `make run-emu` | Ensures `build/emu`; `DIFF` defaults to `1` (difftest on) and `LOG` to `0` (no timestamped log) |
| `make run-emu-debug` | Forces `--log` and `--db`; accepts `WARMUP`, `MAX_INSTR`, `WAVE_BEGIN/END`, `FORK` |

Script-layer defaults (`scripts/run-emu.sh`):

* emulator at `XSAI/build/emu` (change `XSAI_SIM_BUILD_DIR` to relocate);
* reference model at `XSAI/ready-to-run/riscv64-nemu-interpreter-so` (override with `--diff-so`);
* process stack raised to 64 MiB (`EMU_STACK_KB=65536`);
* payload is mandatory.

## Three kinds of payload

| Kind | Path | Use |
| --- | --- | --- |
| Bare-metal images | `XSAI/ready-to-run/*.bin` | First choice for minimal validation |
| GCPT boot image | `firmware/gcpt_restore/build-*/build/gcpt.bin` | Full boot flow |
| Checkpoint slices | `firmware/checkpoints/**/*.zstd` | Slicing and performance study |

## Minimal validation

Principles: simple input, shortest failure path, fast pass/fail, and an upgrade
path to a debug run with artifacts. Recommended order:
`coremark-2-iteration.bin` → `microbench.bin` → `linux.bin` → `gcpt.bin` → checkpoints.

```bash
# Tier 1: minimal bare-metal workload (recommended entry)
make run-emu PAYLOAD=XSAI/ready-to-run/coremark-2-iteration.bin DIFF=1

# Tier 2: keep logs and DB
make run-emu-debug PAYLOAD=XSAI/ready-to-run/coremark-2-iteration.bin DIFF=1

# Tier 3: minimal Linux-level simulation
make run-emu PAYLOAD=XSAI/ready-to-run/linux.bin DIFF=1
```

Do not rely on the default `PAYLOAD` (which is `gcpt.bin` and pulls in the
firmware build chain).

## Diff control

| Value | Effect | Use |
| --- | --- | --- |
| `DIFF=1` (default) | Passes `--diff`; step-by-step comparison against the reference | Standard path |
| `DIFF=0` | Passes `--no-diff` | Isolate problems caused by the diff interface itself |

Two-step practice: run `DIFF=1` first; if it fails and the reference model is
suspected, re-run with `DIFF=0`.

## Pass/fail criteria

| Output | State | Verdict |
| --- | --- | --- |
| `HIT GOOD TRAP` | `STATE_GOODTRAP` | Pass |
| `EXIT at pc = ...` | `STATE_SIM_EXIT` | Usually pass |
| `EXCEEDING CYCLE/INSTR LIMIT` | `STATE_LIMIT_EXCEEDED` | Acceptable for windowed runs |
| `ABORT at pc = ...` | `STATE_ABORT` | Fail |
| `HIT BAD TRAP` | — | Fail |

Also verify: payload recognition (`The image is ...`, `Zstd file detected`, ...),
reference model attachment, absence of mismatches or
`No difftest check for more than ... cycles, maybe get stuck.`, and the final
`instrCnt` / `cycleCnt` / `IPC` statistics.

## Debug artifacts and waveforms

`run-emu-debug` writes `log/<prog>_<timestamp>.log`, `...err.log` and `.db` (ChiselDB).

```bash
make run-emu-debug PAYLOAD=<payload> DIFF=1 WAVE_BEGIN=<b> WAVE_END=<e>
```

Waveforms go to `log/<prog>_<timestamp>.fst`, and **compile-time `EMU_TRACE`** is
required for runtime dumping to work.
