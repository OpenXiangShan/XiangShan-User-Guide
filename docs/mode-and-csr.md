---
file_authors_:
- zengjinhong <zengjinhong21@mails.ucas.ac.cn>
---

## 处理器模式与控制寄存器

### 处理器模式

{{var_processor_name}} 支持 RISC-V 特权架构手册规定的以下 5 种特权模式。

Table: {{var_processor_name}} 支持的特权级列表

| 名称                                    | 缩写  | PRIV  |   V   |
| --------------------------------------- | :---: | :---: | :---: |
| 机器模式（Machine mode）                |   M   |   3   |   0   |
| 监管模式（Supervisor mode）             | HS/S  |   1   |   0   |
| 用户模式（User mode）                   |   U   |   0   |   0   |
| 虚拟监管模式（Virtual supervisor mode） |  VS   |   1   |   1   |
| 虚拟用户模式（Virtual user mode）       |  VU   |   0   |   1   |

当 V 关闭时，昆明湖支持 RISC-V 的三种特权模式：Machine-mode（机器模式）、Supervisor-mode（监管模式）以及 User-mode（用户模式）（在下面分别称为 M 模式，S 模式，U 模式）。三种模式在对寄存器的访问、特权指令的使用、内存空间的访问上存在区别，其中 M 模式的权限最高，U 模式的权限最低。昆明湖初始化时处在 M 模式。

* U 模式：该模式下通常运行常规应用程序，只能访问指定给普通用户模式的寄存器，避免其接触特权信息。
* S 模式：该模式下通常运行操作系统，它可以访问除了机器模式的寄存器以外的寄存器，它协同调度常规用户程序，为它们提供管理与服务。
* M 模式：该模式拥有最高权限，拥有所有资源的使用权。

当 V 开启时，TODO

### 控制寄存器

