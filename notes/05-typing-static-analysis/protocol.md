# `Protocol`

`Protocol` 解决的问题是：我们想表达“只要对象有这些方法和属性，就可以用”，而不要求它继承某个基类。

**`Protocol` 是静态类型系统中的结构化接口；它把 Python 的鸭子类型写成可检查的接口边界。**

这和运行时的协议式编程一致：对象能做什么，比对象名义上是什么更重要。

## 1. 最小 Protocol

```python
from typing import Protocol

class SupportsClose(Protocol):
    def close(self) -> None:
        ...

def cleanup(resource: SupportsClose) -> None:
    resource.close()
```

任何有 `close()` 方法的对象都满足：

```python
class FileLike:
    def close(self) -> None:
        pass

cleanup(FileLike())
```

`FileLike` 不需要继承 `SupportsClose`。

## 2. 属性也可以在 Protocol 中声明

```python
from typing import Protocol

class Named(Protocol):
    name: str

def display(obj: Named) -> str:
    return obj.name
```

任何有 `name: str` 属性的对象都可接受。

如果属性只读，可以用 property：

```python
class HasId(Protocol):
    @property
    def id(self) -> str:
        ...
```

## 3. Protocol 和 abc 的区别

`abc`：

```python
class Storage(ABC):
    ...
```

要求实现者显式继承，偏名义类型。

`Protocol`：

```python
class Storage(Protocol):
    ...
```

不要求继承，偏结构类型。

使用判断：

- 你控制所有实现，并需要共享实现：`abc`。
- 你只关心能力，不控制实现：`Protocol`。
- 你想给鸭子类型加静态检查：`Protocol`。

## 4. 运行时检查

默认 `Protocol` 主要给静态检查器使用。若需要 `isinstance`，必须加 `runtime_checkable`：

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

运行时检查只看结构存在，不完整检查类型签名。因此它不能替代静态检查。

## 5. Protocol 适合依赖注入

```python
from typing import Protocol

class UserRepository(Protocol):
    def get_name(self, user_id: str) -> str:
        ...

class UserService:
    def __init__(self, repository: UserRepository):
        # repository 可以是真实数据库实现，也可以是测试 fake
        self.repository = repository

    def greet(self, user_id: str) -> str:
        return f"hello {self.repository.get_name(user_id)}"
```

测试 fake：

```python
class FakeRepository:
    def get_name(self, user_id: str) -> str:
        return "Alice"
```

没有继承关系，但结构满足。

## 6. 小 Protocol 优于大接口

坏接口：

```python
class Repository(Protocol):
    def create_user(self): ...
    def delete_user(self): ...
    def list_users(self): ...
    def create_team(self): ...
    def delete_team(self): ...
```

更好：

```python
class UserReader(Protocol):
    def get_user(self, user_id: str) -> User:
        ...
```

函数需要什么能力，就依赖什么能力。接口越小，替换越容易。

## 7. 检查表

使用 `Protocol` 时，按下面问：

1. 我关心的是继承关系，还是结构能力？
2. 这个接口是否足够小？
3. 实现类是否由我控制？
4. 是否主要用于静态检查？
5. 是否真的需要运行时 `isinstance`？
6. Protocol 中属性是否应该只读？

最小心智模型：

1. `Protocol` 是结构化接口。
2. 实现类不需要继承它。
3. 它把鸭子类型变成可检查边界。
4. 默认服务静态检查。
5. 小协议比大接口更灵活。
