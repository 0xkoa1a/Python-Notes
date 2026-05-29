# 迭代运行时与生成器

Python 的 `for` 循环不是“只能遍历列表”的语法糖。它背后是一套运行时模型：`iter(obj)` 取得迭代器，`next(it)` 推动迭代器前进，生成器把函数调用变成可暂停、可恢复的数据流。

**一个对象只要能被 `iter(obj)` 转换为迭代器，就能被 `for`、推导式、`list()`、`tuple()`、`sum()`、`any()`、`all()` 等消费。**

这一章重点放在运行时：迭代器如何保存状态、生成器如何暂停和恢复、惰性流水线为什么能成立。自定义类型如何完整实现 `__iter__`、`__next__`、`__reversed__` 等数据模型入口，会在第三章“自定义类型的迭代协议”中展开。

## 1. 可迭代对象与迭代器

两个概念必须分开：

- 可迭代对象：能被 `iter(obj)` 调用的对象。
- 迭代器：能被 `next(it)` 不断取出元素的对象。

列表是可迭代对象：

```python
xs = [1, 2, 3]
it = iter(xs)

print(next(it))  # 1
print(next(it))  # 2
print(next(it))  # 3
```

取完后再取：

```python
next(it)  # StopIteration
```

迭代器协议包括两个方法：

```python
class IteratorLike:
    def __iter__(self):
        return self    # 直接返回自己

    def __next__(self):
        ...
```

可迭代对象协议通常是：

```python
class IterableLike:
    def __iter__(self):
        return some_iterator
```

关键区别：

**可迭代对象负责产生迭代器；迭代器负责保存遍历状态并逐个产出元素。**

**迭代器必须也是可迭代对象**，这样才能让 for 循环可以一视同仁地处理“容器”和“迭代器本身”。

## 2. `for` 循环的真实模型

这段代码：

```python
for x in xs:
    print(x)
```

大致等价于：

```python
it = iter(xs)

while True:
    try:
        x = next(it)
    except StopIteration:
        break
    print(x)
```

所以 `for` 循环不关心对象是不是列表。它只关心：

1. `iter(xs)` 能否得到迭代器。
2. `next(it)` 能否不断返回下一个元素。
3. 结束时是否抛出 `StopIteration`。

这就是为什么这些对象都能放进 `for`：

```python
for x in [1, 2, 3]:
    ...

for ch in "abc":
    ...

for key in {"a": 1, "b": 2}:
    ...

for line in open("data.txt"):
    ...
```

它们不是共享某个继承基类，而是都满足迭代协议。

## 3. 迭代器是一次性的状态机

迭代器保存当前位置。它通常是一次性的。

```python
xs = [1, 2, 3]
it = iter(xs)

print(list(it))  # [1, 2, 3]
print(list(it))  # []
```

第二次为空，因为同一个迭代器已经被消费完。

列表则不是一次性的：

```python
xs = [1, 2, 3]

print(list(xs))  # [1, 2, 3]
print(list(xs))  # [1, 2, 3]
```

每次 `iter(xs)` 都会创建一个新的列表迭代器。

这解释了一个重要设计原则：

```python
def consume(items):
    for item in items:
        ...
```

如果 `items` 是列表，可以多次遍历；如果它是迭代器，遍历一次后就没了。函数文档和类型标注应尽量说明这一点：

```python
from collections.abc import Iterable, Iterator

def total(items: Iterable[int]) -> int:
    return sum(items)

def read_stream() -> Iterator[str]:
    ...
```

## 4. 协议入口先建立直觉

这一章只需要先抓住两个入口：

```python
it = iter(obj)   # 取得迭代器对象
value = next(it) # 推动迭代器前进一步
```

自定义类型当然可以通过 `__iter__` 和 `__next__` 接入这套机制，但那属于数据模型设计问题。这里先把运行时直觉立住：**可迭代对象产生迭代器；迭代器保存遍历状态；生成器是最常见的迭代器来源之一。**

完整的自定义容器实现、`__getitem__` fallback、`__reversed__` 等内容，见第三章 [自定义类型的迭代协议](../03-data-model-protocols/iteration-data-model.md)。

## 5. 生成器函数

函数体里出现 `yield`，这个函数就变成生成器函数：

```python
def numbers():
    yield 1
    yield 2
    yield 3

g = numbers()
print(g)        # <generator object numbers at 0x...>
print(next(g))  # 1
print(next(g))  # 2
```

调用生成器函数不会立刻执行函数体，而是返回生成器对象。直到调用 `next(g)`，函数体才开始运行。

生成器的核心模型：

**生成器是可暂停、可恢复的函数调用。每次 `yield` 产出一个值，并保存当前执行位置和局部变量。**

例如：

```python
def demo():
    print("start")
    yield 1
    print("middle")
    yield 2
    print("end")

g = demo()
print(next(g))
print(next(g))
next(g)
```

执行顺序是：

```text
start
1
middle
2
end
StopIteration
```

`return` 在生成器中表示结束：

```python
def gen():
    yield 1
    return
    yield 2

print(list(gen()))  # [1]
```

## 6. 生成器表达式

生成器表达式不会一次性创建完整列表：

```python
squares = (x * x for x in range(10))
print(squares)
print(next(squares))
```

对比列表推导式：

```python
xs = [x * x for x in range(10)]
```

列表推导式立即创建列表。生成器表达式按需产出元素。

适合用生成器表达式的场景：

- 数据量大，不想一次性占用内存。
- 只需要消费一次。
- 想把多个处理步骤串成 pipeline。

例如：

```python
total = sum(x * x for x in range(1_000_000))
# Python 允许直接把生成器表达式放在函数调用里，省略外层的括号。
```

这里不会先创建一百万个平方数的列表。

## 7. 惰性计算与流水线

迭代协议让 Python 很适合写数据流水线：

```python
def read_lines(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.rstrip("\n")

def non_empty(lines):
    for line in lines:
        if line:
            yield line

def lower(lines):
    for line in lines:
        yield line.lower()
```

组合：

```python
lines = lower(non_empty(read_lines("data.txt")))

for line in lines:
    print(line)
```

这里每次只处理一行。不是先读完文件、再过滤、再转小写。

可以用生成器表达式写得更短：

```python
with open("data.txt", encoding="utf-8") as f:
    lines = (line.strip().lower() for line in f if line.strip())
    for line in lines:
        print(line)
```

## 8. `yield from`

`yield from iterable` 用于把另一个可迭代对象中的元素逐个产出：

```python
def flatten_once(groups):
    for group in groups:
        yield from group

print(list(flatten_once([[1, 2], [3, 4]])))  # [1, 2, 3, 4]
```

它等价于：

```python
def flatten_once(groups):
    for group in groups:
        for item in group:
            yield item
```

`yield from` 的价值是表达“委托给另一个迭代器”。

递归展开时也常见：

```python
def walk_tree(node):
    yield node.value
    for child in node.children:
        yield from walk_tree(child)
```

在高级生成器协程中，`yield from` 还有传递 `send`、`throw`、返回值等语义，但日常最常用的理解是“把内部迭代器的产出转发出来”。

## 9. `iter(callable, sentinel)`

`iter` 有一个较少见但很有用的形式：

```python
iter(callable, sentinel)
```

它会重复调用 `callable()`，直到返回值等于 `sentinel`。

例如按块读取文件：

```python
with open("data.bin", "rb") as f:
    for chunk in iter(lambda: f.read(8192), b""):
        process(chunk)
```

这比手写 `while True` 更直接地表达了“不断读取，直到空字节串”。

## 10. 字典迭代

字典默认迭代键：

```python
d = {"a": 1, "b": 2}

for key in d:
    print(key)
```

如果要值：

```python
for value in d.values():
    print(value)
```

如果要键值对：

```python
for key, value in d.items():
    print(key, value)
```

`dict.keys()`、`dict.values()`、`dict.items()` 返回的是视图对象，不是列表。它们会反映字典的变化：

```python
d = {"a": 1}
keys = d.keys()

d["b"] = 2
print(keys)  # dict_keys(['a', 'b'])
```

遍历字典时不要修改字典大小：

```python
for key in d:
    d["new"] = 3  # RuntimeError
```

可以先复制键列表：

```python
for key in list(d):
    if should_delete(key):
        del d[key]
```

## 11. `enumerate` 与 `zip`

需要索引时，用 `enumerate`：

```python
for i, value in enumerate(items):
    print(i, value)
```

不要写：

```python
for i in range(len(items)):
    print(i, items[i])
```

除非确实需要用索引做复杂访问。

并行遍历多个序列，用 `zip`：

```python
names = ["Alice", "Bob"]
scores = [90, 80]

for name, score in zip(names, scores):
    print(name, score)
```

`zip` 在最短输入耗尽时停止：

```python
print(list(zip([1, 2, 3], ["a"])))  # [(1, 'a')]
```

如果需要严格长度一致，现代 Python 可以使用：

```python
for a, b in zip(xs, ys, strict=True):
    ...
```

长度不一致时会抛出 `ValueError`。

## 12. `StopIteration` 不应该从生成器体内泄漏

迭代器通过抛出 `StopIteration` 表示结束。但在生成器函数内部，通常不要手动抛出 `StopIteration`。

```python
def gen():
    raise StopIteration
```

现代 Python 会把它转换为 `RuntimeError`。生成器要结束，应使用 `return`：

```python
def gen():
    return
    yield 1
```

统一理解：

- 迭代器的 `__next__` 用 `StopIteration` 告诉外部“没有下一个”。
- 生成器函数体中用 `return` 表示正常结束。

## 13. 可迭代对象的 API 设计

如果函数只需要遍历，不要求索引，接受 `Iterable`：

```python
from collections.abc import Iterable

def total(xs: Iterable[int]) -> int:
    return sum(xs)
```

如果需要多次遍历，要小心迭代器被消费：

```python
def average(xs):
    total = sum(xs)
    count = sum(1 for _ in xs)
    return total / count
```

如果 `xs` 是迭代器，这段代码第二次遍历时已经空了。

修复方式取决于需求：

```python
def average(xs):
    xs = list(xs)
    return sum(xs) / len(xs)
```

这会消耗内存，但语义清楚：函数需要把输入物化。

或者一次遍历完成：

```python
def average(xs):
    total = 0
    count = 0
    for x in xs:
        total += x
        count += 1
    return total / count
```

## 14. 检查表

遇到迭代问题，按下面问：

1. 这个对象是可迭代对象，还是迭代器？
2. `iter(obj)` 返回的是新迭代器，还是对象自身？
3. 这个迭代器是否已经被消费过？
4. 是否需要多次遍历？如果需要，输入能否重复遍历？
5. 是需要惰性 pipeline，还是需要立即物化成列表？
6. `yield` 是在产出值，还是应该用 `return` 结束生成器？
7. 函数 API 应该接受 `Iterable`、`Iterator`，还是具体容器？

最小心智模型：

1. `for` 循环基于 `iter` 和 `next`。
2. 可迭代对象产生迭代器。
3. 迭代器保存状态，通常只能消费一次。
4. 生成器是可暂停、可恢复的函数调用。
5. `yield from` 委托给另一个可迭代对象。
6. 惰性迭代能节省内存，但也带来一次性消费问题。

迭代运行时的美感在于：`for`、生成器、惰性流水线和一次性消费都不是 special case。它们都是同一套“取得迭代器，然后逐步推进”的模型。
