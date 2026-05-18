# CPU-bound 与 IO-bound

并发模型选择的第一步，不是选线程还是 async，而是判断瓶颈在哪里。

**CPU-bound 卡在计算；IO-bound 卡在等待外部系统。不同瓶颈需要不同执行模型。**

把这一步判断错，后面的工具选择都会偏。

## 1. CPU-bound

CPU-bound 任务主要消耗 CPU：

- 纯 Python 大循环。
- 图片处理。
- 压缩解压。
- 加密哈希。
- 数值计算。
- 搜索和组合优化。

示例：

```python
def count_primes(n: int) -> int:
    count = 0
    for x in range(2, n):
        if is_prime(x):
            count += 1
    return count
```

如果核心循环是纯 Python，多线程通常不能让它在多个核心上并行执行。

可选方向：

- 改算法。
- 用 NumPy/PyTorch/Numba 等库。
- 用多进程。
- 写 C/Rust 扩展。

## 2. IO-bound

IO-bound 任务主要在等待：

- 网络请求。
- 数据库查询。
- 文件读写。
- 子进程完成。
- sleep / 定时器。

示例：

```python
def fetch(url: str) -> str:
    response = http_get(url) # 大部分时间在等网络
    return response.text
```

等待期间 CPU 没有忙，线程或 async 可以让程序同时处理别的等待任务。

可选方向：

- 线程池。
- `asyncio`。
- 批量请求。
- 连接池。

## 3. 混合任务

很多任务混合：

```text
下载数据 -> 解析 JSON -> 计算摘要 -> 写数据库
```

要拆开看：

- 下载：IO-bound。
- JSON 解析：可能 CPU-bound。
- 计算摘要：可能 CPU-bound。
- 写数据库：IO-bound。

整体优化要找真正瓶颈，而不是按任务名字猜。

## 4. 快速判断方法

观察 CPU 使用：

- 单核接近 100%，任务慢：可能 CPU-bound。
- CPU 很低，任务慢：可能在等 IO。

观察代码形态：

- 大量 Python for-loop：可能 CPU-bound。
- 大量网络/文件/数据库调用：可能 IO-bound。

最终还是要 profiling。

## 5. 选择表

```text
IO-bound + 阻塞库       -> 线程池
IO-bound + async 库     -> asyncio
CPU-bound + 纯 Python   -> 多进程 / 改算法 / 扩展
CPU-bound + 数组计算    -> NumPy / PyTorch
小任务数量巨大          -> 注意调度开销
```

工具不是越高级越好。匹配瓶颈才重要。

## 6. 检查表

选择并发模型前，按下面问：

1. 程序慢时 CPU 是否忙？
2. 时间是否花在等待外部系统？
3. 核心循环是否是纯 Python？
4. 是否有可用的高效库？
5. 任务粒度是否足够大，能抵消调度开销？
6. 是否先测量过再优化？

最小心智模型：

1. CPU-bound 等 CPU。
2. IO-bound 等外部系统。
3. 线程适合很多阻塞 IO。
4. async 适合 async 生态的 IO。
5. 多进程适合纯 Python CPU 并行。
6. 先分类，再选工具。
