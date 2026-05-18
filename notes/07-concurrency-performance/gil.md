# GIL

GIL 是 Python 性能讨论里最容易被神化的概念。它既不是“Python 不能并发”的意思，也不是所有性能问题的根源。

**GIL 是 CPython 解释器中的全局解释器锁：在同一进程内，同一时刻通常只有一个线程执行 Python 字节码。**

注意这里有三个限定：CPython、同一进程、Python 字节码。

## 1. GIL 保护什么

CPython 的对象模型大量依赖引用计数。多个线程同时修改对象引用计数会很复杂。GIL 简化了解释器内部对象状态管理。

直观理解：

```text
多个线程可以存在
多个线程可以等待 IO
但执行 Python 字节码时通常要轮流拿 GIL
```

所以 GIL 主要限制的是 CPU 密集的纯 Python 多线程并行。

## 2. GIL 不阻止 IO 并发

当线程等待网络、磁盘、sleep 等 IO 时，GIL 可以释放给其他线程。

```python
from concurrent.futures import ThreadPoolExecutor
import time

def wait():
    time.sleep(1) # sleep 时当前线程不需要执行 Python 字节码
    return "done"

with ThreadPoolExecutor(max_workers=10) as pool:
    print(list(pool.map(lambda _: wait(), range(10))))
```

这类 IO-bound 任务用线程可以提升吞吐。

## 3. GIL 不限制多进程

每个进程有自己的 Python 解释器和自己的 GIL。

```text
process A -> GIL A
process B -> GIL B
```

所以 CPU-bound 任务可以用多进程并行，但代价是进程创建、序列化和进程间通信开销。

## 4. C 扩展可以释放 GIL

NumPy、PyTorch 等库的核心计算通常在 C/C++/CUDA 中执行。它们可能在长时间计算时释放 GIL，或者根本不在 Python 字节码层执行核心循环。

所以：

```python
array_a + array_b
```

快，不是因为 Python 循环快，而是因为一次 Python 调用进入了底层高效计算。

## 5. GIL 不是性能分析替代品

看到慢代码不要先喊 GIL。先问：

- 是 CPU-bound 还是 IO-bound？
- 时间花在 Python 循环，还是外部库？
- 是否在频繁创建对象？
- 是否在等待网络或磁盘？
- 是否有算法复杂度问题？

GIL 只是性能模型的一部分。

## 6. 检查表

遇到并发性能问题，按下面问：

1. 当前实现是 CPython 吗？
2. 慢任务是否执行大量 Python 字节码？
3. 任务是 CPU-bound 还是 IO-bound？
4. 线程是否主要在等待 IO？
5. 是否可以用多进程绕开同一 GIL？
6. 是否可以把核心计算交给 NumPy/PyTorch/C/Rust？

最小心智模型：

1. GIL 限制同进程多线程执行 Python 字节码。
2. IO 等待期间线程仍然有价值。
3. 多进程有多个 GIL。
4. 底层扩展可能释放 GIL。
5. 不要用 GIL 替代 profiling。
