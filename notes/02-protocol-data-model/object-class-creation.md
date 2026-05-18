# 对象创建与类创建协议

对象创建协议回答两个问题：

1. 调用类时，实例如何被创建和初始化？
2. 执行 `class` 语句时，类对象如何被创建？

**实例创建通常经过 `__new__` 和 `__init__`；类创建则由元类、类命名空间、`__set_name__`、`__init_subclass__` 和 class decorator 共同参与。**

不要把类理解成静态模板。类本身也是运行时创建出来的对象。

## 1. 调用类时发生什么

```python
class User:
    def __init__(self, name):
        self.name = name

u = User("Alice")
```

`User("Alice")` 大致发生：

1. 类对象 `User` 被调用。
2. 元类的 `__call__` 接管调用过程。
3. 调用 `User.__new__` 创建实例对象。
4. 调用 `User.__init__` 初始化实例对象。
5. 返回实例对象。

通常你只写 `__init__`，因为大多数类不需要自定义对象分配。

## 2. `__new__`

`__new__` 负责创建并返回新对象：

```python
class User:
    def __new__(cls, name):
        # cls 是正在创建实例的类对象
        print("new", cls, name)
        obj = super().__new__(cls)
        return obj

    def __init__(self, name):
        # self 是 __new__ 返回的实例对象
        print("init", self, name)
        self.name = name

u = User("Alice")
```

`__new__` 是静态式方法，接收类对象 `cls`，必须返回实例对象。`__init__` 不创建对象，只初始化已经创建好的对象。

## 3. 什么时候需要 `__new__`

常见场景：

- 继承不可变内置类型。
- 实现单例或缓存。
- 控制实际返回的对象类型。

不可变类型示例：

```python
class UpperStr(str):
    def __new__(cls, value):
        # str 不可变，必须在 __new__ 中决定最终字符串值
        return super().__new__(cls, value.upper())

s = UpperStr("hello")
print(s)  # HELLO
```

如果放在 `__init__`，已经太晚了，因为字符串对象的值在创建时就定了。

## 4. `__init__`

`__init__` 初始化对象，返回值必须是 `None`：

```python
class User:
    def __init__(self, name):
        # self 是已经创建好的实例
        self.name = name

u = User("Alice")
```

不要从 `__init__` 返回对象：

```python
class Bad:
    def __init__(self):
        return 1  # TypeError
```

`__init__` 的职责是建立对象不变量。创建结束后，对象应处于可用状态。

## 5. `class` 语句也是可执行语句

```python
class User:
    species = "human"

    def greet(self):
        return "hello"
```

这不是静态声明。执行 `class` 语句时，Python 大致做：

1. 准备类命名空间。
2. 执行类体，把 `species`、`greet` 等名字放入命名空间。
3. 调用元类创建类对象。
4. 把类名 `User` 绑定到新类对象。

所以类体中的代码会执行：

```python
class Demo:
    print("class body runs")
```

导入模块时执行到这个类定义，就会打印。

## 6. `type` 可以创建类

类对象通常由 `type` 创建：

```python
User = type(
    "User",          # 类名
    (),              # 基类元组
    {"species": "human"}, # 类命名空间
)

print(User.species)
```

这说明 `class` 语句不是唯一方式。它是创建类对象的语法糖。

大致对应：

```python
class User:
    species = "human"
```

## 7. 元类

元类是创建类对象的类。默认元类是 `type`：

```python
class User:
    pass

print(type(User))  # <class 'type'>
```

自定义元类：

```python
class Meta(type):
    def __new__(mcls, name, bases, namespace):
        # mcls 是元类本身，name 是类名，bases 是基类元组，namespace 是类体命名空间
        print("creating class", name)
        return super().__new__(mcls, name, bases, namespace)

class User(metaclass=Meta):
    pass
```

元类很强，但也很重。很多场景可以用 `__init_subclass__` 或 class decorator 替代。

## 8. `__init_subclass__`

当一个类被继承时，父类的 `__init_subclass__` 会被调用：

```python
class Plugin:
    registry = []

    def __init_subclass__(cls, **kwargs):
        # cls 是新创建的子类对象
        super().__init_subclass__(**kwargs)
        Plugin.registry.append(cls)

class JsonPlugin(Plugin):
    pass

class CsvPlugin(Plugin):
    pass

print(Plugin.registry)  # [JsonPlugin, CsvPlugin]
```

它适合：

- 自动注册子类。
- 校验子类是否定义了必要属性。
- 给子类补默认配置。

相比元类，`__init_subclass__` 更局部、更容易读。

## 9. Class Decorator

类装饰器接收类对象，返回类对象或替代对象：

```python
def add_id(cls):
    # cls 是刚创建好的类对象
    cls.id = None
    return cls

@add_id
class User:
    pass

print(User.id)
```

等价于：

```python
class User:
    pass

User = add_id(User)
```

类装饰器适合对类做一次性改造，比如注册、补方法、添加配置。`dataclass` 就是类装饰器的典型例子。

## 10. `__set_name__` 的时机

描述符的 `__set_name__` 在类创建期间调用：

```python
class Field:
    def __set_name__(self, owner, name):
        # owner 是正在创建的类对象，name 是描述符绑定的类属性名
        self.owner = owner
        self.name = name

class User:
    name = Field()
```

调用顺序上，类体先执行，命名空间里出现 `name = Field()`；创建类对象时，Python 通知这个描述符它的归属。

## 11. 选择工具

很多类创建定制需求有多个工具：

- 只想初始化实例：用 `__init__`。
- 要控制不可变对象创建：用 `__new__`。
- 要复用字段访问逻辑：用描述符。
- 要在子类创建时注册或校验：用 `__init_subclass__`。
- 要一次性改造类：用 class decorator。
- 要控制类对象创建全过程：才考虑 metaclass。

不要一看到“类创建”就上元类。元类是强工具，但会提高理解成本。

## 12. 检查表

遇到对象或类创建问题，按下面问：

1. 当前是在创建实例，还是创建类对象？
2. 是否只需要初始化实例？如果是，用 `__init__`。
3. 是否必须在对象创建前决定值？如果是，考虑 `__new__`。
4. 是否是在继承发生时做注册或校验？考虑 `__init_subclass__`。
5. 是否是在类创建后做一次改造？考虑 class decorator。
6. 是否真的需要控制类对象创建全过程？最后再考虑 metaclass。
7. 描述符是否需要通过 `__set_name__` 获取字段名？

最小心智模型：

1. 类调用创建实例。
2. `__new__` 创建对象。
3. `__init__` 初始化对象。
4. `class` 语句执行类体并创建类对象。
5. 类也是对象，通常由 `type` 创建。
6. 元类控制类对象创建。
7. `__init_subclass__` 和 class decorator 是更轻量的类定制工具。
