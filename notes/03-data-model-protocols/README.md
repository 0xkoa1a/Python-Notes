# 数据模型协议

这一层的目标是理解 Python 如何用数据模型协议把语法连接到对象行为。

第二章已经讲过类、实例、属性、方法和继承。这里开始进入更底层的协议入口：当你写 `repr(obj)`、`obj[key]`、`obj(...)`、`obj.name` 时，Python 到底会调用对象上的哪些方法。

建议按协议分组阅读，而不是按魔术方法表死背：

1. [表示协议](representation-protocol.md)
2. [布尔与长度协议](truth-length-protocol.md)
3. [容器协议](container-protocol.md)
4. [自定义类型的迭代协议](iteration-data-model.md)
5. [调用协议](call-protocol.md)
6. [比较与哈希协议](comparison-hash-protocol.md)
7. [属性访问协议](attribute-access-protocol.md)
8. [描述符协议](descriptor-protocol.md)
9. [对象创建与类创建协议](object-class-creation.md)

核心信念：**语法调用协议，协议调用对象。魔术方法不是零散技巧，而是对象接入 Python 语言生态的接口。**
