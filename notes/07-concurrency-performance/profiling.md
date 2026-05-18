# profiling

性能优化的第一原则是测量。没有测量，优化很容易变成猜谜。

**profiling 的目标是找出时间和内存真正花在哪里；先定位瓶颈，再决定改算法、换数据结构、并发、向量化还是扩展。**

## 1. `timeit`

微基准：

```python
import timeit

elapsed = timeit.timeit(
    "sum(range(1000))",
    number=10_000,
)

print(elapsed)
```

`timeit` 会重复执行，减少偶然波动。适合比较小片段，不适合端到端业务性能。

## 2. `perf_counter`

粗略计时：

```python
import time

start = time.perf_counter()
run()
elapsed = time.perf_counter() - start

print(f"elapsed: {elapsed:.3f}s")
```

`perf_counter` 适合测量经过时间。不要用 `datetime.now()` 做性能计时。

## 3. `cProfile`

函数级 profiling：

```python
import cProfile

cProfile.run("main()", sort="cumtime")
```

常看指标：

- `ncalls`：调用次数。
- `tottime`：函数自身耗时。
- `cumtime`：函数及其子调用累计耗时。

`cumtime` 高说明这个调用路径整体重，`tottime` 高说明函数自身代码重。

## 4. `pstats`

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
main()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumtime").print_stats(20)
```

这样可以在代码里控制 profiling 范围。

## 5. `tracemalloc`

内存分配追踪：

```python
import tracemalloc

tracemalloc.start()

run()

snapshot = tracemalloc.take_snapshot()
top = snapshot.statistics("lineno")[:10]

for stat in top:
    print(stat)
```

`stat` 会告诉你哪些文件行分配内存最多。

## 6. 常见优化顺序

通常按这个顺序想：

1. 算法复杂度是否错了？
2. 是否重复做了同一件事？
3. 数据结构是否选错？
4. 是否能批量处理？
5. 是否能用标准库或高效第三方库？
6. 是否需要并发？
7. 是否需要扩展语言？

并发不是第一优化手段。坏算法并发后仍然坏。

## 7. 检查表

优化前，按下面问：

1. 有没有测量？
2. 瓶颈是时间、内存、IO 还是启动开销？
3. 是函数自身慢，还是子调用慢？
4. 是否存在明显算法问题？
5. 是否用错数据结构？
6. 并发是否真的匹配瓶颈？
7. 优化后是否重新测量？

最小心智模型：

1. 先测量，再优化。
2. `timeit` 测小片段。
3. `cProfile` 看函数耗时。
4. `tracemalloc` 看内存分配。
5. 优化是工程判断，不是工具炫技。
