# 容器协议

容器协议回答的问题是：对象如何表现得像一个集合、序列或映射。

**`in`、索引、切片、赋值、删除、遍历等语法并不是只属于内置容器；它们会调用对象实现的容器协议。**

理解容器协议，就能理解为什么 `list`、`tuple`、`dict`、字符串、Pandas 对象、自定义集合都能接入相似的语法。

## 1. `in` 与 `__contains__`

表达式：

```python
x in container
```

优先调用：

```python
container.__contains__(x)
```

示例：

```python
class NameSet:
    def __init__(self, names):
        self._names = set(names)

    def __contains__(self, name):
        # name 是 in 左侧传入的对象
        return name.lower() in self._names

names = NameSet({"alice", "bob"})
print("Alice" in names)  # True
```

`__contains__` 应返回布尔值或可转成布尔值的对象。为了清楚，建议直接返回 `True` / `False`。

如果没有 `__contains__`，Python 会尝试迭代对象并逐个比较：

```python
class Numbers:
    def __iter__(self):
        yield 1
        yield 2
        yield 3

print(2 in Numbers())  # True
```

## 2. 索引与 `__getitem__`

表达式：

```python
obj[key]
```

会调用：

```python
obj.__getitem__(key)
```

对序列来说，`key` 通常是整数：

```python
class Words:
    def __init__(self, text):
        self._words = text.split()

    def __getitem__(self, index):
        # index 是方括号里的对象，通常是 int 或 slice
        return self._words[index]

w = Words("python object protocol")
print(w[0])  # python
```

对映射来说，`key` 可以是任意可哈希对象：

```python
class Env:
    def __init__(self, data):
        self._data = dict(data)

    def __getitem__(self, key):
        # key 是映射键，不要求是整数
        return self._data[key]

env = Env({"PATH": "/bin"})
print(env["PATH"])  # /bin
```

## 3. 切片也是 key

切片语法：

```python
obj[start:stop:step]
```

传给 `__getitem__` 的是 `slice` 对象：

```python
class DebugSeq:
    def __getitem__(self, key):
        # key 可能是 int，也可能是 slice
        print(repr(key))

seq = DebugSeq()
seq[1]       # 1
seq[1:5:2]   # slice(1, 5, 2)
```

支持切片：

```python
class Words:
    def __init__(self, text):
        self._words = text.split()

    def __getitem__(self, key):
        if isinstance(key, slice):
            # key.indices 可把 None 和负数归一化到给定长度
            return Words(" ".join(self._words[key]))
        return self._words[key]

    def __repr__(self):
        return f"Words({self._words!r})"

w = Words("a b c d")
print(w[1:3])  # Words(['b', 'c'])
```

切片不是特殊语法分支，它只是构造了一个 `slice` 对象作为 key。

## 4. 赋值与删除

索引赋值：

```python
obj[key] = value
```

调用：

```python
obj.__setitem__(key, value)
```

删除：

```python
del obj[key]
```

调用：

```python
obj.__delitem__(key)
```

示例：

```python
class Store:
    def __init__(self):
        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        # key 和 value 分别来自 obj[key] = value 的两侧
        self._data[key] = value

    def __delitem__(self, key):
        # key 来自 del obj[key]
        del self._data[key]

s = Store()
s["x"] = 1
print(s["x"])  # 1
del s["x"]
```

如果对象不支持修改，就不要实现 `__setitem__` 和 `__delitem__`，或者明确抛出 `TypeError`。

## 5. `len` 与容器大小

容器通常实现 `__len__`：

```python
class Store:
    def __init__(self, data):
        self._data = dict(data)

    def __len__(self):
        # len(store) 调用这里；返回非负整数
        return len(self._data)

print(len(Store({"a": 1})))  # 1
```

`__len__` 也影响布尔判断：

```python
empty = Store({})
print(bool(empty))  # False
```

除非你实现了 `__bool__` 覆盖它。

## 6. 没有 `__iter__` 时的旧式迭代

如果对象没有 `__iter__`，但有从 `0` 开始的 `__getitem__`，Python 可以通过连续索引进行迭代，直到 `IndexError`。

```python
class OldSeq:
    def __init__(self, items):
        self._items = list(items)

    def __getitem__(self, index):
        # for 循环会依次尝试 index=0, 1, 2...
        return self._items[index]

for x in OldSeq(["a", "b"]):
    print(x)
```

这个兼容行为解释了为什么某些只实现 `__getitem__` 的对象也能被迭代。但现代自定义容器更建议显式实现 `__iter__`。

## 7. 序列与映射的设计差异

相同的 `__getitem__` 可以表达序列，也可以表达映射。区别在 API 语义：

```python
seq[0]       # 序列：位置
mapping[key] # 映射：键
```

设计对象时要让 key 的含义稳定清楚。不要让同一个对象既像列表又像字典，除非领域模型真的需要。

可以继承抽象基类帮助补全行为：

```python
from collections.abc import Sequence

class Words(Sequence):
    def __init__(self, text):
        self._words = text.split()

    def __getitem__(self, index):
        return self._words[index]

    def __len__(self):
        return len(self._words)

w = Words("a b c")
print("b" in w)       # Sequence 根据 __iter__/__getitem__ 提供成员测试
print(w.index("c"))   # Sequence 混入的方法
```

`Sequence` 不是必须继承的基类，但它能让“这是序列”这件事在类型和文档上更清楚。

## 8. 检查表

设计容器协议时，按下面问：

1. 这个对象是序列、映射、集合，还是领域特定容器？
2. `in` 应该走快速查找，还是迭代比较？
3. `obj[key]` 中的 key 是位置、键，还是切片？
4. 是否支持修改？如果不支持，不要假装支持。
5. `len(obj)` 是否便宜且稳定？
6. 是否需要显式 `__iter__`？
7. 是否应该继承 `Sequence`、`Mapping`、`MutableMapping` 等抽象基类？

最小心智模型：

1. `x in obj` 调用成员协议。
2. `obj[key]` 调用 `__getitem__`。
3. 切片是 `slice` 对象。
4. `obj[key] = value` 调用 `__setitem__`。
5. `del obj[key]` 调用 `__delitem__`。
6. 容器协议让自定义对象进入 Python 的通用语法生态。
