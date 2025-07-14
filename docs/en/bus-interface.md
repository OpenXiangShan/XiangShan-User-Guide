---
file_authors_:
- Sun Jiru <yuyake02@outlook.com>
---

# Bus Interface {#sec:bus-interface}

The bus interface of {{processor_name}} has a width of 256 bits and supports a
subset of AMBA CHI Issue B or Issue E.b. For detailed information about this
protocol, please refer to the AMBA® CHI Architecture Specification.

## Supported Response Types

The RespErr in the CHI protocol can indicate either a normal or an error
response. The response types supported by {{processor_name}} are as follows.

| Value of RespErr | Response type          |
| :--------------: | ---------------------- |
|       0b00       | Normal Okay            |
|       0b01       | Exclusive Okay         |
|       0x11       | Non-data Error (NDERR) |

Since {{processor_name}} does not have data error checking codes, it does not
support DERR.

## Behavior under different bus responses.

* Normal Okay: Indicates successful normal transfer access or failed exclusive
  transfer access. A failed exclusive read transfer implies the bus does not
  support exclusive transfers, triggering an access error exception. A failed
  exclusive write transfer only indicates lock acquisition failure without
  raising an exception.
* Exclusive Okay: Exclusive access successful.
* NDERR: Access error, read transactions generate access error exceptions, write
  transactions ignore this error.

## Interface signals

CHI uses different channels to transmit various messages, including:

* Data (DAT)
* Request (REQ)
* Response (RSP)
* Snoop (SNP)

Channels prefixed with TX are for sending messages, while those prefixed with RX
are for receiving messages. {{processor_name}} has a total of 6 channels:

* RXDAT
* RXRSP
* RXSNP
* TXDAT
* TXREQ
* TXRSP

The signals included in these channels will be listed later. In addition to
these channels, the bus interface also includes the following signals.

| Signal Name          | I/O | Functional Description                                |
| -------------------- | --- | ----------------------------------------------------- |
| chi_rx_linkactiveack | O   | Determines the state of RX.                           |
| chi_rx_linkactivereq | I   | Determines the state of RX.                           |
| chi_tx_linkactiveact | I   | Determines the state of TX.                           |
| chi_tx_linkactivereq | O   | Determines the state of TX.                           |
| chi_rxsactive        | I   | Indicates that there is an ongoing transaction in RX. |
| chi_txsactive        | O   | Indicates TX has ongoing transactions.                |

The state of RX is determined by linkactiveack and linkactivereq of RX; the
state of TX is determined by linkactiveack and linkactivereq of TX.

| Status     | linkactivatereq | linkactivateack |
| ---------- | --------------- | --------------- |
| STOP       | 0               | 0               |
| ACTIVATE   | 1               | 0               |
| RUN        | 1               | 1               |
| DEACTIVATE | 0               | 1               |

### Channel Signals

Table: RXDAT Channel Signals

| Signal Name         | I/O | Functional Description                                                         |
| ------------------- | --- | ------------------------------------------------------------------------------ |
| chi_rx_dat_flitv    | I   | The valid signal of the flit, high level indicates the flit is valid.          |
| chi_rx_dat_lcrdv    | O   | L-Credit valid signal                                                          |
| chi_rx_dat_flit     | I   | RXDAT channel flit                                                             |
| chi_rx_dat_flitpend | I   | The pending signal of a flit, indicating that a flit will be transmitted next. |

Table: RXRSP Channel Signals

| Signal Name         | I/O | Functional Description                                                         |
| ------------------- | --- | ------------------------------------------------------------------------------ |
| chi_rx_rsp_flitv    | I   | The valid signal of the flit, high level indicates the flit is valid.          |
| chi_rx_rsp_lcrdv    | O   | Valid signal for L-Credit                                                      |
| chi_rx_rsp_flit     | I   | Flit of RXRSP channel                                                          |
| chi_rx_rsp_flitpend | I   | The pending signal of a flit, indicating that a flit will be transmitted next. |

Table: RXSNP Channel Signals

| Signal Name         | I/O | Functional Description                                                         |
| ------------------- | --- | ------------------------------------------------------------------------------ |
| chi_rx_snp_flitv    | I   | The valid signal of the flit, high level indicates the flit is valid.          |
| chi_rx_snp_lcrdv    | O   | Valid signal for L-Credit                                                      |
| chi_rx_snp_flit     | I   | Flit of RXSNP channel                                                          |
| chi_rx_snp_flitpend | I   | The pending signal of a flit, indicating that a flit will be transmitted next. |

Table: TXDAT Channel Signals

| Signal Name         | I/O | Functional Description                                                         |
| ------------------- | --- | ------------------------------------------------------------------------------ |
| chi_tx_dat_flitv    | O   | The valid signal of the flit, high level indicates the flit is valid.          |
| chi_tx_dat_lcrdv    | I   | Valid signal for L-Credit                                                      |
| chi_tx_dat_flit     | O   | Flit of TXDAT channel                                                          |
| chi_tx_dat_flitpend | O   | The pending signal of a flit, indicating that a flit will be transmitted next. |

Table: TXREQ Channel Signals

| Signal Name         | I/O | Functional Description                                                         |
| ------------------- | --- | ------------------------------------------------------------------------------ |
| chi_tx_req_flitv    | O   | The valid signal of the flit, high level indicates the flit is valid.          |
| chi_tx_req_lcrdv    | I   | Valid signal for L-Credit                                                      |
| chi_tx_req_flit     | O   | Flit of TXREQ channel                                                          |
| chi_tx_req_flitpend | O   | The pending signal of a flit, indicating that a flit will be transmitted next. |

Table: TXRSP Channel Signals

| Signal Name         | I/O | Functional Description                                                         |
| ------------------- | --- | ------------------------------------------------------------------------------ |
| chi_tx_rsp_flitv    | O   | The valid signal of the flit, high level indicates the flit is valid.          |
| chi_tx_rsp_lcrdv    | I   | Valid signal for L-Credit                                                      |
| chi_tx_rsp_flit     | O   | Flit of TXRSP channel                                                          |
| chi_tx_rsp_flitpend | O   | The pending signal of a flit, indicating that a flit will be transmitted next. |

### flit format

Empty bit width indicates this signal shares with the previous line's signal.
Signal name annotated with * means this signal only applies to CHI Issue E.b.
Bit width annotated with * indicates this signal has different widths in CHI
Issue B and Issue E.b, with the * marking E.b's width.

Table: Data flit

| Signal Name            | Bit width | Functional Description                                                                          |
| ---------------------- | --------- | ----------------------------------------------------------------------------------------------- |
| QoS                    | 4         | Quality of Service, higher values indicate higher priority.                                     |
| TgtID                  | id_width  | Target ID.                                                                                      |
| SrcID                  | id_width  | Source ID.                                                                                      |
| TxnID                  | 8/12*     | Transaction ID.                                                                                 |
| HomeNID                | id_width  | Home node ID, which the requester uses as TgtID when sending CompAck.                           |
| Opcode                 | 3/4*      | Opcode.                                                                                         |
| RespErr                | 2         | Corresponding error code.                                                                       |
| Resp                   | 3         | Response status.                                                                                |
| DataSource             | 3/4*      | Data source.                                                                                    |
| {1'b0, FwdState[2:0]}* |           | Indicates the status in the CompData sent from the snooper to the requester.                    |
| {1'b0, DataPull[2:0]}* |           |                                                                                                 |
| CBusy                  | 3         | The busy level of the completer, with encoding determined by specific implementation.           |
| DBID                   | 8/12*     | Data buffer ID, used for requester's TxnID.                                                     |
| CCID                   | 2         | ID of the critical data block.                                                                  |
| DataID                 | 2         | The ID of the data block being transmitted. 0b00 represents [255:0], 0b10 represents [511:256]. |
| TagOp                  | 2         | Indicates the operation to be performed on the Tag.                                             |
| Tag                    | 8         | n groups of 4-bit tags, each tag bound to corresponding 16B data in order, address-aligned.     |
| TU                     | 2         | Indicates the tag to be updated.                                                                |
| TraceTag               | 1         | Tag, used for tracking.                                                                         |
| RSVDC                  | 4         | Reserved for user-defined purposes, with meanings determined by specific implementations.       |
| BE                     | 32        | Byte enable. Indicates whether each byte is valid.                                              |
| Data                   | 256       | Data.                                                                                           |

Table: Request flit

| Signal Name                            | Bit width | Functional Description                                                                                     |
| -------------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------- |
| QoS                                    | 4         | Quality of Service, higher values indicate higher priority.                                                |
| TgtID                                  | id_width  | Target ID.                                                                                                 |
| SrcID                                  | id_width  | Source ID.                                                                                                 |
| TxnID                                  | 8/12*     | Transaction ID.                                                                                            |
| ReturnNID                              | id_width  | Node ID requiring a response.                                                                              |
| StashNID                               |           | The target ID of the Stash request.                                                                        |
| {4'b0, SLCRepHint[6:0]}*               |           | SLCRepHint: SLC replacement hint.                                                                          |
| StashNIDValid                          | 1         | Used for Stash transactions, indicating whether StashNID is valid.                                         |
| Endian                                 |           | Used for atomic transactions, 0 indicates little-endian, 1 indicates big-endian.                           |
| Deep                                   |           | Whether the final destination must be written before responding.                                           |
| ReturnTxnID                            | 8/12*     | For DMT.                                                                                                   |
| {6'b0, StashLPIDValid, StashLPID[4:0]} |           | StashLPIDValid: Valid signal for StashLPID in stash transactions. StashLPID: Used for Stash transactions.  |
| Opcode                                 | 6/7*      | Opcode.                                                                                                    |
| Size                                   | 3         | Data size.                                                                                                 |
| Addr                                   | RAW       | Address.                                                                                                   |
| NS                                     | 1         | Indicates the physical address space.                                                                      |
| LikelyShared                           | 1         | Indicates whether the requested data may be shared with another requesting node.                           |
| AllowRetry                             | 1         | Whether retry is allowed.                                                                                  |
| Order                                  | 2         | Used to specify the order requirements of transactions.                                                    |
| PCrdType                               | 4         | Credit type.                                                                                               |
| MemAttr                                | 4         | Attributes of this transaction.                                                                            |
| SnpAttr                                | 1         | Snoop attribute.                                                                                           |
| DoDWT                                  |           | Execute DWT, affecting the TgtID and TxnID values of DBIDResp.                                             |
| PGroupID                               | 5/8*      | Used for PCMO transactions.                                                                                |
| StashGroupID                           |           | Used for StashOnceSep transactions.                                                                        |
| TagGroupID                             |           | Used for tagging.                                                                                          |
| {3'b0, LPID[4:0]}*                     |           | Logical processor ID, used when a requester contains multiple logical processors.                          |
| Excl                                   | 1         | For exclusive transactions.                                                                                |
| SnoopMe                                |           | For atomic transactions, specifies whether a Snoop must be sent to the requester.                          |
| ExpCompAck                             | 1         | Indicates whether the transaction includes a CompAck response.                                             |
| TagOp                                  | 2         | Indicates the operation to be performed on the Tag.                                                        |
| TraceTag                               | 1         | Tag, used for tracking.                                                                                    |
| RSVDC                                  | 4         | Reserved for user-defined purposes, with meaning determined by specific implementations. Can be any value. |

Table: Response flit

| Signal Name               | Bit width | Functional Description                                                                 |
| ------------------------- | --------- | -------------------------------------------------------------------------------------- |
| QoS                       | 4         | Quality of Service, higher values indicate higher priority.                            |
| TgtID                     | id_width  | Target ID.                                                                             |
| SrcID                     | id_width  | Source ID.                                                                             |
| TxnID                     | 8/12*     | Transaction ID.                                                                        |
| Opcode                    | 4/5*      | Opcode.                                                                                |
| RespErr                   | 2         | Response error code.                                                                   |
| Resp                      | 3         | Response status.                                                                       |
| FwdState                  | 3         | Used for DCT, indicating the state in CompData sent from the snooper to the requester. |
| {2'b0, DataPull}          |           | For Stash transactions, indicates whether the Snoop response requires Data Pull.       |
| CBusy                     | 3         | The busy level of the completer, with encoding determined by specific implementation.  |
| DBID                      | 8/12*     | Data buffer ID, used for requester's TxnID.                                            |
| {4'b0, PGroupID[7:0]}     |           | Used for Persistent CMO transactions.                                                  |
| {4'b0, StashGroupID[7:0]} |           | For Stash transactions.                                                                |
| {4'b0, TagGroupID[7:0]}   |           | Used for tagging.                                                                      |
| PCrdType                  | 4         | Credit type.                                                                           |
| TagOp                     | 2         | Indicates the operation to be performed on the Tag.                                    |
| TraceTag                  | 1         | Tag, used for tracking.                                                                |

Table: Snoop flit

| Signal Name                                  | Bit width | Functional Description                                                                                           |
| -------------------------------------------- | --------- | ---------------------------------------------------------------------------------------------------------------- |
| QoS                                          | 4         | Quality of Service, higher values indicate higher priority.                                                      |
| SrcID                                        | id_width  | Source ID.                                                                                                       |
| TxnID                                        | 8/12*     | Transaction ID.                                                                                                  |
| FwdNID                                       | id_width  | Indicates to which requester the CompData response can be forwarded.                                             |
| FwdTxnID                                     | 8/12*     | Used for DCT.                                                                                                    |
| {6'b0, StashLPIDValid[0:0], StashLPID[4:0]}* |           | StashLPIDValid: Used for Stash transactions, the valid bit of StashLPID. StashLPID: Used for Stash transactions. |
| {4'b0, VMIDExt[7:0]}*                        |           | VMIDExt: Used for DVM transactions.                                                                              |
| Opcode                                       | 5         | Opcode.                                                                                                          |
| Addr                                         | SAW       | Address.                                                                                                         |
| NS                                           | 1         | Indicates the physical address space.                                                                            |
| DoNotGoToSD                                  | 1         | Indicates whether the Snoopee is required not to transition to the SD state.                                     |
| RetToSrc                                     | 1         | This field requests the Snoopee to return a copy of the cache line to Home.                                      |
| TraceTag                                     | 1         | Tag, used for tracking.                                                                                          |

## Supported Coherency Transaction types.

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
