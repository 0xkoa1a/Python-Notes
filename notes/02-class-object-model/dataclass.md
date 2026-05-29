# `dataclass`

`dataclass` 解决的是“数据对象样板代码太多”的问题。它不是新的对象模型，而是类装饰器，根据字段声明生成常见方法。

**`dataclass` 把字段声明变成 `__init__`、`__repr__`、`__eq__` 等方法；它适合表达以数据为中心、行为相对简单的值对象或记录对象。**

## 1. 最小 dataclass

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

u = User("Alice", 20)
print(u)  # User(name='Alice', age=20)
```

`@dataclass` 会读取类上的类型标注，把它们当作字段，并生成：

- `__init__`
- `__repr__`
- `__eq__`

默认情况下，它不会让类型标注变成运行时类型检查。

```python
u = User("Alice", "not an int")  # 默认可以运行
```

类型标注主要服务读者、IDE 和静态检查器。

## 2. 字段默认值

```python
@dataclass
class User:
    name: str
    role: str = "guest"

print(User("Alice"))  # User(name='Alice', role='guest')
```

有默认值的字段要放在无默认值字段后面，规则和函数参数类似。

## 3. `default_factory`

可变默认值要用 `default_factory`：

```python
from dataclasses import dataclass, field

@dataclass
class Team:
    members: list[str] = field(default_factory=list)

a = Team()
b = Team()

a.members.append("Alice")
print(b.members)  # []
```

`default_factory=list` 表示每次创建实例时调用 `list()` 生成新列表。

不要写：

```python
@dataclass
class BadTeam:
    members: list[str] = []  # dataclass 会拒绝常见可变默认值
```

这和函数默认参数、类可变属性背后的模型一致：默认对象如果共享，就会共享可变状态。

## 4. `field`

`field` 可以控制字段行为：

```python
from dataclasses import dataclass, field

@dataclass
class Account:
    username: str
    password: str = field(repr=False) # 不出现在 __repr__ 中
    id: int = field(compare=False)    # 不参与 __eq__ 比较
```

常用参数：

- `default`
- `default_factory`
- `repr`
- `compare`
- `init`
- `kw_only`

示例：

```python
@dataclass
class Item:
    name: str
    normalized: str = field(init=False)

    def __post_init__(self):
        # __post_init__ 在自动生成的 __init__ 之后调用
        self.normalized = self.name.strip().lower()
```

## 5. `__post_init__`

当初始化后需要校验或派生字段，用 `__post_init__`：

```python
@dataclass
class Rectangle:
    width: float
    height: float

    def __post_init__(self):
        # self 已经拥有 width 和 height 字段
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
```

`__post_init__` 适合建立不变量。不要把大量业务逻辑塞进去。

## 6. `frozen=True`

不可变值对象：

```python
@dataclass(frozen=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
p.x = 3  # dataclasses.FrozenInstanceError
```

`frozen=True` 会阻止普通属性赋值，并且在合适情况下生成哈希：

```python
points = {Point(1, 2)}
```

这适合用作字典键、集合元素、配置值、领域值对象。

注意：`frozen=True` 是浅层不可变。如果字段本身是可变对象，内部对象仍可能被修改。

```python
@dataclass(frozen=True)
class Box:
    items: list[int]

b = Box([])
b.items.append(1)  # 可以，修改的是列表对象内部
```

## 7. `order=True`

生成排序方法：

```python
@dataclass(order=True)
class Version:
    major: int
    minor: int

print(Version(3, 10) < Version(3, 11))  # True
```

排序按字段顺序进行，类似元组比较：

```python
(major, minor)
```

只有对象存在自然顺序时才使用 `order=True`。如果排序只是某次操作需要，用 `key` 更清楚。

## 8. dataclass 适合什么

适合：

- 配置对象。
- 命令参数对象。
- 简单领域值对象。
- 测试数据结构。
- 函数返回的结构化结果。

不适合：

- 需要复杂不变量和大量行为的对象。
- 需要运行时类型验证的边界对象。
- 需要 ORM 生命周期管理的实体。
- 隐藏大量副作用的服务类。

如果你需要运行时数据验证，Pydantic 可能更适合。如果你需要持久化映射，ORM 模型可能更适合。

## 9. 检查表

使用 dataclass 时，按下面问：

1. 这个类是否主要承载数据？
2. 字段默认值是否可变？如果可变，是否用了 `default_factory`？
3. 是否需要 `__post_init__` 建立不变量？
4. 是否应该 `frozen=True`？
5. 字段是否都应该出现在 `repr` 中？
6. 字段是否都应该参与相等比较？
7. 对象是否真的有自然排序？
8. 是否需要运行时类型验证？如果需要，dataclass 默认不提供。

最小心智模型：

1. `dataclass` 是类装饰器。
2. 它根据字段生成样板方法。
3. 类型标注默认不强制运行时类型。
4. `default_factory` 用于每实例创建默认可变对象。
5. `frozen=True` 表达值对象倾向。
6. dataclass 适合数据中心类，不适合所有类。
