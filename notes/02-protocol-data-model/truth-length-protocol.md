# 布尔与长度协议

Python 中很多对象都能放进 `if`、`while`、`and`、`or`、`not`。这背后不是“每种类型各有规则”，而是一套布尔协议。

**布尔上下文先尝试 `__bool__`；如果没有，再尝试 `__len__`；如果两者都没有，对象默认为真。**

这套协议解释了空列表为假、非空字符串为真、自定义对象默认为真等现象。

## 1. 布尔上下文

这些位置都会触发布尔判断：

```python
if obj:
    ...

while obj:
    ...

not obj
obj and other
obj or other
```

入口是 `bool(obj)`：

```python
print(bool([]))      # False
print(bool([1]))     # True
print(bool(""))      # False
print(bool("hello")) # True
```

常见假值：

- `False`
- `None`
- 数字零：`0`、`0.0`、`0j`
- 空容器：`""`、`[]`、`{}`、`set()`、`tuple()`

其他大多数对象为真。

## 2. `__bool__`

自定义布尔语义：

```python
class Result:
    def __init__(self, ok, value=None):
        self.ok = ok
        self.value = value

    def __bool__(self):
        # bool(result) 会调用这里；返回值必须是真正的 bool
        return self.ok

r = Result(False)
print(bool(r))  # False
```

`__bool__` 必须返回 `True` 或 `False`：

```python
class Bad:
    def __bool__(self):
        return 1  # TypeError: __bool__ should return bool
```

不要让 `__bool__` 做昂贵计算或产生副作用。布尔判断可能出现在非常普通的位置，读者会默认它很轻。

## 3. `__len__` 作为后备

如果没有 `__bool__`，Python 会尝试 `__len__`：

```python
class Bag:
    def __init__(self, items):
        self.items = list(items)

    def __len__(self):
        # len(bag) 和 bool(bag) 都可能调用这里
        return len(self.items)

bag = Bag([])
print(len(bag))   # 0
print(bool(bag))  # False
```

`__len__` 必须返回非负整数：

```python
class Bad:
    def __len__(self):
        return -1

bool(Bad())  # ValueError
```

如果对象既没有 `__bool__` 也没有 `__len__`，默认为真：

```python
class Marker:
    pass

print(bool(Marker()))  # True
```

## 4. `None` 判断不要和假值混淆

常见错误：

```python
def use_timeout(timeout=None):
    if not timeout:
        timeout = 5
```

这会把 `0` 也当作没有传入。更精确的写法：

```python
def use_timeout(timeout=None):
    if timeout is None:
        timeout = 5
```

统一判断：

```text
是否没有值：用 is None。
是否为空容器：用 if not xs。
是否为特定布尔单例：很少需要用 is True / is False。
```

## 5. `and` 与 `or` 返回对象本身

`and` 和 `or` 不一定返回布尔值，它们返回参与运算的对象。

```python
print("hello" or "default")  # hello
print("" or "default")       # default
print([] and 123)            # []
print([1] and 123)           # 123
```

规则：

- `x or y`：如果 `x` 为真，返回 `x`；否则返回 `y`。
- `x and y`：如果 `x` 为假，返回 `x`；否则返回 `y`。

这解释了常见默认值写法：

```python
name = user_input or "anonymous"
```

但它会把空字符串也替换掉。如果空字符串是合法输入，就应该显式判断 `None`。

## 6. 设计布尔语义要谨慎

有些对象天然适合布尔语义：

```python
class QueryResult:
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        # 空结果为假，非空结果为真
        return len(self.rows)
```

有些对象不应该有含糊的布尔语义。比如数组库可能拒绝：

```python
if array:
    ...
```

因为数组里有多个元素时，“整体为真”到底是所有元素为真，还是任意元素为真，并不明确。好的 API 会迫使调用者写清楚：

```python
if array.any():
    ...

if array.all():
    ...
```

设计自定义对象时，如果布尔语义不明显，不实现 `__bool__` 可能比实现一个含糊规则更好。

## 7. 检查表

遇到布尔判断问题，按下面问：

1. 这里调用的是 `bool(obj)` 吗？
2. 对象是否实现了 `__bool__`？
3. 如果没有，是否实现了 `__len__`？
4. `__len__` 是否返回非负整数？
5. 这里是想判断 `None`，还是想判断空？
6. `and` / `or` 的返回值是否被误以为一定是 bool？
7. 自定义对象的真假语义是否明确？

最小心智模型：

1. 布尔上下文调用布尔协议。
2. `__bool__` 优先级高于 `__len__`。
3. 空容器为假来自长度协议。
4. 普通自定义对象默认为真。
5. `and` 和 `or` 返回对象，不强制返回 bool。
