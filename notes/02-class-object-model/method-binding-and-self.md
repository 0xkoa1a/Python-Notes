# 方法绑定与 `self`

`self` 不是关键字，也不是魔法变量。它只是一个普通参数名。真正的机制是方法绑定。

**函数对象放在类上时会作为描述符参与属性访问；通过实例访问方法时，Python 自动把实例和函数绑定成一个 bound method；调用 bound method 时实例会作为第一个参数传入。**

这就是 `obj.method()` 为什么能少写一个参数的原因。

## 1. 类里的函数

```python
class User:
    def greet(self):
        return f"hello, {self.name}"
```

类体执行后，`greet` 是保存在类命名空间里的函数对象：

```python
print(User.__dict__["greet"]) # 函数对象
```

它还不是“绑定到某个实例的方法”。它只是一个函数，第一参数名叫 `self`。

## 2. 通过实例访问会绑定

```python
u = User()
u.name = "Alice"

method = u.greet

print(method)      # bound method
print(method())    # hello, Alice
```

`method` 是绑定方法对象。它保存了两样东西：

- 原始函数：`User.greet`
- 绑定实例：`u`

可以观察：

```python
print(method.__func__) # 原始函数对象 User.greet
print(method.__self__) # 被绑定的实例 u
```

`method()` 等价于：

```python
User.greet(u)
```

## 3. 通过类访问不会绑定实例

```python
User.greet(u)  # 显式传入实例
```

如果直接调用：

```python
User.greet()
```

会报缺少 `self` 参数。因为通过类访问得到的是函数对象，没有自动绑定实例。

通过实例访问：

```python
u.greet()
```

Python 自动绑定 `u`，所以不需要手动传。

## 4. `self` 可以换名字，但不要换

```python
class User:
    def greet(this):
        return "hello"
```

这可以运行，因为 `self` 只是参数名。但不要这样写。Python 社区约定实例方法第一个参数叫 `self`，类方法第一个参数叫 `cls`。

约定不是语法要求，但它是可读性的基础。

## 5. 实例方法、类方法、静态方法

### 实例方法

```python
class User:
    def greet(self):
        # self 是被绑定的实例对象
        return self.name
```

实例方法需要访问或修改实例状态。

### 类方法

```python
class User:
    default_role = "guest"

    @classmethod
    def with_default_role(cls, name):
        # cls 是被绑定的类对象，可能是 User，也可能是子类
        obj = cls(name)
        obj.role = cls.default_role
        return obj
```

类方法适合作为替代构造器，或者需要尊重子类的工厂方法。

### 静态方法

```python
class User:
    @staticmethod
    def normalize_name(name):
        # 静态方法不会自动接收 self 或 cls
        return name.strip().title()
```

静态方法只是放在类命名空间中的普通工具函数。它不需要实例状态，也不需要类对象。

## 6. 什么时候用哪种方法

问一个简单问题：

```text
这个函数需要实例状态吗？
```

需要：实例方法。

```text
这个函数需要类对象，并且应该对继承友好吗？
```

需要：类方法。

```text
这个函数只是逻辑上归属于这个类，不需要 self 或 cls 吗？
```

可以用静态方法。

但不要为了“组织起来”滥用静态方法。如果它和类没有强关系，放在模块级函数更清楚。

## 7. 绑定方法是临时对象

每次访问实例方法，Python 通常会创建一个新的 bound method 对象：

```python
u = User()

print(u.greet is u.greet)  # 通常是 False
```

这不影响语义，因为两个 bound method 都绑定同一个实例和同一个函数：

```python
m1 = u.greet
m2 = u.greet

print(m1.__self__ is m2.__self__) # True
print(m1.__func__ is m2.__func__) # True
```

不要用 `is` 判断两次方法访问是否“同一个方法”。如果需要比较，比较 `__self__` 和 `__func__`。

## 8. 方法作为回调

绑定方法可以像普通函数一样传递：

```python
class Counter:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

c = Counter()
callback = c.inc  # callback 保存了 c 这个实例
callback()

print(c.count)  # 1
```

`callback` 持有实例引用。因此把绑定方法保存很久，也会让实例保持存活。这在回调、事件系统和缓存中需要注意。

## 9. 检查表

遇到方法相关问题，按下面问：

1. 函数是通过类访问，还是通过实例访问？
2. 得到的是函数对象，还是 bound method？
3. bound method 的 `__self__` 是谁？
4. bound method 的 `__func__` 是哪个函数？
5. 这个方法需要 `self`、`cls`，还是两者都不需要？
6. 类方法是否应该尊重子类？
7. 保存 bound method 是否会延长实例生命周期？

最小心智模型：

1. `self` 是普通参数名。
2. 函数放在类上会参与描述符协议。
3. 通过实例访问方法会产生 bound method。
4. bound method 调用时自动传入实例。
5. 类方法绑定类对象。
6. 静态方法不自动绑定任何对象。
