# 类与对象模型

这一层的目标是先建立 Python 面向对象的基本模型：类对象、实例对象、属性、方法绑定、继承、组合，以及常用的类工具。

这一层不急着展开所有魔术方法。先理解普通类如何工作，再进入下一层的数据模型协议，会更自然。

建议阅读顺序：

1. [类对象与实例对象](class-and-instance-objects.md)
2. [类属性与实例属性](class-and-instance-attributes.md)
3. [方法绑定与 `self`](method-binding-and-self.md)
4. [`property`](property.md)
5. [继承、MRO 与多重继承](inheritance-and-mro.md)
6. [`dataclass`](dataclass.md)
7. [`slots`](slots.md)
8. [`abc` 与 `typing.Protocol`](abc-and-protocol.md)

核心信念：**Python 的类首先是运行时对象，其次才是类型模板。属性查找、方法绑定和继承关系构成了 Python OOP 的日常模型；描述符和魔术方法是下一层对这个模型的协议化展开。**
