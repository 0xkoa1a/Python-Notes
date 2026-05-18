# 属性访问协议

属性访问协议回答的问题是：`obj.name` 到底如何找到一个对象。

**属性访问不是简单地从对象字典里取值。`obj.name` 会进入 `__getattribute__`；找不到时才可能进入 `__getattr__`；赋值和删除分别进入 `__setattr__` 与 `__delattr__`。**

这套协议支撑了普通属性、方法绑定、property、描述符、ORM 字段、Pydantic 模型、代理对象和很多框架魔法。

## 1. 点号访问进入 `__getattribute__`

表达式：

```python
obj.name
```

会调用：

```python
obj.__getattribute__("name")
```

示例：

```python
class Trace:
    def __init__(self):
        self.x = 1

    def __getattribute__(self, name):
        # name 是点号右侧的属性名字符串
        print("get", name)
        return object.__getattribute__(self, name)

t = Trace()
print(t.x)
```

必须调用 `object.__getattribute__`，否则会无限递归：

```python
class Bad:
    def __getattribute__(self, name):
        return self.__dict__[name]  # 访问 self.__dict__ 又会进入 __getattribute__
```

正确写法：

```python
class Safe:
    def __getattribute__(self, name):
        data = object.__getattribute__(self, "__dict__")
        return data[name]
```

不过大多数代码不应该重写 `__getattribute__`。它太底层，影响所有属性访问。

## 2. `__getattr__` 是找不到时的后备

`__getattr__` 只有在正常属性查找失败时才调用：

```python
class Config:
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        # 只有普通查找找不到 name 时才进入这里
        try:
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

cfg = Config({"host": "localhost"})
print(cfg.host)  # localhost
```

注意要抛 `AttributeError`，不是 `KeyError`。很多内置函数和工具依赖这个约定：

```python
hasattr(cfg, "missing")  # 内部会捕获 AttributeError
```

`__getattr__` 适合：

- 延迟加载属性。
- 代理对象。
- 把字典键映射为属性。
- 模块级动态属性。

## 3. `__getattribute__` 与 `__getattr__` 的区别

```text
__getattribute__：每次属性访问都会调用。
__getattr__：只有属性找不到时才调用。
```

示例：

```python
class Demo:
    existing = 1

    def __getattr__(self, name):
        # name 是找不到的属性名
        return f"fallback for {name}"

d = Demo()
print(d.existing) # 1，不调用 __getattr__
print(d.missing)  # fallback for missing
```

如果只是想提供缺失属性的后备，优先用 `__getattr__`。只有要拦截所有访问时，才考虑 `__getattribute__`。

## 4. 属性赋值进入 `__setattr__`

语句：

```python
obj.name = value
```

调用：

```python
obj.__setattr__("name", value)
```

示例：

```python
class Positive:
    def __setattr__(self, name, value):
        # name 是属性名，value 是要绑定到属性上的对象
        if name == "score" and value < 0:
            raise ValueError("score must be non-negative")
        object.__setattr__(self, name, value)

p = Positive()
p.score = 10
```

同样，必须通过 `object.__setattr__` 完成真正赋值，避免递归。

很多校验场景用 `property` 或描述符更清楚。`__setattr__` 适合需要统一拦截多个属性的场景。

## 5. 删除属性进入 `__delattr__`

语句：

```python
del obj.name
```

调用：

```python
obj.__delattr__("name")
```

示例：

```python
class Protected:
    def __delattr__(self, name):
        # name 是 del 右侧要删除的属性名
        if name.startswith("_"):
            raise AttributeError("private attributes cannot be deleted")
        object.__delattr__(self, name)
```

删除属性不是删除对象本身，而是删除对象命名空间里的一个绑定。

## 6. `__dict__` 与属性存储

普通实例通常把属性保存在实例字典里：

```python
class User:
    pass

u = User()
u.name = "Alice"

print(u.__dict__)  # {'name': 'Alice'}
```

但不要把属性访问简化成“就是查 `__dict__`”。因为属性查找还会涉及：

- 类属性。
- 描述符。
- `property`。
- `__getattribute__`。
- `__getattr__`。
- `__slots__`。

示例：

```python
class User:
    species = "human"

u = User()
print(u.species)  # 来自类对象 User.__dict__，不在 u.__dict__ 中
```

## 7. 代理对象

属性协议可以实现代理：

```python
class Proxy:
    def __init__(self, target):
        object.__setattr__(self, "_target", target)

    def __getattr__(self, name):
        # target 是被代理对象；name 是当前代理对象找不到的属性
        target = object.__getattribute__(self, "_target")
        return getattr(target, name)

class Service:
    def run(self):
        return "running"

p = Proxy(Service())
print(p.run())  # running
```

这里 `p.run` 在代理对象上找不到，于是 `__getattr__` 把访问转发给 target。

如果还要代理赋值，需要实现 `__setattr__`。但代理对象很容易让调试变复杂，必须谨慎设计。

## 8. 检查表

遇到属性访问问题，按下面问：

1. 这是读取、赋值，还是删除属性？
2. 读取是否被 `__getattribute__` 拦截？
3. 普通查找失败后是否进入 `__getattr__`？
4. `__getattr__` 是否正确抛出 `AttributeError`？
5. 自定义 `__setattr__` 是否调用了 `object.__setattr__`？
6. 属性来自实例字典、类属性，还是描述符？
7. 是否真的需要这么底层的协议，还是 `property` 足够？

最小心智模型：

1. `obj.name` 进入 `__getattribute__`。
2. 找不到时才进入 `__getattr__`。
3. `obj.name = value` 进入 `__setattr__`。
4. `del obj.name` 进入 `__delattr__`。
5. 属性访问协议是描述符、方法绑定和框架魔法的基础。
