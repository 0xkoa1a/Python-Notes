# 类属性与实例属性

类属性和实例属性的区别，是 Python OOP 中最常见的误解来源之一。

**类属性保存在类对象上，被所有实例共享；实例属性保存在实例对象上，只属于单个实例；属性查找会先看实例，再看类和基类。**

如果再加上“可变对象共享状态”这一条，很多看似诡异的 bug 都会变得直白。

## 1. 类属性是共享属性

```python
class User:
    species = "human"

alice = User()
bob = User()

print(alice.species) # human
print(bob.species)   # human
```

`species` 存在类对象 `User` 上：

```python
print(User.__dict__["species"]) # human
print(alice.__dict__)           # {}
```

实例访问 `alice.species` 时，实例字典里找不到，于是去类对象上找。

## 2. 实例属性是单个对象状态

```python
class User:
    species = "human"

    def __init__(self, name):
        self.name = name  # name 是实例属性

alice = User("Alice")
bob = User("Bob")

print(alice.__dict__) # {'name': 'Alice'}
print(bob.__dict__)   # {'name': 'Bob'}
```

每个实例有自己的 `name`。修改一个实例不会影响另一个：

```python
alice.name = "Alicia"

print(alice.name) # Alicia
print(bob.name)   # Bob
```

## 3. 实例属性遮蔽类属性

```python
class User:
    role = "guest"

u = User()
print(u.role)  # guest，来自类属性

u.role = "admin"

print(u.role)      # admin，来自实例属性
print(User.role)   # guest，类属性仍然存在
print(u.__dict__)  # {'role': 'admin'}
```

`u.role = "admin"` 没有修改 `User.role`，而是在实例 `u` 的命名空间中创建了一个新绑定。

如果要修改类属性，明确通过类对象：

```python
User.role = "member"
```

## 4. 可变类属性陷阱不是陷阱

```python
class Team:
    members = []

    def add(self, name):
        self.members.append(name)

a = Team()
b = Team()

a.add("Alice")
print(b.members)  # ['Alice']
```

这不是 Python 特殊坑。`members` 是类属性，绑定到一个列表对象。所有实例访问到的都是同一个列表。

图景：

```text
Team.members ───> []
a.members ──────┘
b.members ──────┘
```

正确写法是把每个实例独有的可变状态放进 `__init__`：

```python
class Team:
    def __init__(self):
        self.members = []  # 每次创建实例时创建新列表

    def add(self, name):
        self.members.append(name)
```

## 5. 类属性适合什么

类属性适合保存真正共享的东西：

```python
class HttpStatus:
    OK = 200
    NOT_FOUND = 404
```

或者保存所有实例共享的配置：

```python
class User:
    table_name = "users"
```

或者保存注册表，但要清楚这是全局共享状态：

```python
class Plugin:
    registry = []

    def __init_subclass__(cls):
        # cls 是新创建的子类对象
        Plugin.registry.append(cls)
```

类属性不是不能可变，而是可变类属性必须被设计成共享状态。

## 6. 用类属性做默认值

类属性可以作为默认值来源：

```python
class Parser:
    default_encoding = "utf-8"

    def __init__(self, encoding=None):
        if encoding is None:
            encoding = self.default_encoding
        self.encoding = encoding
```

这样子类可以覆盖默认值：

```python
class LatinParser(Parser):
    default_encoding = "latin-1"

print(LatinParser().encoding)  # latin-1
```

这里通过 `self.default_encoding` 读取，允许实例所属类或子类参与属性查找。通过 `Parser.default_encoding` 读取则会固定使用基类值。

## 7. 属性查找简化顺序

对普通属性而言，可以先用这个简化模型：

```text
实例字典 -> 类字典 -> 基类字典 -> 找不到则 AttributeError
```

示例：

```python
class Base:
    x = "base"

class Child(Base):
    pass

c = Child()
print(c.x)  # base

Child.x = "child"
print(c.x)  # child

c.x = "instance"
print(c.x)  # instance
```

完整属性查找还涉及描述符、`__getattribute__`、`__getattr__`，第三章展开。这里先记住：实例属性、类属性、基类属性不是同一层。

## 8. 检查表

遇到类属性和实例属性问题，按下面问：

1. 属性绑定发生在类体中，还是 `self.xxx = ...` 中？
2. 属性对象是否可变？
3. 这个状态应该被所有实例共享，还是每个实例独有？
4. 赋值是通过实例，还是通过类对象？
5. 实例属性是否遮蔽了类属性？
6. 子类是否需要覆盖默认值？

最小心智模型：

1. 类属性保存在类对象上。
2. 实例属性保存在实例对象上。
3. 实例访问属性时可以找到类属性。
4. 实例赋值通常创建或更新实例属性。
5. 可变类属性意味着共享可变状态。
