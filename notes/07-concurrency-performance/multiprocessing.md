# 进程

多进程适合绕开同一进程内的 GIL，让 CPU-bound 任务在多个核心上并行执行。

**每个进程有独立解释器、独立内存和独立 GIL；进程间通信需要序列化数据，因此并行收益要和通信开销一起算。**

## 1. 进程池

```python
from concurrent.futures import ProcessPoolExecutor

def compute(x: int) -> int:
    return x * x

with ProcessPoolExecutor() as pool:
    results = list(pool.map(compute, range(10)))
```

任务函数和参数需要能被序列化，通常依赖 pickle。

## 2. 适合进程的任务

适合：

- 纯 Python CPU-bound。
- 每个任务粒度较大。
- 输入输出数据不太大。
- 任务之间独立。

不适合：

- 大量小任务。
- 频繁共享状态。
- 需要传巨大对象。
- 已经由 NumPy/PyTorch 底层并行处理的计算。

## 3. 进程不共享普通内存

```python
items = []

def worker(x):
    items.append(x) # 修改的是子进程自己的 items
```

子进程里的修改不会自动出现在父进程。应该通过返回值收集：

```python
with ProcessPoolExecutor() as pool:
    results = list(pool.map(worker, range(10)))
```

共享内存和 Manager 存在，但会增加复杂度。优先设计独立任务。

## 4. Windows 上的入口保护

跨平台多进程代码应使用：

```python
def main() -> None:
    with ProcessPoolExecutor() as pool:
        ...

if __name__ == "__main__":
    main()
```

Windows 创建子进程需要重新导入主模块。如果顶层直接创建进程，可能递归创建子进程。

## 5. 检查表

使用多进程前，按下面问：

1. 任务是否真的是 CPU-bound？
2. 任务粒度是否足够大？
3. 参数和返回值是否可序列化？
4. 数据传输开销是否会抵消并行收益？
5. 是否需要跨平台入口保护？
6. 是否可以避免共享状态？

最小心智模型：

1. 多进程绕开同一 GIL。
2. 进程内存彼此独立。
3. 通信需要序列化。
4. CPU-bound 独立任务最适合进程池。
5. Windows 需要 `if __name__ == "__main__"` 保护。
