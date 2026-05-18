# 泛型

泛型解决的问题是：一个函数或类可以处理多种类型，但输入和输出之间存在稳定关系。

**泛型不是“任意类型都行”的模糊表达，而是把类型之间的关系保留下来。**

比如 `list[int]` 和 `list[str]` 都是列表，但取出来的元素类型不同。泛型让检查器知道这种关系。

## 1. 为什么需要泛型

没有泛型：

```python
from typing import Any

def first(items: list[Any]) -> Any:
    return items[0]
```

调用：

```python
x = first([1, 2, 3])
```

静态检查器只知道 `x` 是 `Any`，后续检查变弱。

使用泛型：

```python
def first[T](items: list[T]) -> T:
    return items[0]
```

含义：输入列表元素是什么类型，返回值就是什么类型。

如果你的 Python 版本或工具暂不支持新语法，可以用老写法：

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]
```

## 2. `TypeVar`

`TypeVar` 表示类型变量：

```python
from typing import TypeVar

T = TypeVar("T")

def identity(value: T) -> T:
    return value
```

调用：

```python
a = identity(1)       # T 被推断为 int
b = identity("text")  # T 被推断为 str
```

`T` 的关键不是“任意类型”，而是同一次调用中所有 `T` 必须一致。

## 3. 泛型类

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def get(self) -> T:
        return self.value

int_box = Box[int](1)
text_box = Box[str]("hello")
```

`Box[int]` 表示这个盒子里保存 `int`。`get()` 返回的也是 `int`。

现代 Python 也有更简洁的类泛型语法，但很多代码库仍使用 `Generic[T]`，需要能读懂。

## 4. 多个类型变量

```python
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")

def get_or_default(mapping: dict[K, V], key: K, default: V) -> V:
    return mapping.get(key, default)
```

这里表达：

- `key` 的类型要和字典键类型一致。
- `default` 的类型要和值类型一致。
- 返回值类型和值类型一致。

泛型的价值在于保存这些关系。

## 5. 受限 TypeVar

```python
from typing import TypeVar

AnyStr = TypeVar("AnyStr", str, bytes)

def concat(a: AnyStr, b: AnyStr) -> AnyStr:
    return a + b
```

这表示 `a` 和 `b` 要么都是 `str`，要么都是 `bytes`。不能一个是 `str`，一个是 `bytes`。

## 6. 上界 bound

```python
from typing import TypeVar

class SupportsClose:
    def close(self) -> None:
        ...

TClose = TypeVar("TClose", bound=SupportsClose)

def close_and_return(resource: TClose) -> TClose:
    resource.close()
    return resource
```

`bound` 表示类型变量必须是某个上界的子类型。函数既能调用 `close()`，又能保持具体返回类型。

## 7. 泛型不是运行时容器检查

```python
xs: list[int] = [1, 2, 3]
```

运行时 `xs` 仍是普通 list：

```python
print(type(xs))  # <class 'list'>
```

不要期待 `list[int]` 自动阻止你 append 字符串：

```python
xs.append("bad")  # 运行时可能成功，静态检查器会报错
```

泛型主要是静态约束。

## 8. 检查表

使用泛型时，按下面问：

1. 输入和输出之间是否有类型关系？
2. `Any` 是否丢失了本可保留的信息？
3. 同一个 `TypeVar` 是否表示同一次调用中类型一致？
4. 是否需要多个类型变量？
5. 是否需要受限类型或上界？
6. 是否误以为泛型会做运行时检查？

最小心智模型：

1. 泛型保存类型关系。
2. `TypeVar` 表示可推断的类型变量。
3. 同一个 `T` 在同一次调用中保持一致。
4. 泛型类把类型参数绑定到实例接口上。
5. 泛型默认服务静态检查，不改变容器运行时行为。
