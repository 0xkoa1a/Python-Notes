# 迭代协议与数据模型

运行时模型里已经讲过 `iter`、`next`、生成器和惰性计算。这里换一个角度：迭代协议如何作为数据模型的一部分，让对象进入 Python 的通用消费生态。

**实现 `__iter__` 的对象，不只是能被 `for` 循环遍历；它还能被 `list()`、`tuple()`、`sum()`、`any()`、`all()`、推导式、解包、`zip()` 等统一消费。**

这就是协议的力量：一个小入口，接入一整套语言能力。

## 1. 协议入口

可迭代对象实现：

```python
def __iter__(self):
    ...
```

迭代器实现：

```python
def __iter__(self):
    return self

def __next__(self):
    ...
```

入口函数：

```python
it = iter(obj)   # 调用 obj.__iter__()
value = next(it) # 调用 it.__next__()
```

`for` 循环、推导式和很多标准库函数都建立在这两个入口之上。

## 2. 可重复遍历的容器

容器对象通常应该让每次 `iter(obj)` 都产生新的迭代器：

```python
class Deck:
    def __init__(self, cards):
        self._cards = list(cards)

    def __iter__(self):
        # 每次调用 __iter__ 都返回一个新的列表迭代器
        return iter(self._cards)

deck = Deck(["A", "K", "Q"])
print(list(deck))  # ['A', 'K', 'Q']
print(list(deck))  # ['A', 'K', 'Q']
```

这类对象像列表、元组、字典一样，可以重复遍历。

如果 `__iter__` 返回 `self`，对象自己就是迭代器，通常只能消费一次：

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        # self 自己保存 current 状态，因此它就是迭代器
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

c = Countdown(3)
print(list(c))  # [3, 2, 1]
print(list(c))  # []
```

设计时要分清：对象表示“数据集合”，还是表示“一次遍历过程”。

## 3. 生成器实现 `__iter__`

很多自定义容器可以用生成器简化：

```python
class Lines:
    def __init__(self, text):
        self._text = text

    def __iter__(self):
        # 这是生成器函数；调用 __iter__ 时返回一个新的生成器对象
        for line in self._text.splitlines():
            if line:
                yield line

lines = Lines("a\n\nb")
print(list(lines))  # ['a', 'b']
```

这种写法同时拥有：

- 容器对象本身可重复遍历。
- 每次遍历的状态由生成器对象保存。
- 代码比手写迭代器类更短。

## 4. 解包也使用迭代协议

解包会消费可迭代对象：

```python
a, b, c = [1, 2, 3]
```

自定义对象也一样：

```python
class Pair:
    def __iter__(self):
        # 解包时会依次从这个迭代器取值
        yield "left"
        yield "right"

x, y = Pair()
print(x, y)  # left right
```

星号解包也基于迭代：

```python
first, *middle, last = range(5)
print(first)   # 0
print(middle)  # [1, 2, 3]
print(last)    # 4
```

`middle` 是列表，因为星号目标会收集中间剩余元素。

## 5. 构造器和聚合函数

这些函数都消费可迭代对象：

```python
list(obj)
tuple(obj)
set(obj)
sum(obj)
any(obj)
all(obj)
max(obj)
min(obj)
```

示例：

```python
class Squares:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        for x in range(self.n):
            yield x * x

squares = Squares(5)

print(list(squares)) # [0, 1, 4, 9, 16]
print(sum(squares))  # 30
```

一次实现 `__iter__`，对象就接入了大量通用函数。

## 6. `reversed` 与 `__reversed__`

`reversed(obj)` 优先调用 `obj.__reversed__()`。如果没有，它会尝试使用 `__len__` 和 `__getitem__` 从后向前取值。

```python
class Timeline:
    def __init__(self, events):
        self._events = list(events)

    def __iter__(self):
        return iter(self._events)

    def __reversed__(self):
        # reversed(timeline) 会调用这里
        return reversed(self._events)

t = Timeline(["start", "middle", "end"])
print(list(reversed(t)))  # ['end', 'middle', 'start']
```

如果反向遍历有更高效的实现，就提供 `__reversed__`。

## 7. 迭代和容器修改

遍历时修改底层容器容易产生不稳定行为：

```python
items = [1, 2, 3, 4]

for x in items:
    if x % 2 == 0:
        items.remove(x)
```

这段代码可能跳过元素，因为迭代器保存的是位置状态，而列表结构被修改了。

更清楚的写法：

```python
items = [1, 2, 3, 4]
items = [x for x in items if x % 2 != 0]
```

或者遍历副本：

```python
for x in list(items):
    if x % 2 == 0:
        items.remove(x)
```

设计自定义容器时也要考虑：迭代期间修改对象，是允许、禁止，还是行为未定义。

## 8. 检查表

设计迭代协议时，按下面问：

1. 对象是可重复遍历的集合，还是一次性的迭代器？
2. `__iter__` 应该返回新迭代器，还是 `self`？
3. 遍历状态保存在哪里？
4. 是否需要 `__reversed__`？
5. 迭代期间修改容器是否允许？
6. 对象是否应该能被解包？
7. 对象接入 `list()`、`sum()`、`any()` 等函数后语义是否自然？

最小心智模型：

1. 迭代协议是数据模型的一部分。
2. `__iter__` 让对象被通用消费。
3. 迭代器保存遍历状态。
4. 容器通常返回新迭代器。
5. 一次性数据流通常让自身成为迭代器。
