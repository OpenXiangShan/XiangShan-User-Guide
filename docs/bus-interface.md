---
file_authors_:
- Sun Jiru <yuyake02@outlook.com> 
---

# 总线接口 {#sec:bus-interface}

{{var_processor_name}} 的总线接口具有 256 位宽度，支持 CHI Issue B 或 Issue E.b 的子集。
关于该协议的详细内容，请参考 AMBA® CHI Architecture Specification。

## 支持的响应类型

CHI 协议的 RespErr 可以表示响应正常或是错误。 {{var_processor_name}} 支持的响应类型如下。

| RespErr的值 | 响应类型                 |
| :---------: | ----------------------- |
| 0b00        | Normal Okay             |
| 0b01        | Exclusive Okay          |
| 0x11        | Non-data Error，即 NDERR |

由于 {{var_processor_name}} 不具有数据校验码，因此不支持 DERR。

## 不同总线响应下的行为

* Normal Okay：普通传输访问成功，或 exclusive 传输访问失败；读传输 exclusive 访问失败代表总线不支持 exclusive 传输，产生访问错误异常，写传输 exclusive 访问失败仅代表抢锁失败，不会返回异常。
* Exclusive Okay：exclusive 访问成功。
* NDERR：访问出错，读传输产生访问错误异常，写传输忽略此错误。

## 接口信号

CHI 使用不同的通道传输不同的消息，传输的消息包括：

* 数据（DAT）
* 请求（REQ）
* 响应（RSP）
* 监听（SNP）

以 TX 字母为前缀的通道用于发送消息，以 RX 字母为前缀的通道用于接收消息。
{{var_processor_name}} 一共有 6 个通道：

* RXDAT
* RXRSP
* RXSNP
* TXDAT
* TXREQ
* TXRSP

后文将会列出这些通道包含的信号。
除了这些通道外，总线接口还包含以下的信号。 

| 信号名               | I/O | 功能描述           |
| -------------------- | --- | ----------------- |
| chi_rx_linkactiveack | O   | 决定 RX 的状态。 |
| chi_rx_linkactivereq | I   | 决定 RX 的状态。 |
| chi_tx_linkactiveact | I   | 决定 TX 的状态。 |
| chi_tx_linkactivereq | O   | 决定 TX 的状态。 |
| chi_rxsactive        | I   | 表示 RX 有正在进行的事务。 |
| chi_txsactive        | O   | 表示 TX 有正在进行的事务。 |

RX 的 linkactiveack 和 linkactivereq 决定了 RX 的状态；TX 的 linkactiveack 和 linkactivereq 决定了 TX 的状态。

| 状态       | linkactivatereq | linkactivateack |
| ---------- | --------------- | --------------- |
| STOP       | 0               | 0               |
| ACTIVATE   | 1               | 0               |
| RUN        | 1               | 1               |
| DEACTIVATE | 0               | 1               |

### 通道信号

Table: RXDAT 通道信号

| 信号名              | I/O | 功能描述                      |
| ------------------- | --- | ---------------------------- |
| chi_rx_dat_flitv    | I   | flit 的有效信号，高电平表示 flit 有效           |
| chi_rx_dat_lcrdv    | O   | L-Credit 有效信号                             |
| chi_rx_dat_flit     | I   | RXDAT 通道的 flit                             |
| chi_rx_dat_flitpend | I   | flit 的 pending 信号，表示接下来会传输一个 flit |

Table: RXRSP 通道信号

| 信号名              | I/O | 功能描述                                        |
| ------------------- | --- | ----------------------------------------------- |
| chi_rx_rsp_flitv    | I   | flit 的有效信号，高电平表示 flit 有效           |
| chi_rx_rsp_lcrdv    | O   | L-Credit 的有效信号                           |
| chi_rx_rsp_flit     | I   | RXRSP 通道的 flit                             |
| chi_rx_rsp_flitpend | I   | flit 的 pending 信号，表示接下来会传输一个 flit |

Table: RXSNP 通道信号

| 信号名              | I/O | 功能描述                                        |
| ------------------- | --- | ----------------------------------------------- |
| chi_rx_snp_flitv    | I   | flit 的有效信号，高电平表示 flit 有效           |
| chi_rx_snp_lcrdv    | O   | L-Credit 的有效信号                           |
| chi_rx_snp_flit     | I   | RXSNP 通道的 flit                             |
| chi_rx_snp_flitpend | I   | flit 的 pending 信号，表示接下来会传输一个 flit |

Table: TXDAT 通道信号

| 信号名              | I/O | 功能描述                                        |
| ------------------- | --- | ----------------------------------------------- |
| chi_tx_dat_flitv    | O   | flit 的有效信号，高电平表示 flit 有效           |
| chi_tx_dat_lcrdv    | I   | L-Credit 的有效信号                           |
| chi_tx_dat_flit     | O   | TXDAT 通道的 flit                             |
| chi_tx_dat_flitpend | O   | flit 的 pending 信号，表示接下来会传输一个 flit |

Table: TXREQ 通道信号

| 信号名              | I/O | 功能描述                                        |
| ------------------- | --- | ----------------------------------------------- |
| chi_tx_req_flitv    | O   | flit 的有效信号，高电平表示 flit 有效           |
| chi_tx_req_lcrdv    | I   | L-Credit 的有效信号                           |
| chi_tx_req_flit     | O   | TXREQ 通道的 flit                             |
| chi_tx_req_flitpend | O   | flit 的 pending 信号，表示接下来会传输一个 flit |

Table: TXRSP 通道信号

| 信号名              | I/O | 功能描述                                        |
| ------------------- | --- | ----------------------------------------------- |
| chi_tx_rsp_flitv    | O   | flit 的有效信号，高电平表示 flit 有效           |
| chi_tx_rsp_lcrdv    | I   | L-Credit 的有效信号                           |
| chi_tx_rsp_flit     | O   | TXRSP 通道的 flit                             |
| chi_tx_rsp_flitpend | O   | flit 的 pending 信号，表示接下来会传输一个 flit |

### flit 格式

位宽为空，代表此信号与上一行的信号是共用的。
信号名后面标注\*，代表此信号仅适用于 CHI Issue E.b。
位宽后面标注\*，代表此信号在 CHI Issue B 和 Issue E.b 中具有不同的位宽，两个位宽中标注\*的是 E.b 中的位宽。

Table: Data flit

| 信号名        | 位宽 | 功能描述                      |
| ------------- | ------- | ---------------------------- |
| QoS                     | 4        | Quality of Service，数值越大优先级越高。 |
| TgtID                   | id_width | 目标 ID。 |
| SrcID                   | id_width | 来源 ID。 |
| TxnID                   | 8/12\*   | 事务 ID。 |
| HomeNID                 | id_width | Home 节点 ID，请求者在发送 CompAck 时把这个 ID 作为 TgtID。|
| Opcode                  | 3/4\*    | 操作码。 |
| RespErr                 | 2        | 相应错误码。 |
| Resp                    | 3        | 响应状态。 |
| DataSource              | 3/4\*    | 数据来源。 |
| {1'b0，FwdState[2:0]}\* |          | 指示从监听者发送到请求者的 CompData 中的状态。 |
| {1'b0, DataPull[2:0]}\* |          |
| CBusy                   | 3        | 完成者的繁忙程度，其编码由具体的实现决定。 |
| DBID                    | 8/12\*   | 数据缓冲区 ID，用于请求方的 TxnID。 |
| CCID                    | 2        | 关键数据块的 ID。 |
| DataID                  | 2        | 正在被传输的数据块的 ID。0b00 表示 [255:0]，0b10表示 [511:256]。 |
| TagOp                   | 2        | 表示要对 Tag 执行的操作。 |
| Tag                     | 8        | n 组 4 位 tag，每个 tag 绑定对应顺序的 16B 数据，地址对齐。 |
| TU                      | 2        | 指示要更新的 tag。 |
| TraceTag                | 1        | 标记，用于跟踪。 |
| RSVDC                   | 4        | 保留给用户使用，其含义由具体的实现决定。 |
| BE                      | 32       | 字节使能。表示每个字节是否有效。 |
| Data                    | 256      | 数据。 |

Table: Request flit

| 信号名        | 位宽 | 功能描述                      |
| ------------- | ------- | ---------------------------- |
| QoS                     | 4        | Quality of Service，数值越大优先级越高。 |
| TgtID                   | id_width | 目标 ID。 |
| SrcID                   | id_width | 来源 ID。 |
| TxnID                   | 8/12\*   | 事务 ID。 |
| ReturnNID               | id_width | 需要回复的节点 ID。 |
| StashNID                |          | Stash 请求的目标 ID。 |
| {4'b0, SLCRepHint[6:0]}\* |          | SLCRepHint：SLC 替换提示。 |
| StashNIDValid           | 1        | 用于 Stash 事务，表示 StashNID 是否有效。|
| Endian                  |          | 用于原子事务，0 表示小端，1 表示大端。|
| Deep                    |          | 在响应之前是否必须先写入最终目的地。|
| ReturnTxnID             | 8/12\*   | 用于DMT。|
| {6'b0，StashLPIDValid，StashLPID[4:0]}\* | | StashLPIDValid：用于 stash 事务，StashLPID 的有效信号。StashLPID：用于 Stash 事务。 |
| Opcode                  | 6/7\*    | 操作码。 |
| Size                    | 3        | 数据大小。 |
| Addr                    | RAW      | 地址。 |
| NS                      | 1        | 用于指示物理地址空间。 |
| LikelyShared            | 1        | 表示请求的数据是否可能与另一个请求节点共享。 |
| AllowRetry              | 1        | 是否允许重试。 |
| Order                   | 2        | 用于指定事务的顺序要求。 |
| PCrdType                | 4        | Credit 类型。 |
| MemAttr                 | 4        | 本次事务的属性。 |
| SnpAttr                 | 1        | Snoop 属性。 |
| DoDWT                   |          | 执行 DWT, 影响 DBIDResp 的 TgtID 和 TxnID 取值。 |
| PGroupID                | 5/8\*    | 用于 PCMO 事务。 |
| StashGroupID            |          | 用于 StashOnceSep 事务。 |
| TagGroupID              |          | 用于标记。 |
| {3'b0，LPID[4:0]}\*     |          | 逻辑处理器 ID，用于一个请求者包含多个逻辑处理器的情况。 |
| Excl                    | 1        | 用于 exclusive 事务。 |
| SnoopMe                 |          | 用于原子事务，指定是否必须向请求者发送 Snoop。 |
| ExpCompAck              | 1        | 表示事务是否包含了一个 CompAck 响应。|
| TagOp                   | 2        | 表示要对 Tag 执行的操作。 |
| TraceTag                | 1        | 标记，用于跟踪。 |
| RSVDC                   | 4        | 保留给用户使用，其含义由具体的实现决定。可以是任何值。 |

Table: Response flit

| 信号名        | 位宽 | 功能描述                      |
| ------------- | ------- | ---------------------------- |
| QoS           | 4        | Quality of Service，数值越大优先级越高。 |
| TgtID         | id_width | 目标 ID。 |
| SrcID         | id_width | 来源 ID。 |
| TxnID         | 8/12\*   | 事务 ID。 |
| Opcode        | 4/5\*    | 操作码。 |
| RespErr       | 2        | 响应错误码。 |
| Resp          | 3        | 响应状态。 |
| FwdState      | 3        | 用于 DCT，指示从监听者发送到请求者的 CompData 中的状态。 |
| {2'b0，DataPull} |       | 用于 Stash 事务，指示 Snoop 响应是否需要 Data Pull。 |
| CBusy         | 3        | 完成者的繁忙程度，其编码由具体的实现决定。 |
| DBID          | 8/12\*   | 数据缓冲区 ID，用于请求方的 TxnID。 |
| {4'b0，PGroupID[7:0]}     | | 用于 Persistent CMO 事务。 |
| {4'b0，StashGroupID[7:0]} | | 用于 Stash 事务。 |
| {4'b0，TagGroupID[7:0]}   | | 用于标记。 |
| PCrdType      | 4 | Credit 类型。 |
| TagOp         | 2 | 表示要对 Tag 执行的操作。 |
| TraceTag      | 1 | 标记，用于跟踪。 |

Table: Snoop flit

| 信号名        | 位宽 | 功能描述                      |
| ------------- | ------- | ---------------------------- |
| QoS                  | 4        | Quality of Service，数值越大优先级越高。 |
| SrcID                | id_width | 来源 ID。 |
| TxnID                | 8/12\*   | 事务 ID。 |
| FwdNID               | id_width | 指示 CompData 响应可以转发到哪个请求者。 |
| FwdTxnID             | 8/12\*   | 用于 DCT。|
| {6'b0，StashLPIDValid[0:0]，StashLPID[4:0]}\* | | StashLPIDValid：用于 Stash 事务，StashLPID 的有效位。StashLPID：用于 Stash 事务。 |
| {4'b0，VMIDExt[7:0]}\* |          | VMIDExt：用于 DVM 事务。|
| Opcode               | 5        | 操作码。 |
| Addr                 | SAW      | 地址。 |
| NS                   | 1        | 用于指示物理地址空间。 |
| DoNotGoToSD          | 1        | 指示是否要求 Snoopee 不转换到 SD 状态。 |
| RetToSrc             | 1        | 该字段请求 Snoopee 将缓存行的副本返回给 Home。 |
| TraceTag             | 1        | 标记，用于跟踪。 |

## 支持的 Coherency Transaction 类型

* SnpShared
* SnpClean
* SnpOnce
* SnpNotSharedDirty
* SnpUniqueStash
* SnpMakeInvalidStash
* SnpUnique
* SnpCleanShared
* SnpCleanInvalid
* SnpMakeInvalid
* SnpStashUnique
* SnpStashShared
* SnpSharedFwd
* SnpCleanFwd
* SnpOnceFwd
* SnpNotSharedDirtyFwd
* SnpUniqueFwd
