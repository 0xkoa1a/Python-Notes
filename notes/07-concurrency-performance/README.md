# 并发、异步与性能模型

这一层的目标是理解 Python 的性能边界和并发选择。

后续笔记建议覆盖：

1. [GIL](gil.md)
2. [CPU-bound 与 IO-bound](cpu-bound-vs-io-bound.md)
3. [线程](threading.md)
4. [进程](multiprocessing.md)
5. [`asyncio`](asyncio.md)
6. [task、取消、超时与异常传播](tasks-cancellation-timeouts.md)
7. [profiling](profiling.md)
8. [NumPy / PyTorch 的性能边界](numpy-pytorch-boundaries.md)
9. [C / Rust extension](c-rust-extension.md)

核心信念：Python 适合做调度层、胶水层和实验层；性能关键路径需要选择合适的执行模型。
