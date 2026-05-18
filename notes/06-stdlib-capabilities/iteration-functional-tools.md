# 迭代与函数式工具

`itertools`、`functools`、`operator` 解决的问题是：把常见迭代、组合、缓存、函数适配模式写成可复用工具。

**这些模块不是为了写“函数式风格”的炫技代码，而是让数据流和函数组合更清楚、更惰性、更少样板。**

## 1. `itertools` 的核心：惰性组合

```python
import itertools

for x in itertools.islice(itertools.count(), 5):
    print(x)
```

`count()` 是无限迭代器，`islice(..., 5)` 只取前 5 个。这里没有创建无限列表。

`itertools` 很多函数返回迭代器，因此通常只能消费一次。

## 2. 常用 itertools

链式连接：

```python
from itertools import chain

items = chain([1, 2], [3, 4])
print(list(items))  # [1, 2, 3, 4]
```

分组：

```python
from itertools import groupby

rows = ["a", "a", "b"]

for key, group in groupby(rows):
    # group 是当前 key 对应的一次性迭代器
    print(key, list(group))
```

注意：`groupby` 只分组相邻元素。要全局分组，先排序或用 `defaultdict`。

组合：

```python
from itertools import combinations, product

print(list(combinations([1, 2, 3], 2))) # [(1, 2), (1, 3), (2, 3)]
print(list(product(["a", "b"], [1, 2]))) # 笛卡尔积
```

## 3. `functools.lru_cache`

缓存纯函数结果：

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

缓存 key 来自参数，因此参数必须可哈希。不要缓存依赖外部可变状态的函数，否则结果可能过期。

查看缓存信息：

```python
print(fib.cache_info())
fib.cache_clear()
```

## 4. `functools.partial`

预绑定部分参数：

```python
from functools import partial

def power(base: int, exp: int) -> int:
    return base ** exp

square = partial(power, exp=2)

print(square(5))  # 25
```

`square` 是可调用对象，保存了原函数和预绑定参数。

## 5. `functools.wraps`

写装饰器时保留原函数元信息：

```python
from functools import wraps

def trace(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # args/kwargs 是转发给原函数的调用参数
        print("call", fn.__name__)
        return fn(*args, **kwargs)

    return wrapper
```

没有 `wraps`，`wrapper.__name__`、文档、标注等会遮蔽原函数，影响调试和框架。

## 6. `operator`

`operator` 提供函数形式的常见运算：

```python
from operator import itemgetter, attrgetter

rows = [{"name": "Alice", "age": 20}, {"name": "Bob", "age": 18}]
rows.sort(key=itemgetter("age"))
```

属性获取：

```python
users.sort(key=attrgetter("name"))
```

它比简单 lambda 更短，也清楚表达“按字段取值”。

## 7. 检查表

使用这些工具时，按下面问：

1. 数据是否可以惰性处理？
2. 这个迭代器是否只能消费一次？
3. `groupby` 输入是否已按 key 排好？
4. 缓存函数是否纯、参数是否可哈希？
5. 装饰器是否使用 `wraps`？
6. `operator` 是否能让 key 函数更清楚？

最小心智模型：

1. `itertools` 组合迭代器。
2. `functools` 适配和增强函数。
3. `operator` 把运算变成函数对象。
4. 惰性工具节省内存，但要注意一次性消费。
