---
file_authors_:
- yimingyan <1650150317@qq.com> 
- Yujunjie <yujunjie21@mails.ucas.ac.cn> 
---

### 内存模型

#### 内存属性

{{var_processor_name}} 支持三种内存类型，分别是可高速缓存内存、不可高速缓存内存和不可缓存外设。

地址的物理内存属性（Physical Memory Attributes）由硬件规定，其支持 RISC-V 手册中所规定的属性：

* R（Read Permission）：可读权限
* W（Write Permission）：可写权限
* X（Execute Permission）：可执行权限
* A（Address matching mode）：地址匹配模式
* L（Lock Bit）：锁定状态

同时 {{var_processor_name}} 还支持 atomic（支持原子指令）属性和 c（支持高速缓存）属性。

#### 内存一致性模型

可高速缓存内存采用 RVWMO（RISC-V Weak Memory Ordering）内存模型。在该模型下，多核之间内存实际的读写顺序和程序给定的访问顺序会不一致。因此 RISC-V 的指令集架构中提供了 Fence 指令来保证内存访问的同步。同时 RISC-V 的 A 扩展中还提供了 LR/SC 指令和 AMO 指令来进行加锁和原子操作。

不可高速缓存内存和不可缓存外设两种内存类型都是强有序（strongly ordered）的。
