# `abc` 与 `typing.Protocol`

抽象基类和 `Protocol` 都在表达“对象应该支持什么接口”，但它们的哲学不同。

**`abc` 是显式继承的名义接口；`Protocol` 是结构化接口，关注对象是否拥有所需成员。**

Python 的动态风格更偏向协议和鸭子类型，但在工程代码中，`abc` 和 `Protocol` 都有清晰位置。

## 1. 鸭子类型

Python 传统风格是鸭子类型：

```python
def close_all(resources):
    for resource in resources:
        resource.close()
```

这个函数不关心 `resource` 的类是什么，只关心它能不能 `.close()`。

这很灵活，但大型项目里，接口边界容易不够明确。于是我们需要更清楚的表达工具。

## 2. 抽象基类 `abc`

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def read(self, key: str) -> bytes:
        ...

    @abstractmethod
    def write(self, key: str, data: bytes) -> None:
        ...
```

子类必须实现抽象方法才能实例化：

```python
class FileStorage(Storage):
    def read(self, key: str) -> bytes:
        return b""

    def write(self, key: str, data: bytes) -> None:
        pass

storage = FileStorage()
```

如果漏掉方法：

```python
class BrokenStorage(Storage):
    def read(self, key: str) -> bytes:
        return b""

BrokenStorage()  # TypeError，仍有抽象方法未实现
```

`ABC` 适合你希望实现者明确继承某个接口的场景。

## 3. 抽象方法可以有实现

抽象方法不等于没有代码：

```python
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    @abstractmethod
    def process(self, item):
        # 子类可以通过 super() 复用这里的公共逻辑
        print("common pre-processing")
```

子类仍然必须覆盖它，但可以调用 `super()`：

```python
class Processor(BaseProcessor):
    def process(self, item):
        super().process(item)
        print("real processing", item)
```

这在协作式继承中有用，但要避免把抽象基类写成复杂的半成品框架。

## 4. 标准库中的 ABC

`collections.abc` 提供很多抽象基类：

```python
from collections.abc import Iterable, Sequence, Mapping

def total(xs: Iterable[int]) -> int:
    return sum(xs)
```

它们既可以用于类型标注，也可以用于运行时判断：

```python
from collections.abc import Sequence

print(isinstance([1, 2], Sequence))  # True
```

但不要过度依赖运行时 `isinstance`。很多时候直接调用协议方法更 Pythonic。

## 5. `Protocol`

`Protocol` 表达结构化接口：

```python
from typing import Protocol

class SupportsClose(Protocol):
    def close(self) -> None:
        ...

def cleanup(resource: SupportsClose) -> None:
    resource.close()
```

任何有 `close()` 方法的对象都满足这个协议，不需要显式继承：

```python
class FileLike:
    def close(self) -> None:
        pass

cleanup(FileLike())  # 静态类型检查器认为可接受
```

这更贴近 Python 的鸭子类型：对象像鸭子，不必登记成鸭子。

## 6. Protocol 默认主要用于静态检查

```python
class SupportsRead(Protocol):
    def read(self) -> str:
        ...
```

默认情况下，`Protocol` 不应该被当作普通运行时 `isinstance` 检查工具。

如果确实需要运行时检查，要使用 `@runtime_checkable`：

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None:
        ...

class Resource:
    def close(self) -> None:
        pass

print(isinstance(Resource(), SupportsClose))  # True
```

注意：运行时 protocol 检查通常只检查成员是否存在，不会完整检查函数签名和类型。

## 7. 选择 `abc` 还是 `Protocol`

使用 `abc` 的场景：

- 你控制实现类。
- 你希望实现者显式继承。
- 需要共享部分实现。
- 需要运行时禁止不完整子类实例化。
- 框架需要注册和管理子类。

使用 `Protocol` 的场景：

- 你只关心对象有什么方法，不关心它来自哪个类。
- 你不控制实现类。
- 想表达鸭子类型接口。
- 主要服务静态类型检查。
- 希望降低继承耦合。

例子：

```python
class Repository(Protocol):
    def get_user(self, user_id: str) -> object:
        ...
```

业务服务不需要强迫所有 repository 继承同一个基类，只要结构满足即可。

## 8. Protocol 与组合

`Protocol` 很适合组合式设计：

```python
from typing import Protocol

class Sender(Protocol):
    def send(self, message: str) -> None:
        ...

class Notifier:
    def __init__(self, sender: Sender):
        self.sender = sender

    def notify(self, message: str) -> None:
        self.sender.send(message)
```

`Notifier` 不关心 sender 是邮件、短信、日志还是测试 fake。它只关心 sender 支持 `send`。

这比继承一个巨大基类更轻。

## 9. 抽象不是越多越好

不要提前抽象：

```python
class BaseThing(ABC):
    ...
```

如果只有一个实现、接口还不稳定，抽象层可能只会增加噪声。

更好的节奏：

1. 先写具体代码。
2. 当出现两个以上实现，观察共同接口。
3. 抽出 `Protocol` 或 `ABC`。
4. 让测试验证替换关系。

抽象的目的不是显得架构完整，而是降低依赖和表达边界。

## 10. 检查表

设计接口时，按下面问：

1. 我需要显式继承关系，还是结构化能力？
2. 实现类是否由我控制？
3. 是否需要共享默认实现？
4. 是否需要运行时禁止不完整实现？
5. 是否主要服务类型检查？
6. 是否可以用组合和 `Protocol` 降低耦合？
7. 这个抽象是否已经有多个真实实现？

最小心智模型：

1. 鸭子类型关注对象能做什么。
2. `abc` 表达显式继承接口。
3. `Protocol` 表达结构化接口。
4. `Protocol` 默认主要服务静态检查。
5. `@runtime_checkable` 只提供有限运行时检查。
6. 好抽象来自真实重复，不来自预感。
