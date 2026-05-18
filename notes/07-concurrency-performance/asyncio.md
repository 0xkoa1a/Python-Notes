# `asyncio`

`asyncio` 解决的是单线程内管理大量并发 IO 的问题。它不是让 CPU 计算变快的魔法。

**`asyncio` 的核心是事件循环：协程在 `await` 处主动让出控制权，事件循环在等待 IO 的任务之间切换。**

理解 async 的关键，是把“并发等待”和“并行计算”分开。

## 1. 协程函数

```python
async def fetch(url: str) -> str:
    response = await async_http_get(url)
    return response.text
```

调用协程函数不会立刻执行函数体，而是返回协程对象：

```python
coro = fetch("https://example.com") # coro 是协程对象
```

要运行它，需要事件循环：

```python
import asyncio

result = asyncio.run(fetch("https://example.com"))
```

## 2. `await`

`await` 表示：当前协程等待某个 awaitable 完成，并把控制权交还事件循环。

```python
async def main():
    text = await fetch("https://example.com")
    print(text)
```

如果一个 async 函数内部没有真正 await IO，只是做 CPU 循环，它不会带来并发收益，还会阻塞事件循环。

## 3. 并发任务

```python
async def main():
    task1 = asyncio.create_task(fetch("https://a.example"))
    task2 = asyncio.create_task(fetch("https://b.example"))

    # task1/task2 是 Task 对象，表示已交给事件循环调度的协程
    a = await task1
    b = await task2
```

更常见：

```python
results = await asyncio.gather(
    fetch("https://a.example"),
    fetch("https://b.example"),
)
```

`gather` 会并发等待多个 awaitable。

## 4. async 生态要求全链路配合

如果你在 async 函数中调用阻塞函数：

```python
async def bad():
    time.sleep(1) # 阻塞整个事件循环
```

应该用：

```python
async def good():
    await asyncio.sleep(1) # 让出事件循环
```

网络、数据库、文件库也一样。async 代码需要使用 async 版本的库，否则会阻塞事件循环。

## 5. 适合 asyncio 的任务

适合：

- 大量网络连接。
- async HTTP 客户端。
- async 数据库驱动。
- Web 服务。
- WebSocket。
- 高并发 IO 调度。

不适合：

- 纯 Python CPU-bound。
- 少量简单阻塞操作。
- 生态库没有 async API 的场景。

## 6. 检查表

使用 asyncio 前，按下面问：

1. 任务是否主要是 IO-bound？
2. 依赖库是否提供 async API？
3. 是否在 async 函数中调用了阻塞函数？
4. 是否用 `create_task` 或 `gather` 真正并发启动任务？
5. CPU-heavy 部分是否会阻塞事件循环？
6. 是否需要处理取消、超时和异常？

最小心智模型：

1. async 是并发等待，不是并行计算。
2. 协程在 `await` 处让出控制权。
3. 事件循环调度可运行任务。
4. 阻塞调用会卡住整个事件循环。
5. async 需要生态链配合。
