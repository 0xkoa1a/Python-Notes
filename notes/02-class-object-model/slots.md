# `slots`

`__slots__` 是控制实例属性存储方式的工具。普通实例通常用 `__dict__` 存属性，`slots` 则让类声明固定的一组实例属性名。

**`__slots__` 的核心作用是：限制实例可拥有的属性，并避免为每个实例创建普通 `__dict__`，从而节省内存。**

它不是“让类更高级”的装饰，也不是默认优化项。只有在对象数量很多或需要限制属性时才值得考虑。

## 1. 普通实例有 `__dict__`

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.__dict__)  # {'x': 1, 'y': 2}

p.z = 3
print(p.__dict__)  # {'x': 1, 'y': 2, 'z': 3}
```

普通实例可以动态新增属性，因为实例有字典。

## 2. 定义 `__slots__`

```python
class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x, p.y)

p.z = 3  # AttributeError
```

`__slots__` 声明实例允许拥有的属性名。没有列出的属性不能赋值。

通常 slotted 实例没有 `__dict__`：

```python
hasattr(p, "__dict__")  # False
```

## 3. `slots` 节省什么

普通实例为每个对象准备一个字典，灵活但有内存成本。`slots` 用固定槽位保存属性，减少每个实例的存储开销。

适合场景：

- 会创建大量小对象。
- 属性集合固定。
- 不需要动态加属性。
- 想更早发现拼写错误。

例如几百万个点、词法 token、AST 节点、几何对象等。

不适合场景：

- 对象属性经常动态变化。
- 框架需要写入额外属性。
- 你依赖 `obj.__dict__`。
- 只是为了“看起来更专业”。

## 4. `slots` 和类属性

不要把 slot 名和类属性默认值混在一起：

```python
class Bad:
    __slots__ = ("x",)
    x = 1  # 冲突：x 已经被 slot 描述符占用
```

slot 名会在类上创建描述符，用来管理实例槽位。因此同名类属性会冲突。

正确做法是在 `__init__` 中赋值：

```python
class Good:
    __slots__ = ("x",)

    def __init__(self):
        self.x = 1
```

## 5. 继承中的 `slots`

如果基类没有 `__slots__`，子类即使定义 slots，实例通常仍会有 `__dict__`：

```python
class Base:
    pass

class Child(Base):
    __slots__ = ("x",)

c = Child()
c.y = 1  # 可能允许，因为 Base 提供了 __dict__
```

要真正移除实例字典，继承链中的类都要配合。

```python
class Base:
    __slots__ = ()

class Child(Base):
    __slots__ = ("x",)
```

`__slots__ = ()` 表示这个类不新增实例槽位，也不创建 `__dict__`。

## 6. 需要弱引用时

普通对象通常可以被弱引用。slotted 对象如果需要弱引用，要显式加入 `__weakref__`：

```python
import weakref

class Point:
    __slots__ = ("x", "y", "__weakref__")

    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
r = weakref.ref(p)  # 可以
```

`__weakref__` 是让实例支持弱引用的特殊槽位。

## 7. dataclass 与 slots

现代 dataclass 可以直接生成 slots：

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
p.z = 3  # AttributeError
```

如果你已经在用 dataclass，并且对象数量很多，`slots=True` 是比手写 `__slots__` 更整洁的选择。

也可以组合不可变值对象：

```python
@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int
```

这常用于大量小型值对象。

## 8. `slots` 不是访问控制

`slots` 限制属性集合，但不是安全边界：

```python
class User:
    __slots__ = ("name",)
```

这并不表示 `name` 是私有或安全的。它只是改变存储布局和属性限制。

如果需要表达只读，考虑 `property`、`frozen=True` dataclass，或者明确 API 约定。

## 9. 检查表

使用 slots 前，按下面问：

1. 是否会创建大量实例？
2. 属性集合是否固定？
3. 是否需要动态新增属性？
4. 是否依赖 `__dict__`？
5. 继承链上的类是否都配合 slots？
6. 是否需要弱引用？如果需要，是否加入 `__weakref__`？
7. 是否可以用 `@dataclass(slots=True)` 更清楚地表达？

最小心智模型：

1. 普通实例属性存在 `__dict__` 中。
2. `__slots__` 声明固定属性槽位。
3. slots 可以节省大量小对象的内存。
4. slots 限制动态属性，但不是访问控制。
5. 继承中 slots 需要整条链一起考虑。
