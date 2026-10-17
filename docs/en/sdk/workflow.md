# Workflow and Contribution {#sec:sdk-workflow}

This repository uses an issue-first, branch-per-change workflow: changes stay small enough to review and are validated on the narrowest path that can prove the behaviour. This chapter is for people filing issues or pull requests, and for people changing several places in the same repository at once. See [Build System and make Targets](build.md#sec:sdk-build) for build and run entry points, and [Submodules and Version Management](submodules.md#sec:sdk-submodules) for submodule and version records.

## Starting from an issue

| Case | Template to use |
| --- | --- |
| Bug | bug report template, after checking [Troubleshooting](../verification/troubleshooting.md#sec:debug-troubleshooting) |
| Failure with an unclear cause | problem report template, until the root cause is clear |
| New behaviour or workflow change | feature request template |
| Question | question template |

Terminal-first flow:

```bash
bash scripts/bug-report.sh
bash scripts/create-issue.sh --type bug --title "..."
bash scripts/create-issue.sh --type feature --title "..."
```

An issue title is a human-readable summary and carries the template prefix (`[Bug Report] ...`, `[Feature Request] ...`, `[Problem] ...`); Conventional Commit style such as `fix(qemu): ...` or `docs(checkpoint): ...` is reserved for commits and pull request titles. **When the root cause belongs to an upstream component repository (`XSAI`, `NEMU`, `qemu`, `riscv-rootfs`), raise or link an issue there**, and keep the `xsai-env` issue focused on the integration context.

## Branch naming

```bash
git switch master
git pull --ff-only
git switch -c fix/123-checkpoint-replay
```

| Prefix | Use |
| --- | --- |
| `fix/<issue>-short-topic` | bug fix |
| `feat/<issue>-short-topic` | new behaviour |
| `docs/<issue>-short-topic` | documentation only |
| `test/<issue>-short-topic` | tests only |
| `refactor/<issue>-short-topic` | structure changes that preserve behaviour |
| `chore/<issue>-short-topic` | maintenance |
| `ci/<issue>-short-topic` | CI changes |
| `bump/<component>-<rev-or-topic>` | submodule or version bump |
| `wip/<topic>` | temporary private work only; rename before opening a pull request |

A branch has one primary write scope. When a change spans a high-risk contract (Matrix ISA semantics, difftest, memory map, checkpoint format, rootfs boot flow), **split it into serial pull requests unless the interface change itself needs coordinated patches**.

## Commits and pull requests

Commit subjects follow Conventional Commits:

```text
fix(checkpoint): respect Makefile SimPoint defaults
feat(rootfs): add llama bench model preset
docs(workflow): document branch and PR flow
chore(submodule): bump NEMU to a587e09
```

Keep every commit reviewable and buildable; separate mechanical reformatting from behaviour changes; reference the issue ID in the body when useful (`Fixes #123`, `Refs #123`). **Do not commit generated artefacts under `local/`, `build/`, `log/` or `firmware/checkpoints/`**. A submodule bump states the old and the new revision and the reason.

Pull requests target `master`. The description carries the linked issue (`Fixes #123` / `Refs #123`), a summary of user-visible or workflow-visible changes, the main workstream and the paths touched, the validation commands that were run (or why they were not), risks and review focus in coupled areas, and links to upstream issues or pull requests when the root cause spans repositories. Keep unfinished work in draft; mark it ready only after rebasing or merging onto current `master` with validation passing, or with the remaining gaps stated explicitly. Before merging, confirm the branch is in sync with `master` and that CI either passes or its failures are understood and recorded; prefer squash or rebase merges to keep `master` linear. Reviewers of a submodule bump confirm that the target commit can be fetched from the submodule remote and that validation from the root covers integration behaviour.

## Submodule changes

A submodule change produces two different commits: the real code commit in the submodule repository, and the gitlink bump commit in `xsai-env`; the outer repository can only point at a submodule commit that exists in a reachable remote. Nested submodules are committed from the inside out: for `XSAI/CUTE` that is `XSAI/CUTE` → `XSAI` → `xsai-env`, and every layer points at a revision that is committed, pushed and reviewable in the layer below. See [Submodules and Version Management](submodules.md#sec:sdk-submodules) for the full sequence, the timing of `make versions` and what the root bump pull request has to record.

## Debugging and support

Frequent problems:

| Problem | Log or symptom | Cause | Handling |
| --- | --- | --- | --- |
| Kernel panic: No working init found | `Failed to execute /init (error -2)` followed by `Kernel panic - not syncing: No working init found.` | the initramfs contains `/init`, but the loader path that busybox points at is missing from the image | `make firmware`, then `make run-qemu`; if this follows an environment switch, run `make -C firmware/riscv-rootfs clean` first and rebuild |
| Linux boots extremely slowly under RTL | OpenSBI and early Linux messages appear normally, and later boot messages take minutes to hours | the ratio between `mtime` and the device tree `timebase-frequency` is wrong | see the timebase scale below |

### timebase scale

The number of RTL cycles per guest second equals the `RTC clock divider` times the `timebase-frequency`, and XSAI simulation hardware divides the RTL clock by 100 by default. A DTB declaring 10 MHz therefore needs `1,000,000,000` RTL cycles for one guest second; to estimate host time, divide that cycle count by the simulation rate you actually measure on your own backend. The bundled XSAI Linux image and the DTS generated by XSAI use 1 MHz, while the QEMU `nemu` machine uses 10 MHz, so **a DTB cannot be carried between QEMU and RTL without rechecking this value**. Enabling the RTC driver or CPUFreq does not fix a wrong `mtime` scale.

```bash
fdtget firmware/nemu_board/dts/build/xiangshan_ai.dtb /cpus timebase-frequency
grep -E 'CONFIG_(HZ|NO_HZ|RISCV_TIMER|CPU_FREQ|RTC_CLASS)' firmware/riscv-linux/.config

make -C firmware build-dtb-xsai XSAI_TIMEBASE_FREQ=10000000
make run-qemu

make -C firmware build-dtb-xsai XSAI_TIMEBASE_FREQ=1000000
make -C firmware build-gcpt-nemu
make xsai XSAI_SIM_RTC_CLOCK_DIV=100
make run-emu PAYLOAD=firmware/gcpt_restore/build-nemu/build/gcpt.bin
```

The boot log must report the same timebase, for example `Platform Timer Device : aclint-mtimer @ 1000000Hz` and `sched_clock: 64 bits at 1MHz`. Rebuild the NEMU/RTL payload after changing the DTB, because the payload embeds the DTB; use a separate simulation build directory per divider, the fast-RTC profile being `XSAI_SIM_BUILD_DIR=build-fast-rtc XSAI_SIM_RTC_CLOCK_DIV=2`. The fast-RTC profile suits software boot and debugging and is **not suitable for wall-clock or timer-latency measurements**; architectural performance results use `cycle`, `instret` and the default divider.

### Reporting and notifications

`bash scripts/bug-report.sh` produces the environment and repository information bundle for a bug report (options `--basic`, `--build-cmd <cmd>`, `--run-cmd <cmd>`, `--note <text>`; the output is the `${ROOT}/bug-report` directory and `bug-report.tar.gz`). `bash scripts/create-issue.sh` is the terminal-first issue workflow built on the GitHub CLI, defaults to the `OpenXiangShan/xsai-env` repository, and reports `GitHub CLI is not authenticated. Run 'gh auth login' first.` when it is not authenticated.

## Workflow boundaries and parallel work

Five operating principles:

1. A task has exactly one primary write scope.
2. Cross-subsystem changes are allowed when the interface itself is what changes.
3. If A changes a contract of B, change A first and integrate B in a second step, rather than letting unrelated agents edit both sides at once.
4. Prefer the root `Makefile` and the shared environment entry points.
5. Tests and tools should validate or automate a flow, and **should not quietly become the only source of truth for a subsystem contract**.

See [SDK Layout and Directory Structure](layout.md#sec:sdk-layout) for the main paths, ownership and typical entry points of each workstream.

**Safe to parallelise**:

* Documentation-only tasks under `docs/`, `README.md`, `AGENTS.md` and `.agents/skills/`.
* Self-contained changes inside a single `firmware/riscv-rootfs/apps/<app>/`, `nexus-am/apps/<app>/` or `nexus-am/tests/<test>/`, without touching the shared rootfs manifest, init scripts, common runtime or ISA contracts.
* Independent helpers under `tools/` or `scripts/` that do not change component contracts.

**Must be serialised** (unless there is a very clear split of write ownership):

* Matrix ISA semantics, CSR behaviour, instruction encoding or ABI expectations.
* difftest/reference-model alignment between `NEMU/` and `XSAI/`.
* Memory map, DTB, reserved-memory or DMA window changes.
* Checkpoint format, restore behaviour, or profile/cluster/dump orchestration.
* Shared runtime or library changes in `nexus-am/` that fan out to many apps and tests.
* Top-level environment and build entry changes under `Makefile`, `scripts/`, `env.sh` and `.envrc*`.

High-risk coupled areas and how to treat them:

| Area | Files involved | Advice |
| --- | --- | --- |
| Matrix ISA, intrinsic, CSR or ABI changes | `llvm-project-ame/`, `DSL/`, `nexus-am/`, `NEMU/`, `qemu/`, `XSAI/` | Land the source-of-truth change first, then update consumers one by one, with explicit validation at each layer |
| difftest alignment | `NEMU/` and `XSAI/` | Change the side that owns the contract first, then integrate the other |
| Memory-map and DTB changes | `mk/`, firmware board files, Linux config assumptions, rootfs apps such as `hello_xsai` | Treat them as a firmware/platform contract change |
| Checkpoint flow changes | `scripts/checkpoint.sh`, `Makefile`, `qemu/`, `firmware/gcpt_restore/`, `NEMU/resource/simpoint/` | Keep a single integration owner; failures usually only show end to end |
| Rootfs boot flow changes | app code, `firmware/riscv-rootfs/Makefile`, initramfs manifests, init scripts | Treat build, packaging and boot invocation as one change |

High-risk coupled changes require at least one reviewer familiar with the owning subsystem. Routing order: identify the primary workstream, list the most likely source-of-truth paths, mark the downstream consumers (they may need validation but should not be edited now); when several sources of truth must change, split the work into serial stages, prefer the smallest local edit, and validate on the narrowest path that can prove the change; when ownership is unclear, start from the subsystem that defines the interface.
