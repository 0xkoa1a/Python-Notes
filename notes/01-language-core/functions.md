# 函数机制

Python 函数不是“语句块的包装”。函数本身也是对象，它有名字、参数、默认值、闭包、属性，并且可以被传递、返回、装饰和调用。

**函数机制的统一模型是：`def` 执行时创建函数对象；调用时创建局部命名空间；参数绑定发生在函数体执行之前；函数体执行结束后返回一个对象或抛出异常。**

很多所谓函数陷阱，都来自没有把“函数定义时”和“函数调用时”分清楚。

## 1. `def` 是可执行语句

`def` 不是纯声明。执行到 `def` 语句时，Python 会创建函数对象，并把函数名绑定到这个对象。

```python
def add(x, y):
    return x + y

print(add)
print(type(add))
```

可以把它粗略理解为：

```text
创建一个函数对象
把名字 add 绑定到这个函数对象
```

所以函数可以赋值给别的名字：

```python
def add(x, y):
    return x + y

op = add
print(op(1, 2))  # 3
```

也可以放进容器：

```python
ops = [str.upper, str.lower]

for op in ops:
    print(op("Py"))
```

函数对象可以作为参数：

```python
def apply(fn, x):
    return fn(x)

print(apply(abs, -3))  # 3
```

也可以作为返回值：

```python
def make_multiplier(n):
    def mul(x):
        return x * n

    return mul

times3 = make_multiplier(3)
print(times3(10))  # 30
```

这就是“函数是一等公民”的含义：函数对象和其他对象一样，可以被绑定、传递、保存和返回。

## 2. 函数调用：先绑定参数，再执行函数体

函数调用大致分成两步：

1. 根据调用表达式，把实参对象绑定到形参名字。
2. 创建局部命名空间，执行函数体。

```python
def f(a, b):
    print(a, b)

f(1, 2)
```

调用时发生：

```text
local a -> 1
local b -> 2
```

参数绑定不是复制对象。它和普通赋值一样，是名字绑定：

```python
def append_one(xs):
    xs.append(1)

items = []
append_one(items)
print(items)  # [1]
```

`xs` 和 `items` 绑定到同一个列表对象。

但如果函数内部重新绑定参数名，不会影响外部名字：

```python
def replace(xs):
    xs = [1, 2, 3]

items = []
replace(items)
print(items)  # []
```

**函数参数传递不是“传值 vs 传引用”的二选一；它是对象绑定。**

## 3. 参数种类

Python 的函数参数系统很强，核心是区分参数能否按位置传、能否按关键字传，以及是否收集剩余参数。

```python
def f(pos_only, /, normal, *args, kw_only, **kwargs):
    ...
```

从左到右：

- `/` 前：只能按位置传。
- `/` 和 `*` 之间：既可以按位置传，也可以按关键字传。
- `*args`：收集多余的位置参数。
- `*` 后：只能按关键字传。
- `**kwargs`：收集多余的关键字参数。

示例：

```python
def connect(host, port, *, timeout=5, ssl=False):
    print(host, port, timeout, ssl)

connect("localhost", 5432)
connect("localhost", 5432, timeout=10)
connect("localhost", 5432, ssl=True)
```

`timeout` 和 `ssl` 是 keyword-only 参数。这样调用更清楚：

```python
connect("localhost", 5432, True, 10)  # 不允许，也不清楚
```

keyword-only 参数适合布尔开关、配置项和容易混淆的参数。

位置-only 参数常见于内置函数或需要保护参数名的 API：

```python
def f(x, /):
    return x

f(1)
f(x=1)  # TypeError
```

它的意义是：调用者不能依赖参数名 `x`，以后实现可以改名而不破坏调用代码。

## 4. `*args` 与 `**kwargs`

`*args` 把多余的位置参数收集成元组：

```python
def f(*args):
    print(args)

f(1, 2, 3)  # (1, 2, 3)
```

`**kwargs` 把多余的关键字参数收集成字典：

```python
def f(**kwargs):
    print(kwargs)

f(name="Alice", age=20)  # {'name': 'Alice', 'age': 20}
```

转发调用时也常见：

```python
def logged_call(fn, *args, **kwargs):
    print("calling", fn.__name__)
    return fn(*args, **kwargs)

print(logged_call(pow, 2, 10))
```

这里有两个方向：

```python
def f(*args): ...
```

表示“收集参数”。

```python
f(*items)
```

表示“展开可迭代对象作为位置参数”。

同理：

```python
def f(**kwargs): ...
```

表示“收集关键字参数”。

```python
f(**options)
```

表示“展开字典作为关键字参数”。

## 5. 默认参数在函数定义时求值

这是函数机制里最重要的时间点问题。

```python
def f(x=[]):
    x.append(1)
    return x

print(f())  # [1]
print(f())  # [1, 1]
```

正确理解：

**默认参数表达式在执行 `def` 语句时求值一次，结果保存在函数对象上；每次省略参数调用时，形参绑定到这个默认对象。**

可以观察默认参数：

```python
def f(x=[]):
    x.append(1)
    return x

print(f.__defaults__)  # ([],)
f()
print(f.__defaults__)  # ([1],)
```

推荐写法：

```python
def f(x=None):
    if x is None:
        x = []
    x.append(1)
    return x
```

这里 `None` 是哨兵对象。每次调用如果没有传入列表，就在函数调用期间创建新的列表。

默认参数在定义时求值也可以被有意利用：

```python
def make_counter(step=1, _state={"count": 0}):
    _state["count"] += step
    return _state["count"]
```

这段代码可运行，但一般不推荐。它隐藏了共享状态，读者需要理解函数对象保存默认参数对象。工程代码中更清晰的写法是闭包或类。

## 6. 返回值与 `None`

函数没有显式 `return` 时，返回 `None`：

```python
def f():
    pass

print(f())  # None
```

`return` 后没有表达式，也返回 `None`：

```python
def f():
    return

print(f())  # None
```

函数只能返回一个对象。但这个对象可以是元组：

```python
def divmod_like(a, b):
    return a // b, a % b

q, r = divmod_like(10, 3)
```

这里不是返回了两个独立值，而是返回了一个二元组，然后调用方解包。

## 7. 函数对象的属性

函数对象携带很多信息：

```python
def f(x: int, y: int = 0) -> int:
    """Add two numbers."""
    return x + y

print(f.__name__)
print(f.__doc__)
print(f.__defaults__)
print(f.__annotations__)
```

这些属性是很多工具的基础：

- `help`
- 文档生成器
- Web 框架路由
- CLI 框架参数解析
- 测试框架
- 装饰器
- 类型检查工具

函数也可以有自定义属性：

```python
def f():
    pass

f.calls = 0
f.calls += 1
```

不过工程中通常更倾向使用闭包、类或装饰器来保存状态。

## 8. Lambda：表达式形式的匿名函数

`lambda` 创建函数对象：

```python
square = lambda x: x * x
print(square(5))  # 25
```

它和 `def` 的主要区别是语法：

- `lambda` 是表达式，可以放在表达式位置。
- `lambda` 函数体只能是一个表达式。
- `def` 更适合复杂逻辑、文档字符串、类型标注和调试。

常见用法：

```python
users = [{"name": "Bob"}, {"name": "Alice"}]
users.sort(key=lambda user: user["name"])
```

不要为了“高级感”滥用 lambda。可读性更重要：

```python
def by_name(user):
    return user["name"]

users.sort(key=by_name)
```

## 9. 装饰器：接收函数，返回函数

装饰器本质上是函数对象的替换：

```python
@decorator
def f():
    ...
```

等价于：

```python
def f():
    ...

f = decorator(f)
```

最小装饰器：

```python
def trace(fn):
    def wrapper(*args, **kwargs):
        print("call", fn.__name__)
        return fn(*args, **kwargs)

    return wrapper

@trace
def add(x, y):
    return x + y

print(add(1, 2))
```

这里发生了三件事：

1. `def add` 创建原始函数对象。
2. `trace(add)` 返回 `wrapper` 函数对象。
3. 名字 `add` 重新绑定到 `wrapper`。

所以装饰器不是在函数调用时才生效，而是在函数定义之后立即执行。

## 10. `functools.wraps`

上面的装饰器有一个问题：

```python
print(add.__name__)  # wrapper
```

原函数元信息丢了。应使用 `functools.wraps`：

```python
from functools import wraps

def trace(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print("call", fn.__name__)
        return fn(*args, **kwargs)

    return wrapper

@trace
def add(x, y):
    """Add two numbers."""
    return x + y

print(add.__name__)  # add
print(add.__doc__)   # Add two numbers.
```

`wraps` 会把原函数的重要元信息复制到 wrapper 上。很多框架依赖这些信息，所以写装饰器时几乎总应该使用它。

## 11. 带参数的装饰器

带参数的装饰器多一层函数：

```python
from functools import wraps

def repeat(n):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(n):
                result = fn(*args, **kwargs)
            return result

        return wrapper

    return decorator

@repeat(3)
def hello():
    print("hello")
```

它等价于：

```python
def hello():
    print("hello")

hello = repeat(3)(hello)
```

分层理解：

- `repeat(3)` 在定义时执行，返回真正的装饰器 `decorator`。
- `decorator(hello)` 接收原函数，返回 `wrapper`。
- 名字 `hello` 绑定到 `wrapper`。

## 12. 递归与调用栈

每次函数调用都会创建新的栈帧和局部命名空间：

```python
def fact(n):
    if n == 0:
        return 1
    return n * fact(n - 1)
```

递归不是函数“自己跳回去”，而是一次调用创建另一次调用。每一层都有自己的 `n`。

Python 默认递归深度有限：

```python
import sys

print(sys.getrecursionlimit())
```

Python 没有保证尾递归优化。深递归场景通常改写为循环，或者显式维护栈。

## 13. 类型标注不改变运行时调用语义

```python
def add(x: int, y: int) -> int:
    return x + y

print(add("a", "b"))  # ab
```

类型标注保存在函数对象的 `__annotations__` 中，默认不会强制检查：

```python
print(add.__annotations__)
```

它的价值在于：

- 给读者说明接口。
- 给 IDE 提供补全和检查。
- 给 mypy / pyright 等静态检查器使用。
- 给部分框架做运行时解析。

不要把类型标注误解成 Python 运行时类型系统的强制约束。

## 14. 常见设计判断

什么时候写函数？

- 有清晰输入输出。
- 逻辑可以独立命名。
- 需要复用或测试。
- 副作用边界可以说清楚。

什么时候不要让函数偷偷修改参数？

- 调用者可能继续使用原对象。
- 参数名没有暗示原地修改。
- 函数看起来像纯计算。

如果要原地修改，命名要诚实：

```python
def normalize_in_place(xs: list[float]) -> None:
    total = sum(xs)
    for i, x in enumerate(xs):
        xs[i] = x / total
```

如果不修改输入，返回新对象：

```python
def normalized(xs: list[float]) -> list[float]:
    total = sum(xs)
    return [x / total for x in xs]
```

## 15. 检查表

遇到函数相关问题，按下面问：

1. 这是函数定义时发生，还是函数调用时发生？
2. `def` 创建的函数对象保存了哪些默认参数、闭包和元信息？
3. 调用时实参如何绑定到形参？
4. 参数名是否只是重新绑定，还是修改了共享对象？
5. 默认参数是否是可变对象？
6. `*args` / `**kwargs` 是在收集，还是在展开？
7. 装饰器是否替换了原函数对象？
8. 是否使用 `functools.wraps` 保留元信息？

最小心智模型：

1. 函数是对象。
2. `def` 执行时创建函数对象并绑定名字。
3. 默认参数在函数定义时求值。
4. 调用时先进行参数绑定，再执行函数体。
5. 参数绑定不复制对象。
6. 装饰器是函数对象的变换。
7. 类型标注默认不改变运行时行为。

函数机制的核心，不是记住更多调用形式，而是分清对象何时创建、名字何时绑定、函数何时执行。
