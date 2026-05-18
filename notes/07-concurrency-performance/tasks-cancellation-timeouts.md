# task、取消、超时与异常传播

并发代码的难点往往不在“启动多个任务”，而在任务失败、超时、取消时系统如何收束。

**Task 是被事件循环调度的协程；取消是向任务注入 `CancelledError`；超时是带时间边界的取消；并发异常需要明确传播和收集策略。**

## 1. Task 是什么

```python
import asyncio

async def work() -> int:
    await asyncio.sleep(1)
    return 42

async def main():
    task = asyncio.create_task(work())
    # task 是 Task 对象，表示已经被事件循环接管的协程
    result = await task
    print(result)
```

协程对象只是“可运行的异步计算”。Task 则表示“已经安排到事件循环中运行的协程”。

## 2. 异常传播

```python
async def fail():
    raise ValueError("boom")

async def main():
    task = asyncio.create_task(fail())
    await task  # 这里会重新抛出 ValueError
```

Task 内部异常不会消失。等待任务结果时，异常会传播给等待者。

如果创建 task 后没人 await，异常可能变成“Task exception was never retrieved”警告。

## 3. `gather`

```python
results = await asyncio.gather(task1(), task2())
```

默认情况下，一个 awaitable 抛异常，`gather` 会把异常传播出去。

如果想把异常作为结果收集：

```python
results = await asyncio.gather(
    task1(),
    task2(),
    return_exceptions=True,
)

for result in results:
    if isinstance(result, Exception):
        # result 是某个任务抛出的异常对象
        handle_error(result)
```

是否使用 `return_exceptions=True` 是语义选择：你想失败立刻中断，还是收集所有结果和错误。

## 4. 取消

```python
task = asyncio.create_task(work())
task.cancel()

try:
    await task
except asyncio.CancelledError:
    # 任务响应取消后会在 await 处抛出 CancelledError
    print("cancelled")
```

取消不是强杀线程。它是协作式的：在协程下一个可取消的 await 点抛出 `CancelledError`。

协程应在 finally 中清理资源：

```python
async def worker():
    try:
        await do_work()
    finally:
        await cleanup()
```

不要随便吞掉 `CancelledError`，否则调用者以为任务取消了，实际还在继续。

## 5. 超时

```python
try:
    result = await asyncio.wait_for(work(), timeout=2)
except TimeoutError:
    print("too slow")
```

`wait_for` 超时时会取消内部任务。

现代写法：

```python
async with asyncio.timeout(2):
    result = await work()
```

超时本质上是“时间到了就取消等待的任务或代码块”。

## 6. `TaskGroup`

现代结构化并发：

```python
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(work1())
        task2 = tg.create_task(work2())

    # 退出 TaskGroup 后，两个任务都已完成或异常已传播
    print(task1.result(), task2.result())
```

如果其中一个任务失败，TaskGroup 会取消其他任务，并以 `ExceptionGroup` 传播异常。

这比手动管理一堆 task 更结构化。

## 7. 检查表

写 async 并发时，按下面问：

1. 创建的 task 是否一定会被 await 或纳入 TaskGroup？
2. 异常是立即传播，还是收集后处理？
3. 是否有超时边界？
4. 取消时资源是否能清理？
5. 是否错误吞掉 `CancelledError`？
6. 是否应该使用 `TaskGroup`？

最小心智模型：

1. Task 是被调度的协程。
2. await task 会取得结果或重新抛异常。
3. 取消是协作式异常注入。
4. 超时通常通过取消实现。
5. TaskGroup 提供结构化并发边界。
