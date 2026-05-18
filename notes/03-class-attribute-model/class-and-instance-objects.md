# 类对象与实例对象

Python 的类不是编译期模板，而是运行时对象。实例也不是类的“复制品”，而是由类创建出来、带有自己状态的对象。

**类对象负责保存共享行为和类级状态；实例对象负责保存单个对象的状态；实例通过自己的类参与属性查找和方法绑定。**

这条线把 Python OOP 从“类里面写函数”提升到“对象、命名空间、协议共同构成运行时系统”。

## 1. 类也是对象

执行类定义会创建类对象：

```python
class User:
    species = "human"

    def greet(self):
        return "hello"

print(User)        # User 是类对象
print(type(User))  # 默认情况下，类对象由 type 创建
```

类对象可以被绑定到其他名字：

```python
Account = User
print(Account is User)  # True，两个名字绑定到同一个类对象
```

类对象也可以放进容器、作为参数传递、作为返回值：

```python
classes = [User, dict, list]

for cls in classes:
    print(cls.__name__)  # cls 是当前循环中的类对象
```

## 2. 实例由类对象创建

调用类对象会创建实例：

```python
class User:
    def __init__(self, name):
        self.name = name

u = User("Alice")

print(u)          # u 是实例对象
print(type(u))    # <class '__main__.User'>
print(u.__class__) # 实例知道自己的类对象
```

`type(u)` 返回实例所属的类对象。`u.__class__` 通常也是同一个类对象。

统一图景：

```text
name User ───> class object User
                 │
                 └── creates
                      │
name u ───────> instance object
```

## 3. 类命名空间与实例命名空间

类对象有自己的命名空间：

```python
class User:
    species = "human"

print(User.__dict__["species"])  # human
```

实例通常也有自己的命名空间：

```python
u = User()
u.name = "Alice"

print(u.__dict__)  # {'name': 'Alice'}
```

类命名空间保存共享属性和函数对象；实例命名空间保存单个实例的状态。

```python
class User:
    species = "human"

    def __init__(self, name):
        self.name = name

u = User("Alice")

print(User.__dict__["species"]) # 类属性
print(u.__dict__["name"])       # 实例属性
```

## 4. 实例不是类字典的复制

创建实例不会把类属性复制到实例字典：

```python
class User:
    species = "human"

u = User()

print(u.__dict__)  # {}
print(u.species)   # human，来自类对象
```

`u.species` 能访问，是因为属性查找会从实例扩展到类，而不是因为实例里有一份 `species`。

如果给实例赋值：

```python
u.species = "robot"

print(u.__dict__)  # {'species': 'robot'}
print(u.species)   # robot，实例属性遮蔽类属性
print(User.species) # human，类属性没有变
```

这解释了很多“为什么我改了这个对象，别的对象没变”的现象。

## 5. 类保存行为，实例保存状态

普通方法函数保存在类对象上：

```python
class User:
    def greet(self):
        return f"hello, {self.name}"

u = User()
u.name = "Alice"

print("greet" in User.__dict__) # True，函数对象在类命名空间
print("greet" in u.__dict__)    # False，实例不保存方法副本
```

实例调用方法时，Python 通过描述符协议把实例绑定进去：

```python
print(u.greet())  # hello, Alice
```

实例没有复制方法。所有实例共享类上的函数对象，只是调用时绑定不同的 `self`。

## 6. `isinstance` 与 `issubclass`

检查实例和类的关系：

```python
class Animal:
    pass

class Dog(Animal):
    pass

d = Dog()

print(isinstance(d, Dog))    # True，d 是 Dog 的实例
print(isinstance(d, Animal)) # True，Dog 继承 Animal
print(issubclass(Dog, Animal)) # True，Dog 是 Animal 的子类
```

`isinstance(obj, cls)` 问的是对象是否符合某个类层次。它不等于 `type(obj) is cls`：

```python
print(type(d) is Dog)       # True
print(type(d) is Animal)    # False
print(isinstance(d, Animal)) # True
```

如果你想尊重继承，使用 `isinstance`。如果你必须判断精确类型，才使用 `type(obj) is cls`。

## 7. 类对象可以被动态修改

类是运行时对象，所以可以动态加属性：

```python
class User:
    pass

def greet(self):
    return f"hello, {self.name}"

User.greet = greet  # 把函数对象绑定到类属性

u = User()
u.name = "Alice"
print(u.greet())  # hello, Alice
```

这不是推荐的日常风格，但它说明：类定义只是创建类对象的一种方式，之后类对象仍然可以被修改。

框架和装饰器常利用这一点。不过工程代码中，动态修改类会增加阅读成本，要有明确收益才使用。

## 8. 检查表

理解类和实例时，按下面问：

1. 当前名字绑定到类对象，还是实例对象？
2. 状态保存在类命名空间，还是实例命名空间？
3. 这个属性是共享的，还是每个实例独有的？
4. 方法函数存在哪里？
5. 调用方法时哪个实例会被绑定为 `self`？
6. 是否需要尊重继承？如果需要，用 `isinstance`。

最小心智模型：

1. 类是运行时对象。
2. 实例由类对象创建。
3. 类保存共享行为和类级状态。
4. 实例保存单个对象状态。
5. 实例不会复制类字典。
6. 方法绑定让类上的函数服务于不同实例。
