# 类型标注与静态分析

这一层的目标是理解 Python 类型标注如何在动态对象模型上提供可选的静态约束。

后续笔记建议覆盖：

1. [基础类型标注](basic-annotations.md)
2. [`None` 与可选类型](none-and-optional.md)
3. [泛型](generics.md)
4. [`Callable`](callable-types.md)
5. [`TypedDict`](typed-dict.md)
6. [`Protocol`](protocol.md)
7. [类型收窄](type-narrowing.md)
8. [mypy / pyright](mypy-and-pyright.md)
9. [渐进式类型系统](gradual-typing.md)

核心信念：类型标注是接口边界，不是运行时强制类型系统。
