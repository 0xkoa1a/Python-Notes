# 上下文管理器

上下文管理器解决的不是“语法好看”问题，而是资源生命周期问题。

**`with` 的核心含义是：进入一段受保护的执行区域；无论正常返回还是异常退出，都按协议执行清理逻辑。**

这让文件、锁、数据库连接、事务、临时状态修改等操作可以用统一方式表达。

## 1. 为什么需要上下文管理器

看文件读取：

```python
f = open("data.txt", encoding="utf-8")
text = f.read()
f.close()
```

如果 `read()` 抛出异常，`close()` 可能不会执行。

手写 `try/finally`：

```python
f = open("data.txt", encoding="utf-8")
try:
    text = f.read()
finally:
    f.close()
```

这才是可靠的资源释放。

`with` 是这类模式的协议化写法：

```python
with open("data.txt", encoding="utf-8") as f:
    text = f.read()
```

它表达的是：

```text
进入资源上下文
执行代码块
无论如何退出，都离开资源上下文
```

## 2. `with` 的真实模型

这段代码：

```python
with expr as target:
    body
```

大致等价于：

```python
manager = expr
enter = type(manager).__enter__
exit = type(manager).__exit__

target = enter(manager)
try:
    body
except BaseException as exc:
    suppress = exit(manager, type(exc), exc, exc.__traceback__)
    if not suppress:
        raise
else:
    exit(manager, None, None, None)
```

真实实现有更多细节，但核心就是：

- 进入时调用 `__enter__`。
- 退出时调用 `__exit__`。
- 如果代码块抛出异常，异常信息传给 `__exit__`。
- 如果 `__exit__` 返回真值，异常被吞掉。
- 如果 `__exit__` 返回假值，异常继续传播。

## 3. `__enter__` 与 `__exit__`

自定义上下文管理器：

```python
class Managed:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("exit")
        return False

with Managed() as m:
    print("body")
```

输出：

```text
enter
body
exit
```

`__enter__` 的返回值会绑定给 `as` 后面的名字：

```python
class Connection:
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False
```

`as` 绑定的不一定是上下文管理器自己，而是 `__enter__` 返回的对象：

```python
class Manager:
    def __enter__(self):
        return "resource"

    def __exit__(self, exc_type, exc, tb):
        return False

with Manager() as value:
    print(value)  # resource
```

## 4. 异常如何传给 `__exit__`

如果 `with` 块内没有异常：

```python
__exit__(None, None, None)
```

如果有异常：

```python
__exit__(exc_type, exc, traceback)
```

示例：

```python
class Watch:
    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("exc_type:", exc_type)
        print("exc:", exc)
        return False

with Watch():
    1 / 0
```

`__exit__` 会收到 `ZeroDivisionError` 的类型和值。

如果 `__exit__` 返回 `False` 或 `None`，异常继续传播：

```python
class NoSuppress:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False
```

如果返回真值，异常被抑制：

```python
class SuppressZeroDivision:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return exc_type is ZeroDivisionError

with SuppressZeroDivision():
    1 / 0

print("still running")
```

吞异常是很强的行为。除非语义非常明确，否则不要随便返回 `True`。

## 5. 用 `try/finally` 理解 `with`

上下文管理器最重要的价值是把清理放进 `finally` 语义中。

```python
class TempState:
    def __init__(self, obj, value):
        self.obj = obj
        self.value = value
        self.old_value = None

    def __enter__(self):
        self.old_value = self.obj.value
        self.obj.value = self.value
        return self.obj

    def __exit__(self, exc_type, exc, tb):
        self.obj.value = self.old_value
        return False
```

使用：

```python
with TempState(config, "debug"):
    run()
```

无论 `run()` 正常结束还是抛异常，旧状态都会恢复。

这类模式包括：

- 打开后关闭。
- 加锁后释放。
- 开启事务后提交或回滚。
- 临时修改环境后恢复。
- 捕获日志或标准输出后恢复。

## 6. `contextlib.contextmanager`

如果上下文管理器逻辑简单，可以用生成器写：

```python
from contextlib import contextmanager

@contextmanager
def managed():
    print("enter")
    try:
        yield "resource"
    finally:
        print("exit")

with managed() as resource:
    print(resource)
```

`yield` 前是 `__enter__` 逻辑，`yield` 的值是 `as` 绑定的值，`finally` 中是 `__exit__` 逻辑。

等价心智模型：

```text
yield 之前：进入
yield 出来的值：资源
yield 之后 / finally：退出
```

如果代码块中抛出异常，异常会在 `yield` 那一行重新抛入生成器：

```python
from contextlib import contextmanager

@contextmanager
def log_errors():
    try:
        yield
    except Exception as exc:
        print("error:", exc)
        raise
```

如果在生成器上下文管理器里捕获异常后不重新抛出，就相当于抑制异常：

```python
from contextlib import contextmanager

@contextmanager
def suppress_value_error():
    try:
        yield
    except ValueError:
        pass
```

这和 `__exit__` 返回真值一致。

## 7. `contextlib` 常用工具

### `closing`

把只有 `close()` 方法的对象包装成上下文管理器：

```python
from contextlib import closing

with closing(get_resource()) as resource:
    use(resource)
```

退出时调用 `resource.close()`。

### `suppress`

明确抑制指定异常：

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    path.unlink()
```

这比空的 `except FileNotFoundError: pass` 更集中地表达意图。

但不要滥用：

```python
with suppress(Exception):
    do_many_things()
```

这会隐藏太多错误。

### `nullcontext`

在有时需要上下文管理器、有时不需要时使用：

```python
from contextlib import nullcontext

cm = open(path) if path else nullcontext(default_file)

with cm as f:
    process(f)
```

它的 `__enter__` 直接返回 `default_file`，`__exit__` 什么都不做。

### `ExitStack`

动态管理多个上下文：

```python
from contextlib import ExitStack

paths = ["a.txt", "b.txt", "c.txt"]

with ExitStack() as stack:
    files = [stack.enter_context(open(path)) for path in paths]
    process(files)
```

如果打开第三个文件时失败，前面已经打开的文件也会被正确关闭。

`ExitStack` 适合上下文数量运行时才知道的情况。

## 8. 多个上下文管理器

可以同时写多个：

```python
with open("in.txt") as src, open("out.txt", "w") as dst:
    dst.write(src.read())
```

进入顺序从左到右，退出顺序从右到左。

等价于嵌套：

```python
with open("in.txt") as src:
    with open("out.txt", "w") as dst:
        dst.write(src.read())
```

退出顺序反过来很重要，因为后进入的资源往往依赖先进入的资源。

## 9. 上下文管理器与事务

数据库事务是上下文管理器的典型场景：

```python
with transaction() as tx:
    update_user(tx)
    write_log(tx)
```

语义可以设计为：

- 正常退出：提交事务。
- 异常退出：回滚事务。

示意：

```python
class Transaction:
    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False
```

这比让调用者手动记住 `commit` / `rollback` 更稳，因为协议把清理路径固定下来。

## 10. 上下文管理器不是资源本身

有时资源对象自己就是上下文管理器：

```python
with open("data.txt") as f:
    ...
```

有时上下文管理器只是管理某种状态：

```python
with decimal.localcontext() as ctx:
    ctx.prec = 50
    ...
```

还有时上下文管理器返回另一个对象：

```python
with lock:
    ...
```

锁的 `__enter__` 可能只负责 acquire，`__exit__` 负责 release。

不要强行认为 `as` 后面的对象一定就是管理器本身。应看 `__enter__` 返回什么。

## 11. 异步上下文管理器

异步上下文管理器使用：

```python
async with expr as target:
    ...
```

对应协议是：

```python
async def __aenter__(self):
    ...

async def __aexit__(self, exc_type, exc, tb):
    ...
```

常见于异步网络连接、异步数据库连接、异步锁：

```python
async with session.get(url) as response:
    text = await response.text()
```

它和普通上下文管理器的统一点是生命周期协议；区别只是进入和退出过程本身需要 `await`。

## 12. 设计上下文管理器的原则

好的上下文管理器应该：

- 进入和退出语义清楚。
- 退出路径可靠，不依赖调用者记忆。
- 异常处理策略明确。
- 默认不吞异常，除非名字和语义明确说明会吞。
- `__exit__` 尽量不抛出会掩盖原始异常的新异常。
- 对外暴露的资源对象清楚。

例如，名字叫 `suppress` 的上下文管理器吞异常是合理的：

```python
with suppress(FileNotFoundError):
    ...
```

但名字叫 `open_resource` 的上下文管理器如果悄悄吞掉所有异常，就非常危险。

## 13. 检查表

遇到上下文管理器问题，按下面问：

1. 进入时需要建立什么资源或状态？
2. 退出时必须释放、恢复、提交还是回滚？
3. 正常退出和异常退出是否不同？
4. `__enter__` 返回什么对象？
5. `__exit__` 是否会吞异常？
6. 如果多个上下文嵌套，进入和退出顺序是否正确？
7. 是否需要 `ExitStack` 动态管理多个资源？
8. 是否应该用 `contextmanager` 简化实现？

最小心智模型：

1. `with` 是资源生命周期协议。
2. `__enter__` 进入上下文并返回 `as` 绑定对象。
3. `__exit__` 负责退出和清理。
4. 异常会传给 `__exit__`。
5. `__exit__` 返回真值会抑制异常。
6. `contextlib` 提供了常见模式的工具化实现。

上下文管理器把“记得清理”变成“结构保证清理”。这就是它真正的价值。
