# 表示协议

表示协议回答的问题是：一个对象如何变成给人看的文本。

**`repr(obj)` 面向开发者，目标是精确和可调试；`str(obj)` 面向用户，目标是友好和可读；格式化协议则让对象参与 f-string、`format()` 和格式规格。**

这不是“打印时调用哪个魔术方法”的零散知识，而是 Python 把对象暴露给人类读者的统一接口。

## 1. `repr` 与 `str`

两个最常见入口：

```python
value = 3.14

print(repr(value))  # 开发者表示，尽量精确
print(str(value))   # 用户表示，通常更友好
```

自定义对象默认表示通常不够有用：

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

u = User("Alice", 20)
print(u)       # 默认调用 str(u)
print(repr(u)) # 默认表示通常包含类型和地址信息
```

实现 `__repr__`：

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        # 返回值必须是 str；这里展示的是开发者调试时最需要的信息
        return f"User(name={self.name!r}, age={self.age!r})"

u = User("Alice", 20)
print(repr(u))  # User(name='Alice', age=20)
```

`!r` 表示对字段调用 `repr()`，不是 `str()`。字符串字段因此会带引号，更适合调试。

## 2. `__repr__` 的目标

好的 `__repr__` 通常满足：

- 包含类型名。
- 包含重建或识别对象所需的关键字段。
- 避免隐藏歧义。
- 不做昂贵计算。
- 不产生副作用。

例如：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        # 尽量接近构造表达式，读者能看出对象如何产生
        return f"Point({self.x!r}, {self.y!r})"

print(Point(1, 2))  # print 会在没有 __str__ 时回退到 __repr__
```

“可被 `eval` 重新构造”是一个好方向，但不是强制要求。很多对象包含连接、文件句柄、缓存、惰性数据，无法也不应该被 `eval(repr(obj))` 还原。

## 3. `__str__` 的目标

`__str__` 面向用户，更像展示文本：

```python
class Money:
    def __init__(self, cents, currency="USD"):
        self.cents = cents
        self.currency = currency

    def __repr__(self):
        # 开发者表示：展示内部存储单位 cents
        return f"Money(cents={self.cents!r}, currency={self.currency!r})"

    def __str__(self):
        # 用户表示：展示常见金额格式
        return f"{self.currency} {self.cents / 100:.2f}"

m = Money(1234)
print(repr(m))  # Money(cents=1234, currency='USD')
print(str(m))   # USD 12.34
```

如果没有 `__str__`，`str(obj)` 会回退到 `__repr__`。所以很多类型只实现 `__repr__` 就足够。

## 4. 容器为什么使用 `repr`

容器展示元素时通常使用元素的 `repr`：

```python
class Label:
    def __str__(self):
        return "hello"

    def __repr__(self):
        return "Label('hello')"

x = Label()
print(str(x))   # hello
print([x])      # [Label('hello')]
```

列表使用 `repr(element)` 是为了避免歧义。如果列表里有字符串，显示为 `['a']` 比 `[a]` 更清楚。

## 5. f-string 中的 `!r`、`!s`、`!a`

f-string 可以显式选择转换方式：

```python
name = "Alice\nBob"

print(f"{name}")    # 默认使用 str(name)
print(f"{name!s}")  # 显式使用 str(name)
print(f"{name!r}")  # 使用 repr(name)，换行会显示为 \n
print(f"{name!a}")  # 使用 ascii(name)，非 ASCII 会转义
```

调试时常用 `!r`：

```python
def parse(text):
    print(f"parse input: {text!r}")  # 能看见空格、换行、引号等细节
```

现代 Python 还支持 debug f-string：

```python
x = 10
y = 20
print(f"{x=}, {y=}")  # 输出变量名和值，适合临时调试
```

## 6. `__format__`

`format(obj, spec)` 和 f-string 的格式规格会进入 `__format__`：

```python
value = 3.14159
print(format(value, ".2f"))  # 3.14
print(f"{value:.2f}")        # 3.14
```

自定义格式：

```python
class Ratio:
    def __init__(self, numerator, denominator):
        self.numerator = numerator
        self.denominator = denominator

    def __format__(self, spec):
        # spec 是格式规格字符串，例如 ".1%" 或 "fraction"
        value = self.numerator / self.denominator
        if spec == "fraction":
            return f"{self.numerator}/{self.denominator}"
        return format(value, spec)

r = Ratio(1, 4)
print(f"{r:fraction}") # 1/4
print(f"{r:.1%}")      # 25.0%
```

`__format__` 应返回字符串。它适合那些有多个合理展示方式的类型，比如金额、比例、日期、单位值。

## 7. `dataclass` 的表示

`dataclass` 会自动生成实用的 `__repr__`：

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

print(User("Alice", 20))  # User(name='Alice', age=20)
```

可以隐藏敏感字段：

```python
from dataclasses import dataclass, field

@dataclass
class Account:
    username: str
    password: str = field(repr=False)  # password 不出现在自动 __repr__ 中

print(Account("alice", "secret"))  # Account(username='alice')
```

表示协议和安全也有关。日志里泄漏 token、密码、密钥，经常就是 `repr` 设计不谨慎造成的。

## 8. 检查表

设计对象表示时，按下面问：

1. 这个表示是给开发者看，还是给最终用户看？
2. `__repr__` 是否包含定位问题所需的关键信息？
3. `__str__` 是否真的需要不同于 `__repr__`？
4. 字段是否应该用 `!r` 保留歧义信息？
5. 是否可能泄漏敏感信息？
6. 格式化是否需要支持多种规格？

最小心智模型：

1. `repr(obj)` 调用 `obj.__repr__()`。
2. `str(obj)` 优先调用 `obj.__str__()`，没有时回退到 `__repr__()`。
3. f-string 默认走格式化协议。
4. `!r` 强制使用 `repr`，适合调试。
5. 容器展示元素时通常使用元素的 `repr`。
