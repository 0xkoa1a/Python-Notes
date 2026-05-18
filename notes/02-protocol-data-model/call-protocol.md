# 调用协议

调用协议回答的问题是：为什么有些对象可以像函数一样被调用。

**`obj(...)` 不要求 `obj` 是函数；它只要求对象可调用。对普通对象来说，调用入口是 `__call__`。**

函数、类、方法、偏函数、可调用实例、装饰器对象、框架中的依赖对象，都建立在这个统一模型上。

## 1. `callable`

判断对象能否被调用：

```python
def f():
    pass

class C:
    pass

print(callable(f))  # True，函数对象可调用
print(callable(C))  # True，类对象可调用，调用会创建实例
print(callable(1))  # False
```

类的实例默认不可调用：

```python
c = C()
print(callable(c))  # False
```

除非实现 `__call__`。

## 2. `__call__`

```python
class Adder:
    def __init__(self, n):
        self.n = n

    def __call__(self, x):
        # obj(x) 会调用 obj.__call__(x)
        return x + self.n

add10 = Adder(10)
print(add10(5))        # 15
print(callable(add10)) # True
```

`__call__` 的参数绑定规则和普通函数一样：

```python
class Logger:
    def __call__(self, *args, **kwargs):
        # args 收集位置参数，kwargs 收集关键字参数
        print("args:", args)
        print("kwargs:", kwargs)

log = Logger()
log(1, 2, level="info")
```

## 3. 可调用对象与闭包

闭包和可调用对象可以表达相似模式。

闭包：

```python
def make_adder(n):
    def add(x):
        return x + n

    return add

add10 = make_adder(10)
```

可调用对象：

```python
class Adder:
    def __init__(self, n):
        self.n = n

    def __call__(self, x):
        return x + self.n

add10 = Adder(10)
```

选择依据：

- 状态很少、逻辑简单：闭包轻便。
- 状态较多、需要多个方法、需要清晰 repr 或配置：可调用对象更清楚。

## 4. 类调用也是协议

类对象可以调用：

```python
class User:
    def __init__(self, name):
        self.name = name

u = User("Alice")
```

`User("Alice")` 大致经历：

1. 调用类对象。
2. 类的元类 `type.__call__` 负责创建实例。
3. 进入 `User.__new__` 分配对象。
4. 进入 `User.__init__` 初始化对象。

这会在对象创建章节详细展开。这里先记住：类能被调用，是因为类对象本身满足调用协议。

## 5. 装饰器对象

装饰器不一定是函数，也可以是可调用对象：

```python
from functools import wraps

class Trace:
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, fn):
        # fn 是被装饰的原函数对象
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # wrapper 是替换原函数的新函数对象
            print(self.prefix, fn.__name__)
            return fn(*args, **kwargs)

        return wrapper

@Trace("call")
def add(x, y):
    return x + y

print(add(1, 2))
```

`@Trace("call")` 的过程：

1. `Trace("call")` 创建一个可调用实例。
2. 这个实例被当作装饰器调用，接收原函数 `add`。
3. 返回 `wrapper`。
4. 名字 `add` 重新绑定到 `wrapper`。

## 6. 带状态的函数对象

可调用对象适合带状态的策略：

```python
class Retry:
    def __init__(self, times):
        self.times = times

    def __call__(self, fn):
        # fn 是需要被重试包装的函数对象
        def wrapper(*args, **kwargs):
            last_error = None
            for _ in range(self.times):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    # exc 是本次调用捕获到的异常对象
                    last_error = exc
            raise last_error

        return wrapper
```

这里 `Retry(times=3)` 比闭包更容易扩展，比如之后增加日志、退避策略、错误分类。

## 7. `functools.partial`

`partial` 会创建一个可调用对象，预先绑定部分参数：

```python
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)

print(square(5))       # 25
print(callable(square)) # True
```

`square` 不是普通函数，而是 `partial` 对象。它保存了：

- 原始可调用对象 `power`。
- 预先绑定的关键字参数 `exp=2`。
- 调用时再传入的新参数。

## 8. 检查表

遇到调用协议问题，按下面问：

1. 被调用的对象到底是什么类型？
2. `callable(obj)` 是否为真？
3. 如果是实例，是否实现了 `__call__`？
4. 调用时参数如何绑定？
5. 这个可调用对象是否保存状态？
6. 它更适合写成函数、闭包、类，还是 `partial`？
7. 如果它是装饰器，返回的是原函数还是 wrapper？

最小心智模型：

1. `obj(...)` 是调用协议。
2. 函数、类、方法天然可调用。
3. 实例实现 `__call__` 后也可调用。
4. 可调用对象可以像函数一样传递，但能携带更明确的状态。
