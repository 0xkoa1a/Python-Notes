# `property`

`property` 让方法以属性形式暴露。它不是为了把 getter/setter 写成 Java 风格，而是为了在保持属性访问语义的同时，加入计算、校验、兼容和封装。

**`property` 是描述符；读取属性时调用 getter，赋值时调用 setter，删除时调用 deleter。它让公开接口保持 `obj.name`，内部实现可以从裸字段演进为受控访问。**

## 1. 从普通属性开始

Python 中通常先写普通属性：

```python
class User:
    def __init__(self, name):
        self.name = name

u = User("Alice")
print(u.name)
```

不要一开始就为每个字段写 getter/setter。Python 的属性访问已经足够直接。

当你后来需要校验或计算时，可以改成 `property`，调用方仍然写 `u.name`。

## 2. 只读 property

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def area(self):
        # area 是计算属性，不存储在实例字典中
        return 3.14159 * self.radius ** 2

c = Circle(2)
print(c.area)  # 像属性一样访问
```

调用方不写 `c.area()`，因为 `area` 表达的是对象的一个属性，而不是一个命令动作。

没有 setter 时，赋值会失败：

```python
c.area = 10  # AttributeError
```

## 3. 带校验的 setter

```python
class User:
    def __init__(self, name):
        self.name = name  # 这里会调用 setter

    @property
    def name(self):
        # getter 返回对外公开的 name
        return self._name

    @name.setter
    def name(self, value):
        # value 是赋值语句右侧的对象
        if not value:
            raise ValueError("name cannot be empty")
        self._name = value

u = User("Alice")
u.name = "Bob"
```

注意内部字段通常换名为 `_name`，避免 setter 中写 `self.name = value` 造成递归。

错误写法：

```python
class Bad:
    @property
    def name(self):
        return self.name  # 读取 self.name 会再次调用 getter，导致递归
```

## 4. deleter

删除属性时可以触发 deleter：

```python
class Cache:
    def __init__(self):
        self._value = "cached"

    @property
    def value(self):
        return self._value

    @value.deleter
    def value(self):
        # del obj.value 时调用这里
        self._value = None

c = Cache()
del c.value
print(c.value)  # None
```

deleter 不常用，但在缓存失效、资源解绑、受控删除中有价值。

## 5. property 与兼容性演进

一开始是普通属性：

```python
class User:
    def __init__(self, name):
        self.name = name
```

后来你想增加规范化：

```python
class User:
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value.strip().title()
```

调用方仍然使用：

```python
u.name
u.name = " alice "
```

这就是 Python 不鼓励预先写 getter/setter 的原因：需要时可以无痛升级。

## 6. property 不应该隐藏昂贵动作

属性访问通常被认为便宜、无副作用：

```python
user.full_name
circle.area
```

如果一个操作很慢、会访问网络、会写数据库、会改变系统状态，更适合写成方法：

```python
report.generate()
client.fetch_user()
```

一个实用判断：

```text
像“是什么”：property。
像“做什么”：method。
```

当然，计算属性可能有轻微计算，但不应让调用方惊讶。

## 7. 缓存属性

如果计算昂贵但结果稳定，可以使用 `functools.cached_property`：

```python
from functools import cached_property

class DataSet:
    def __init__(self, values):
        self.values = values

    @cached_property
    def mean(self):
        # 第一次访问时计算，结果会写入实例字典
        return sum(self.values) / len(self.values)

d = DataSet([1, 2, 3])
print(d.mean) # 第一次计算
print(d.mean) # 后续读取缓存值
```

`cached_property` 会把计算结果缓存到实例上。如果底层数据会变，要考虑缓存失效问题：

```python
del d.mean  # 删除缓存，下次访问会重新计算
```

## 8. property 和描述符

`property` 是数据描述符，保存在类对象上：

```python
class User:
    @property
    def name(self):
        return "Alice"

print(User.__dict__["name"])  # property 对象
```

访问 `u.name` 时，不是去调用实例字典里的函数，而是类上的 `property` 描述符接管访问。

这解释了为什么 property 能拦截读取和赋值，也解释了为什么它能优先于实例字典。

## 9. 检查表

设计 property 时，按下面问：

1. 这个成员表达的是对象状态，还是动作？
2. 读取是否应该便宜、稳定、无副作用？
3. 是否需要校验赋值？
4. 内部存储名是否避免递归？
5. 是否需要 deleter？
6. 是否需要缓存？如果缓存，什么时候失效？
7. 是否只是机械模仿 getter/setter？如果是，普通属性更好。

最小心智模型：

1. `property` 是描述符。
2. getter 处理读取。
3. setter 处理赋值。
4. deleter 处理删除。
5. property 让公开属性接口和内部实现解耦。
