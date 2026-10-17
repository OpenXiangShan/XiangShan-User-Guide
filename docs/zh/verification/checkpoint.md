# Checkpoint 与切片 {#sec:debug-checkpoint}

完整负载在 RTL 上跑一次代价很高，切片把关注的部分取出来单独跑。这一章讲切片怎么做、checkpoint 怎么生成，以及恢复时哪些状态不在其中。

## 验证梯度

先用快的排除软件问题，再上 RTL：

```bash
make run-qemu                                  # 最快，先排软件与启动路径
make run-nemu                                  # 次快，golden model 侧的中间层
make ckpt                                      # 制作 checkpoint
make run-nemu PAYLOAD=<checkpoint.zstd>        # 在 NEMU 上验证 checkpoint
make run-emu  PAYLOAD=<checkpoint.zstd>        # 最后在 RTL 上运行
```

## 关注区域怎么标

关注区域由负载自己声明，外层脚本据此选择切片流程：

| 信号 | 含义 |
| --- | --- |
| `DISABLE_TIME_INTR` | 准备采样：关闭定时器中断 |
| `NOTIFY_PROFILER` | 进入关注区域 |
| `NOTIFY_PROFILE_EXIT` | 退出关注区域 |
| `GOOD_TRAP` | 正常结束 |

最小骨架是在关注区域前后各发一次信号。

按 SimPoint 聚类结果做 checkpoint 必须用 `make ckpt PHASE=checkpoint`，它对应 `make profile`、`make cluster` 之后的那一步。直接 `make ckpt` 走 `PHASE=all`，会跳过 profile 与 cluster 直接出一个切片，不按聚类结果生成。

## checkpoint 不含矩阵状态

**当前 checkpoint 与恢复链路不覆盖矩阵状态**，做矩阵相关的切片分析必须把这一点当前提：

| 项 | 是否随 checkpoint 恢复 |
| --- | --- |
| 矩阵寄存器堆（`tr0` – `tr3`、`acc0` – `acc3`） | **否**，载荷中没有对应段 |
| 矩阵 CSR（`mcsr` 及其余配置位） | **否**，恢复固件的清单不含矩阵 CSR |
| `mstatus.MS` 位 | **是**，随 `mstatus` 一起恢复 |
| `mtilem` / `mtilen` / `mtilek` / `msync` | **否** |

作为对照，向量寄存器有专门的镜像段。矩阵寄存器堆两边都没有。

由此得到的实践要求：

* **采样点必须让矩阵单元处于静止状态**。已提交但还没在矩阵单元里完成的操作，如果在恢复侧丢失，会造成架构上看不见的状态发散，而载荷里没有"矩阵单元空闲"这类标记；
* 需要显式同步时用 `macquire` / `mrelease` / `msyncregreset`；
* 恢复后不要假设 `mxrm` / `mfrm` / `msaten` / `msat` / `mfflags` 与采样点一致。

状态语义的完整说明见[矩阵异常与中断](../isa/exception.md#sec:xsai-exception)。

## 系统级场景

大模型可以打包进 `gcpt.bin`，在功能模拟器与 RTL 之间复用，避免重复加载权重。需要 Linux 环境的负载可以用带操作系统的镜像，配合 checkpoint 恢复流程。

## 两个注意点

* QEMU 与 RTL 的 `timebase-frequency` 假设不同，DTB 不能直接混用，见[常见故障排查](troubleshooting.md#sec:debug-troubleshooting)；
* 切片越细，单次迭代越快，但要确认切片起点处的缓存状态与完整运行一致，否则性能结论会偏移。
