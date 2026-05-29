# 比较与哈希协议

比较与哈希协议回答的问题是：对象如何判断相等、如何排序、如何作为字典键或集合元素。

**`==` 调用相等协议；排序调用富比较协议；哈希表调用 `__hash__`；可哈希对象必须保证相等对象拥有相同哈希值。**

这里最容易出问题的地方是：把“值相等”“身份相同”“可变性”“哈希稳定性”混在一起。

## 1. 相等性：`__eq__`

表达式：

```python
a == b
```

会尝试调用相等协议：

```python
a.__eq__(b)
```

示例：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        # other 是 == 右侧传入的对象
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

p1 = Point(1, 2)
p2 = Point(1, 2)

print(p1 == p2)  # True
print(p1 is p2)  # False
```

`is` 仍然比较身份，`==` 比较你定义的值语义。

## 2. `NotImplemented`

当不知道如何比较另一个类型时，应返回 `NotImplemented`，不是抛异常，也不是返回 `False`。

```python
class Point:
    def __eq__(self, other):
        if not isinstance(other, Point):
            # NotImplemented 告诉 Python：让右侧对象也尝试处理
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
```

`NotImplemented` 是一个特殊单例对象。它不是异常。返回它后，Python 可以尝试反向比较：

```python
other.__eq__(self)
```

如果双方都无法处理，最终结果通常是 `False`。

## 3. 排序：富比较方法

常见比较方法：

- `__lt__`：小于 `<`
- `__le__`：小于等于 `<=`
- `__gt__`：大于 `>`
- `__ge__`：大于等于 `>=`
- `__eq__`：等于 `==`
- `__ne__`：不等于 `!=`

示例：

```python
class Version:
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) < (other.major, other.minor)

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) == (other.major, other.minor)

versions = [Version(3, 11), Version(3, 10)]
print(sorted(versions))  # 需要 __repr__ 才会显示得更友好
```

排序通常只需要 `__lt__`。但如果对象要完整支持比较，最好保持所有比较语义一致。

## 4. `functools.total_ordering`

可以用 `total_ordering` 根据 `__eq__` 和一个排序方法补全其他比较：

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) == (other.major, other.minor)

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) < (other.major, other.minor)
```

`total_ordering` 让代码少一些，但生成的方法多一层调用。性能极端敏感时可以手写。

`total_ordering` 通过布尔逻辑组合实现，是用来补全“布尔比较”的。Project 2 中的 `Field` 类不可以用 `total_ordering`，因为它返回的是一个延迟执行的查询对象，不是布尔值。

## 5. 哈希：`__hash__`

对象能否放进 `set` 或作为 `dict` key，取决于它是否可哈希：

```python
d = {}
d["name"] = "Alice"
d[(1, 2)] = "point"
```

列表不可哈希：

```python
d[[1, 2]] = "bad"  # TypeError
```

因为列表可变，内容变了以后哈希值也应该变，但字典要求键的哈希在生命周期内稳定。

自定义哈希：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        # 哈希应基于与 __eq__ 相同的字段
        return hash((self.x, self.y))

p = Point(1, 2)
print({p})
```

核心契约：

**如果 `a == b`，那么 `hash(a) == hash(b)` 必须成立。反过来不要求成立。**

不同对象可以有哈希冲突，字典和集合会再用相等性判断确认。

## 6. 可变对象不要轻易可哈希

坏例子：

```python
class BadKey:
    def __init__(self, items):
        self.items = list(items)

    def __eq__(self, other):
        return isinstance(other, BadKey) and self.items == other.items

    def __hash__(self):
        return hash(tuple(self.items))

k = BadKey([1, 2])
d = {k: "value"}

k.items.append(3)  # 修改了参与哈希的内部状态
print(d.get(k))    # 结果可能让人困惑
```

对象作为字典键后，参与哈希和相等性的状态不应该改变。否则键可能落在哈希表的旧位置，后续查找失效。

如果对象是可变值对象，通常让它不可哈希更安全：

```python
class MutablePoint:
    __hash__ = None  # 明确声明不可哈希
```

## 7. 重写 `__eq__` 对 `__hash__` 的影响

如果自定义类重写了 `__eq__`，但没有定义 `__hash__`，Python 会默认把 `__hash__` 设为 `None`，让对象不可哈希。

```python
class User:
    def __eq__(self, other):
        return isinstance(other, User)

u = User()
hash(u)  # TypeError
```

这是为了避免“值相等但哈希仍按身份”的危险不一致。

如果你确实想保留身份哈希和身份相等，就不要重写 `__eq__`。如果你定义值相等，就认真定义匹配的哈希，或者明确不可哈希。

## 8. `dataclass` 的比较与哈希

`dataclass` 会根据参数生成比较和哈希行为：

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

print(Point(1, 2) == Point(1, 2))  # True
```

默认可变 dataclass 不可哈希：

```python
p = Point(1, 2)
hash(p)  # TypeError
```

不可变 dataclass 可以安全生成哈希：

```python
@dataclass(frozen=True)
class FrozenPoint:
    x: int
    y: int

print(hash(FrozenPoint(1, 2)))
```

`frozen=True` 表达：对象创建后字段不应再改变，因此适合作为值对象和哈希键。

## 9. 排序 key 常常比比较方法更合适

不一定每个对象都要实现排序协议。很多时候排序只是某次操作的需求：

```python
users = [
    {"name": "Alice", "age": 20},
    {"name": "Bob", "age": 18},
]

users.sort(key=lambda user: user["age"])  # key 函数返回排序依据
```

如果对象天然有全局顺序，实现 `__lt__` 合理。比如版本号、日期、路径。

如果只是某个视角下排序，用 `key` 更清楚。比如用户可以按年龄、名字、注册时间排序，没有唯一自然顺序。

## 10. 检查表

设计比较和哈希时，按下面问：

1. 对象的相等性是身份相等，还是值相等？
2. `__eq__` 处理不了别的类型时是否返回 `NotImplemented`？
3. 是否存在自然排序？如果没有，是否应该用排序 key？
4. 相等用哪些字段，哈希是否使用同一组字段？
5. 对象是否可变？可变字段是否参与哈希？
6. 是否应该显式 `__hash__ = None`？
7. dataclass 的 `frozen`、`eq`、`order` 参数是否匹配语义？

最小心智模型：

1. `==` 走相等协议，不是身份比较。
2. `is` 始终比较身份。
3. 排序走富比较协议或 key 函数。
4. 可哈希对象需要稳定哈希。
5. 相等对象必须有相同哈希。
6. 可变值对象通常不应该可哈希。
