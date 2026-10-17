# VCS 仿真与用例框架 {#sec:sim-vcs}

VCS 用于矩阵单元与 L2 的模块级和系统级验证、覆盖率收集，以及与 Verilator 的交叉确认。这一章说明各用例集的职责、怎么运行，以及和 Verilator 怎么配合。

## 用例集

| 用例集 | 验证对象 | 说明 |
| --- | --- | --- |
| CUTE-Test | 矩阵单元 | 支持与 NEMU 参考模型逐步比对；在 CUTE 工程内单独构建运行，不经顶层 `make test`（后者是环境自检） |
| CUTE-CTRL | 控制通路 | 用例与调试入口 |
| TestTopWithL2 | 矩阵单元 + L2 | 存储侧改用一致性接口（无监听子集），自建 SN 侧功能模型，并提供事务合法性与超时定位 |
| CUTE-UVM | 矩阵单元 | UVM 层次化环境，按核心计算、数据流控制、存储加载、寄存器文件四层组织 |

## 与 Verilator 交叉确认

同一批用例分别在 Verilator 与 VCS 上运行，比较**通过/失败集合**与**超时签名**。两者逐条一致时，才能把故障收敛到设计本身而不是仿真器差异。

## 运行

先用关闭 ChiselDB 与 DRAMsim3 的配置跑通 Verilator，再进入 VCS：

```bash
make -C XSAI emu -j8 CONFIG=DefaultMatrixConfig \
  WITH_DRAMSIM3=0 WITH_CHISELDB=0 WITH_CONSTANTIN=0 \
  EMU_THREADS=8 EMU_TRACE=fst
```

## 覆盖率

以 Verilator 收集行覆盖率与分支覆盖率作为日常基线。覆盖率未达标时先分清两件事：挂死用例使下游路径根本没执行，还是真的存在覆盖遗漏。前者应先修用例。

VCS 侧用于补充确认和时序相关检查。
