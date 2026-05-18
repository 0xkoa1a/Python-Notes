# 线程

线程适合让一个进程同时等待多个阻塞 IO。它不是让纯 Python CPU 循环自动跑满多核的工具。

**在 CPython 中，线程共享进程内存，也共享同一个 GIL；它们适合 IO-bound 阻塞任务，但共享可变状态需要同步。**

## 1. 线程池

日常优先用 `ThreadPoolExecutor`：

```python
from concurrent.futures import ThreadPoolExecutor

def fetch(url: str) -> str:
    return blocking_http_get(url)

urls = ["https://example.com/a", "https://example.com/b"]

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(fetch, urls))
```

`pool.map` 会把多个任务分发给线程。`results` 顺序和输入顺序一致。

## 2. Future

```python
with ThreadPoolExecutor(max_workers=4) as pool:
    future = pool.submit(fetch, "https://example.com")
    # future 表示一个尚未完成或已经完成的异步结果
    result = future.result()
```

`future.result()` 会等待任务完成。如果任务中抛异常，调用 `result()` 时会重新抛出。

## 3. 共享状态

线程共享内存：

```python
items: list[int] = []
```

多个线程同时修改共享对象可能产生竞态。用锁保护关键区：

```python
from threading import Lock

lock = Lock()
items: list[int] = []

def add_item(x: int) -> None:
    with lock:
        # lock 保护这个共享列表的修改
        items.append(x)
```

更好的策略是尽量减少共享可变状态，让线程返回结果，由主线程汇总。

## 4. 适合线程的任务

适合：

- 阻塞网络请求。
- 文件 IO。
- 调用阻塞外部命令。
- 等待数据库响应。

不适合：

- 纯 Python 大量计算。
- 需要复杂共享状态协作。
- 任务非常小导致调度开销占主导。

## 5. 检查表

使用线程前，按下面问：

1. 任务是否主要在等待阻塞 IO？
2. 使用的库是否是阻塞 API？
3. 是否有共享可变状态？
4. 共享状态是否需要锁？
5. 是否可以让任务返回结果而不是共享写入？
6. `max_workers` 是否合理？

最小心智模型：

1. 线程共享内存。
2. CPython 线程共享 GIL。
3. 线程适合 IO-bound 阻塞任务。
4. `Future` 表示异步结果。
5. 共享可变状态需要同步。
