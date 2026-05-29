# 描述符协议

**只要一个对象定义了 `__get__`、`__set__` 或 `__delete__` 中的任意一个，并且它作为类属性存在，它就是描述符。**

## 1. 最小描述符

```python
class Descriptor:
    def __get__(self, instance, owner):
        # instance 是访问属性的实例；通过类访问时为 None
        # owner 是拥有这个描述符的类
        return "value from descriptor"

class User:
    name = Descriptor()

u = User()
print(u.name)    # value from descriptor
print(User.name) # value from descriptor
```

访问 `u.name` 时，Python 发现 `name` 是类 `User` 上的描述符对象，于是调用描述符的 `__get__`。

即以下两条语句是等价的：

```python
c.x
c.__dict__["x"].__get__(c, C)
```

## 2. `instance` 与 `owner`

区分实例访问和类访问：

```python
class Descriptor:
    def __get__(self, instance, owner):
        if instance is None:
            # 通过类访问，例如 User.name
            return self
        # 通过实例访问，例如 u.name
        return f"value for {instance!r}"

class User:
    name = Descriptor()

print(User.name)  # 描述符对象本身
print(User().name)
```

很多描述符在类访问时返回自身，方便调试、配置或元编程。

## 3. 数据描述符与非数据描述符

描述符分两类：

- 数据描述符：实现了 `__set__` 或 `__delete__`。
- 非数据描述符：只实现 `__get__`。

数据描述符优先级高于实例字典；非数据描述符优先级低于实例字典。

数据描述符：

```python
class DataDesc:
    def __get__(self, instance, owner):
        return "from descriptor"

    def __set__(self, instance, value):
        # instance 是被赋值的实例，value 是右侧对象
        instance.__dict__["x"] = value

class C:
    x = DataDesc()

c = C()
c.__dict__["x"] = "from instance dict"
print(c.x)  # from descriptor
```

非数据描述符：

```python
class NonDataDesc:
    def __get__(self, instance, owner):
        return "from descriptor"

class C:
    x = NonDataDesc()

c = C()
c.__dict__["x"] = "from instance dict"
print(c.x)  # from instance dict
```

这条优先级规则解释了为什么实例属性可以遮蔽普通方法，但不能随便遮蔽 property。

更具体来说，顺序是：数据描述符 => 实例字典 => 非数据描述符 => 普通类属性 => `__getattr__` 后备。

## 4. `property` 在这里的位置

`property` 的使用方式、setter 校验、兼容性演进和缓存属性，已经在第二章 [`property`](../02-class-object-model/property.md) 中作为 OOP 工具讲过。这里不重复那些设计建议，只看它在描述符协议里的位置。

**`property` 是数据描述符。** 它作为类属性存在，读取实例属性时调用 getter，赋值时调用 setter，删除时调用 deleter。也正因为它是数据描述符，所以优先级高于实例字典。

```python
class User:
    @property
    def name(self):
        # 访问 user.name 时，property.__get__ 会调用这个 getter。
        return self._name

    @name.setter
    def name(self, value):
        # 给 user.name 赋值时，property.__set__ 会调用这个 setter。
        self._name = value
```

在描述符视角下，`property` 不是特殊语法魔法，而是内置描述符对象。它说明了一件事：**点号属性访问可以被类上的对象接管。**

## 5. 函数也是描述符

类体中的普通函数也是描述符：

```python
class User:
    def greet(self):
        return "hello"

u = User()

print(User.greet) # 函数对象
print(u.greet)    # 绑定方法对象
```

发生了什么：

```python
method = User.greet.__get__(u, User)
```

`method` 是绑定方法对象，它把实例 `u` 和函数 `User.greet` 绑定在一起。调用：

```python
u.greet()
```

等价于：

```python
User.greet(u)
```

这解释了 `self` 不是关键字。`self` 只是普通参数名，只是方法绑定协议会自动把实例作为第一个参数传入。

## 6. `staticmethod` 与 `classmethod`

它们也是描述符包装器。

```python
class C:
    @staticmethod
    def f(x):
        # 静态方法不会自动接收实例或类
        return x

    @classmethod
    def g(cls, x):
        # cls 是绑定进来的类对象
        return cls, x
```

访问：

```python
c = C()
print(c.f(1))  # 1
print(c.g(1))  # (<class '__main__.C'>, 1)
```

`staticmethod` 的描述符逻辑大致是“原样返回函数”。`classmethod` 的描述符逻辑大致是“把类对象绑定为第一个参数”。

## 7. `__set_name__`

描述符可以知道自己被绑定到哪个类属性名：

```python
class Field:
    def __set_name__(self, owner, name):
        # owner 是拥有该字段的类，name 是类属性名
        self.name = name
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)

class User:
    name = Field()

u = User()
u.name = "Alice"
print(u.name)
```

`__set_name__` 在类创建时调用。它让描述符不需要手动写字段名。

## 8. 校验字段

描述符适合复用字段校验逻辑：

```python
class Positive:
    def __set_name__(self, owner, name):
        self.storage_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.storage_name)

    def __set__(self, instance, value):
        # value 是用户赋给字段的新对象
        if value <= 0:
            raise ValueError("value must be positive")
        setattr(instance, self.storage_name, value)

class Product:
    price = Positive()
    stock = Positive()

p = Product()
p.price = 10
p.stock = 5
```

这里 `Positive` 是可复用描述符。它不关心自己被用在 `price` 还是 `stock`，字段名由 `__set_name__` 注入。

## 9. 描述符查找优先级

简化版属性查找顺序：

1. 数据描述符。
2. 实例字典。
3. 非数据描述符或普通类属性。
4. `__getattr__` 后备。

这解释了很多现象：

```python
class C:
    @property
    def x(self):
        return "property"

c = C()
c.__dict__["x"] = "instance"
print(c.x)  # property
```

`property` 是数据描述符，优先于实例字典。

普通方法是非数据描述符，因此可以被实例属性遮蔽：

```python
class C:
    def f(self):
        return "method"

c = C()
c.f = "instance value"
print(c.f)  # instance value
```

## 10. 检查表

遇到描述符问题，按下面问：

1. 这个对象是否定义了 `__get__`、`__set__` 或 `__delete__`？
2. 它是否作为类属性存在？
3. 它是数据描述符还是非数据描述符？
4. 当前访问是通过实例，还是通过类？
5. `instance` 和 `owner` 分别是什么？
6. 实例字典是否能遮蔽它？
7. 是否需要 `__set_name__` 获取字段名？

最小心智模型：

1. 描述符是控制属性访问的对象。
2. 描述符必须放在类上才参与属性协议。
3. `property` 是描述符。
4. 普通函数作为类属性时也是描述符。
5. 方法绑定来自函数描述符的 `__get__`。
6. 数据描述符优先于实例字典。
