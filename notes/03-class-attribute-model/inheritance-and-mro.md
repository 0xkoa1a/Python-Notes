# 继承、MRO 与多重继承

继承不是为了把代码按生物分类树排起来。Python 中继承的核心，是复用行为、表达替换关系，以及让属性查找沿 MRO 继续前进。

**MRO 是类属性查找的线性顺序；`super()` 不是“调用父类”，而是“沿当前 MRO 找下一个实现”。**

理解这句话，多重继承和 mixin 才会从魔法变成可控工具。

## 1. 基本继承

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def bark(self):
        return "woof"

d = Dog()
print(d.speak()) # 来自 Animal
print(d.bark())  # 来自 Dog
```

`Dog` 继承 `Animal`，所以实例属性查找在 `Dog` 找不到时，会继续到 `Animal`。

检查关系：

```python
print(issubclass(Dog, Animal)) # True
print(isinstance(d, Animal))   # True
```

## 2. 覆盖方法

子类可以覆盖基类方法：

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "woof"

print(Dog().speak())  # woof
```

覆盖不是删除基类方法。它只是让属性查找先在子类找到 `speak`，因此不再继续往基类找。

## 3. MRO

每个类都有方法解析顺序：

```python
class A:
    pass

class B(A):
    pass

class C(B):
    pass

print(C.__mro__)
```

输出类似：

```text
(<class '__main__.C'>, <class '__main__.B'>, <class '__main__.A'>, <class 'object'>)
```

属性查找会沿这个顺序进行。

```python
class A:
    x = "A"

class B(A):
    x = "B"

class C(B):
    pass

print(C().x)  # B
```

## 4. `super()` 的真实含义

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        base = super().speak()
        return base + " woof"
```

`super()` 不是简单地“调用父类”。更准确地说，它创建一个代理对象，从当前类之后的 MRO 位置继续查找。

在 `Dog.speak` 中：

```python
super().speak()
```

表示：在 `Dog.__mro__` 中，从 `Dog` 后面开始找 `speak`。

这在单继承里看起来像父类调用，在多重继承里才显出真正含义。

## 5. 多重继承

```python
class A:
    def run(self):
        return "A"

class B:
    def run(self):
        return "B"

class C(A, B):
    pass

print(C.__mro__)
print(C().run())  # A
```

`C(A, B)` 的 MRO 会先找 `A`，再找 `B`。所以 `run` 来自 `A`。

多重继承不是不能用，但必须保持 MRO 可理解。

## 6. 钻石继承与协作式 `super`

```python
class Root:
    def process(self):
        print("Root")

class A(Root):
    def process(self):
        print("A")
        super().process()

class B(Root):
    def process(self):
        print("B")
        super().process()

class C(A, B):
    def process(self):
        print("C")
        super().process()

C().process()
```

输出：

```text
C
A
B
Root
```

`Root` 只调用一次，因为 MRO 是线性的：

```python
print(C.__mro__)  # C, A, B, Root, object
```

关键点：所有类都用 `super()`，而不是硬编码某个父类。

## 7. 协作式初始化

多重继承中，`__init__` 也应协作：

```python
class Base:
    def __init__(self, **kwargs):
        # kwargs 是上游类没有消费完的关键字参数
        super().__init__(**kwargs)

class HasName(Base):
    def __init__(self, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)

class HasAge(Base):
    def __init__(self, age, **kwargs):
        self.age = age
        super().__init__(**kwargs)

class User(HasName, HasAge):
    pass

u = User(name="Alice", age=20)
```

每一层消费自己认识的参数，再把剩余参数交给 MRO 的下一个类。

这类代码要求所有参与者遵守同一个协作协议。如果某个类不调用 `super()`，链条就断了。

## 8. Mixin

Mixin 是提供某种小能力的类，通常不单独实例化：

```python
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.to_dict())

class User(JsonMixin):
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"name": self.name}

print(User("Alice").to_json())
```

好的 mixin 通常：

- 名字以 `Mixin` 结尾。
- 只提供小而明确的能力。
- 清楚说明它依赖宿主类提供什么方法或属性。
- 避免复杂状态。

如果 mixin 依赖 `to_dict`，就应该在文档或类型协议中说清楚。

## 9. 继承 vs 组合

继承表达“是一个”：

```python
class Dog(Animal):
    pass
```

组合表达“有一个”：

```python
class UserService:
    def __init__(self, repository):
        self.repository = repository
```

如果只是想复用代码，优先考虑组合。继承会把类放进同一个替换关系和 MRO 中，长期耦合更强。

常见判断：

```text
子类是否能在任何需要父类的地方使用？
```

如果不能，继承关系可能不成立。

## 10. 检查表

遇到继承问题，按下面问：

1. 这是表达替换关系，还是只是复用代码？
2. 当前类的 `__mro__` 是什么？
3. 属性查找会先命中哪个类？
4. `super()` 会沿 MRO 找到谁？
5. 多重继承中的所有类是否都协作调用 `super()`？
6. mixin 依赖宿主类的哪些方法？
7. 组合是否比继承更清楚？

最小心智模型：

1. 继承影响属性查找。
2. MRO 是线性查找顺序。
3. `super()` 沿 MRO 前进，不是固定父类。
4. 多重继承需要协作式设计。
5. mixin 是小能力组合。
6. 组合通常比继承耦合更低。
