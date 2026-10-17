# 常见故障排查 {#sec:debug-troubleshooting}

这一页按现象查原因。先按现象定位到小节，需要机制说明时再去对应章节。

## 构建类

### 内核 panic：No working init found

**日志**：`Failed to execute /init (error -2)` 之后 `Kernel panic - not syncing`。

**原因**：initramfs 里有 `/init`，但它指向的加载器路径在镜像中不存在。

**处理**：重建 rootfs。切换过环境时先清掉旧产物：

```bash
make -C firmware/riscv-rootfs clean
make firmware
```

## 运行类

### RTL 下 Linux 启动极慢

**现象**：OpenSBI 与早期 Linux 日志正常，后续启动耗时数分钟到数小时，guest 时间远慢于主机时间。

**原因**：Linux 的调度时间来自 `mtime` 与设备树的 `timebase-frequency`：

```text
每 guest 秒所需 RTL 周期数 = RTC 分频 × timebase-frequency
```

仿真硬件默认对 RTL 时钟 100 分频。DTB 若声明 10 MHz，一个 guest 秒就需要 10 亿周期，按你后端实测的仿真速率换算即可估出宿主时间。

关键在于**不同流程用的 DTB 不是同一个**：RTL 仿真用核内生成的 DTS，值为 1 MHz；`firmware/nemu_board/dts/build/xiangshan_ai.dtb` 由 DTSGen 为固件 / NEMU / QEMU 流程生成，默认 10 MHz。DTB 不能在两条流程之间直接搬运，给 RTL 或 NEMU 负载使用时按需重建：

```bash
make -C firmware build-dtb-xsai XSAI_TIMEBASE_FREQ=1000000
```

重建后要一起重建 payload。

**检查**：

```bash
fdtget firmware/nemu_board/dts/build/xiangshan_ai.dtb /cpus timebase-frequency
grep -E 'CONFIG_(HZ|NO_HZ|RISCV_TIMER|CPU_FREQ|RTC_CLASS)' firmware/riscv-linux/.config
```

内核启动日志里的 `Platform Timer Device : aclint-mtimer @ ...Hz` 应与之一致。启用 RTC 驱动或 CPUFreq 不能修正 mtime 比例问题。

### 导不出波形

确认编译期已启用 `EMU_TRACE`。运行期开关不能补上编译期缺失的支持。

### 挂起与卡死

排查顺序：是否仍有指令提交 → 矩阵完成事件是否产生 → 访存响应是否返回。

CUTE + L2 用例环境的看门狗只统计完成类里程碑（命令被接受、释放脉冲、内存侧完成），超时时会输出可复现的签名。

### 结果不一致

1. 先排除未定义行为：读取从未写入的矩阵寄存器区域、缺少必要同步、越界读写；
2. 用[差分验证](difftest.md#sec:debug-difftest)把问题收敛到具体指令与时刻；
3. 确认参考模型与 DUT 使用相同配置，配置不同会产生系统性误报。

### 矩阵访存 miss 的统计不可信

常规测试路径不会触发矩阵访存的 miss 通路，因此 miss 相关统计可能长期是异常值（例如全是 hit）。要评估 miss 性能，先在裸机小用例上确认 miss 通路本身行为正确。

## 软件适配高频故障

接矩阵单元后的问题集中在结果错和崩溃挂死两类，按现象检索。

### 结果错

| 现象 | 根因 | 处理 |
| --- | --- | --- |
| 某层输出全 0，测试报 `error=0` | 核在 `K_pad` 超限时 `memset(dst,0); return`，静默写零 | 提高容量上限，并让形状检查退回框架自带实现 |
| 像素行错位（第 1 行等于第 3 行） | 累加器行步长硬编码 64，实际 `tile_n=128` | 读累加器一律用 `tile_n` |
| 尾包（`real_count < DST_XUNIT`）结果错 | A 的 per-sz 步长用了固定的 `DST_XUNIT`，尾包实际是紧凑布局 | 用包内像素数 `min(real_count, EX)` |
| 板级整层错、QEMU 全对 | tile 尺寸写死在核里，与硬件实际值不符 | 只按探针读到的尺寸生成核，见[数据寄存器](../isa/registers.md#sec:xsai-registers) |
| bf16 结果差 1 ulp、测试边界挂 | 结果未截断到 bf16 网格 | 参考实现与 epilogue 统一截断 |
| attention 输出 0 或 inf | Q 打包与 KV cache 按 fp32 存，而 bf16 核按 2 字节读 | 同时修 Q 打包、KV 存储、指针与跨距的字节单位 |
| GEMV / depthwise 结果与 bf16 语义不符 | 这些旁路没走低精度约定 | 补 bf16 语义，或显式退回框架原实现 |

### 崩溃与挂死

| 现象 | 根因 | 处理 |
| --- | --- | --- |
| 板上 `rc=134`（`SIGABRT`） | 产物里硬编码了匿名池模式，`/dev/mem` 初始化失败即 abort | 池模式只由外部环境传入 |
| 板上 `rc=255` | 匿名池（非物理连续）下算错，被进程内的检查拦下 | 同上；板上必须走物理池 |
| 结果偶发错、不能稳定复现 | `mrelease` / `macquire` 未覆盖所有退出分支，或 MSC 基址寄存器被编译器回收 | 钉住 `s11`，同步覆盖全部退出路径 |
| 某个框架路径在该模拟器上报非法指令 | 框架自带的 fp16 RVV GEMM 与模拟器版本不兼容，与矩阵单元无关 | 关掉该特性绕开 |

### 验证误判

| 现象 | 根因 | 处理 |
| --- | --- | --- |
| 输出解析为空 | awk 未初始化变量把空值传给索引，argmax 落在 0 时打印空串 | 写 `print idx + 0`；每次运行前删除旧输出文件 |
| "加了模型但没进镜像" | 只看构建日志，没核对镜像内容 | 构建后解包核对，或校验镜像尺寸变化 |
| 测试全绿但结论错 | 测试跑的是另一套尺寸或另一条路径 | 打印实际尺寸与调用计数，确认跑的就是要测的路径 |
| 差分 dump 比对假失败 | 读到了 16 B 对齐引入的 padding（未初始化内存） | 只比对有效元素 |
| 自检"自洽地错" | 自检参考沿用了核的错误布局假设 | 参考实现的索引推导必须独立于核 |
| 预打包的 B tile 是旧数据 | `create_pipeline` 早于量化阶段 | 确认时序为 `load_param` → `load_model`（量化）→ `create_pipeline` |

### 构建与集成

| 现象 | 根因 | 处理 |
| --- | --- | --- |
| 交叉编译 CMake configure 失败 | 仍启用了宿主 x86 选项，`CMAKE_MAKE_PROGRAM` 未设 | 关闭宿主 ISA 选项，显式设置 `CMAKE_MAKE_PROGRAM` |
| 编译报找不到 `platform.h` | 漏了 build 目录的 include 路径 | 补 `-I<build>/src` |
| `sysroot` 变成 `/sysroot` | 同一行 `export A=x B=$A/y` 中 `$A` 尚未生效 | 分行 export |
| 模拟器报 `/lib/ld-linux-*.so.1 not found` | 漏设前缀环境变量 | 显式设置 `QEMU_LD_PREFIX` |
| 环境变量传 `"0"` 却当成打开 | 判定用了 `getenv() != NULL`，只判空不判值 | 改为比较取值 |
