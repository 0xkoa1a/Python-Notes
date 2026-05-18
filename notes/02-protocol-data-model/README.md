# 协议与数据模型

这一层的目标是理解 Python 如何用协议把语法连接到对象行为。

后续笔记建议按协议分组，而不是按魔术方法表死背：

1. [表示协议](representation-protocol.md)
2. [布尔与长度协议](truth-length-protocol.md)
3. [容器协议](container-protocol.md)
4. [迭代协议与数据模型](iteration-data-model.md)
5. [调用协议](call-protocol.md)
6. [比较与哈希协议](comparison-hash-protocol.md)
7. [属性访问协议](attribute-access-protocol.md)
8. [描述符协议](descriptor-protocol.md)
9. [对象创建与类创建协议](object-class-creation.md)

核心信念：语法调用协议，协议调用对象。
