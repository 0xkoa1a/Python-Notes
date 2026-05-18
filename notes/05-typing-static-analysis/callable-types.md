# `Callable`

`Callable` 用来标注“可以被调用的对象”。它不仅包括函数，也包括实现了 `__call__` 的对象、绑定方法、`functools.partial` 等。

**`Callable[[参数类型...], 返回类型]` 描述调用入口；它表达的是调用签名，而不是对象必须是函数。**

这和前面的调用协议是同一件事：类型系统给调用协议加了一层静态描述。

## 1. 最小 Callable

```python
from collections.abc import Callable

def apply(fn: Callable[[int], str], value: int) -> str:
    # fn 是一个可调用对象，接收 int，返回 str
    return fn(value)

def to_text(x: int) -> str:
    return str(x)

print(apply(to_text, 42))
```

`Callable[[int], str]` 表示：

- 调用时传一个 `int`。
- 返回 `str`。

## 2. 多参数 Callable

```python
from collections.abc import Callable

Combiner = Callable[[str, str], str]

def combine(a: str, b: str, op: Combiner) -> str:
    return op(a, b)
```

调用：

```python
def join_with_space(a: str, b: str) -> str:
    return f"{a} {b}"

combine("hello", "world", join_with_space)
```

## 3. 任意参数 Callable

```python
from collections.abc import Callable
from typing import Any

Callback = Callable[..., Any]
```

`...` 表示不检查参数列表。它适合非常动态的回调边界，但会降低类型检查精度。

如果知道签名，尽量写清楚：

```python
Callable[[Event], None]
```

比：

```python
Callable[..., None]
```

更有用。

## 4. Callable 和可调用对象

```python
class Prefixer:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def __call__(self, text: str) -> str:
        # __call__ 让实例满足 Callable[[str], str]
        return self.prefix + text

def transform(text: str, fn: Callable[[str], str]) -> str:
    return fn(text)

print(transform("world", Prefixer("hello ")))
```

类型系统关心对象能否按签名调用，不关心它是不是函数对象。

## 5. Callable 的局限

`Callable` 无法很好表达：

- 关键字-only 参数。
- 参数名要求。
- 重载签名。
- 带属性的可调用对象。

如果需要更精细的可调用接口，用 `Protocol`：

```python
from typing import Protocol

class Parser(Protocol):
    name: str

    def __call__(self, text: str, *, strict: bool = False) -> object:
        ...
```

这里 `Parser` 表示：对象既要可调用，又要有 `name` 属性。

## 6. 装饰器类型的难点

简单装饰器：

```python
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")

def trace(fn: Callable[..., T]) -> Callable[..., T]:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # args/kwargs 是转发给原函数的动态参数
        print("call", fn.__name__)
        return fn(*args, **kwargs)

    return wrapper
```

这保留返回类型 `T`，但丢失了参数签名。更精确的装饰器类型需要 `ParamSpec`：

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def trace(fn: Callable[P, R]) -> Callable[P, R]:
    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # P.args/P.kwargs 表示原函数的位置参数和关键字参数形状
        print("call", fn.__name__)
        return fn(*args, **kwargs)

    return wrapper
```

`ParamSpec` 保存参数列表关系，`TypeVar` 保存返回值关系。

## 7. 检查表

标注可调用对象时，按下面问：

1. 这个参数是函数，还是任意可调用对象？
2. 参数类型和返回类型能否写清楚？
3. 是否用了 `Callable[..., Any]` 逃避约束？
4. 是否需要表达关键字-only 参数或属性？
5. 装饰器是否需要保留原函数参数签名？
6. 是否应该用 `Protocol` 或 `ParamSpec`？

最小心智模型：

1. `Callable` 标注调用协议。
2. 它不要求对象是函数。
3. `Callable[[A, B], R]` 表示两个参数和返回值。
4. `Callable[..., R]` 放弃参数检查。
5. 复杂可调用接口用 `Protocol`。
6. 装饰器保留签名用 `ParamSpec`。
