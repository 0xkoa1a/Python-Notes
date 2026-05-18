# 并发、异步与性能模型

这一层的目标是理解 Python 的性能边界和并发选择。

后续笔记建议覆盖：

1. GIL
2. CPU-bound 与 IO-bound
3. 线程
4. 进程
5. `asyncio`
6. task、取消、超时与异常传播
7. profiling
8. NumPy / PyTorch 的性能边界
9. C / Rust extension

核心信念：Python 适合做调度层、胶水层和实验层；性能关键路径需要选择合适的执行模型。
