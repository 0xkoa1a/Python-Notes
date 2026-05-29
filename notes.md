# Python 笔记

Special case 来源于理解的肤浅。深入的理解带来统一和简单。

这个文件是总入口。正式笔记按主题拆分到 `notes/`，章节综合练习放到 `projects/`，可复用代码片段放到 `snippets/`。

## 运行时模型

- [本层 README](notes/01-runtime-model/README.md)
- [对象模型](notes/01-runtime-model/object-model.md)
- [作用域与名字解析](notes/01-runtime-model/scope-and-binding.md)
- [函数机制](notes/01-runtime-model/functions.md)
- [迭代运行时与生成器](notes/01-runtime-model/iteration.md)
- [上下文管理器](notes/01-runtime-model/context-manager.md)
- [异常机制](notes/01-runtime-model/exceptions.md)

## 类与对象模型

- [本层 README](notes/02-class-object-model/README.md)
- [类对象与实例对象](notes/02-class-object-model/class-and-instance-objects.md)
- [类属性与实例属性](notes/02-class-object-model/class-and-instance-attributes.md)
- [方法绑定与 `self`](notes/02-class-object-model/method-binding-and-self.md)
- [`property`](notes/02-class-object-model/property.md)
- [继承、MRO 与多重继承](notes/02-class-object-model/inheritance-and-mro.md)
- [`dataclass`](notes/02-class-object-model/dataclass.md)
- [`slots`](notes/02-class-object-model/slots.md)
- [`abc` 与 `Protocol`](notes/02-class-object-model/abc-and-protocol.md)

## 数据模型协议

- [本层 README](notes/03-data-model-protocols/README.md)
- [表示协议](notes/03-data-model-protocols/representation-protocol.md)
- [布尔与长度协议](notes/03-data-model-protocols/truth-length-protocol.md)
- [容器协议](notes/03-data-model-protocols/container-protocol.md)
- [自定义类型的迭代协议](notes/03-data-model-protocols/iteration-data-model.md)
- [调用协议](notes/03-data-model-protocols/call-protocol.md)
- [比较与哈希协议](notes/03-data-model-protocols/comparison-hash-protocol.md)
- [属性访问协议](notes/03-data-model-protocols/attribute-access-protocol.md)
- [描述符协议](notes/03-data-model-protocols/descriptor-protocol.md)
- [对象创建与类创建协议](notes/03-data-model-protocols/object-class-creation.md)

## 模块、导入与工程模型

- [本层 README](notes/04-modules-engineering-model/README.md)
- [模块对象](notes/04-modules-engineering-model/module-objects.md)
- [`sys.path`](notes/04-modules-engineering-model/sys-path.md)
- [`sys.modules`](notes/04-modules-engineering-model/sys-modules.md)
- [包与 `__init__.py`](notes/04-modules-engineering-model/packages-and-init.md)
- [绝对导入与相对导入](notes/04-modules-engineering-model/absolute-and-relative-imports.md)
- [`python file.py` 与 `python -m package.module`](notes/04-modules-engineering-model/script-vs-module-execution.md)
- [循环导入](notes/04-modules-engineering-model/circular-imports.md)
- [项目结构](notes/04-modules-engineering-model/project-structure.md)
- [测试、配置、日志与 CLI](notes/04-modules-engineering-model/tests-config-logging-cli.md)

## 类型标注与静态分析

- [本层 README](notes/05-typing-static-analysis/README.md)
- [基础类型标注](notes/05-typing-static-analysis/basic-annotations.md)
- [`None` 与可选类型](notes/05-typing-static-analysis/none-and-optional.md)
- [泛型](notes/05-typing-static-analysis/generics.md)
- [`Callable`](notes/05-typing-static-analysis/callable-types.md)
- [`TypedDict`](notes/05-typing-static-analysis/typed-dict.md)
- [`Protocol`](notes/05-typing-static-analysis/protocol.md)
- [类型收窄](notes/05-typing-static-analysis/type-narrowing.md)
- [mypy / pyright](notes/05-typing-static-analysis/mypy-and-pyright.md)
- [渐进式类型系统](notes/05-typing-static-analysis/gradual-typing.md)

## 标准库能力

- [本层 README](notes/06-stdlib-capabilities/README.md)
- [数据结构](notes/06-stdlib-capabilities/data-structures.md)
- [迭代与函数式工具](notes/06-stdlib-capabilities/iteration-functional-tools.md)
- [路径、文件与系统](notes/06-stdlib-capabilities/paths-files-system.md)
- [进程与系统交互](notes/06-stdlib-capabilities/process-system-interaction.md)
- [文本与数据格式](notes/06-stdlib-capabilities/text-data-formats.md)
- [时间、随机与数学](notes/06-stdlib-capabilities/time-random-math.md)
- [日志、配置与 CLI](notes/06-stdlib-capabilities/logging-config-cli.md)
- [调试与检查](notes/06-stdlib-capabilities/debugging-inspection.md)
- [测试辅助](notes/06-stdlib-capabilities/testing-helpers.md)

## 并发、异步与性能模型

- [本层 README](notes/07-concurrency-performance/README.md)
- [GIL](notes/07-concurrency-performance/gil.md)
- [CPU-bound 与 IO-bound](notes/07-concurrency-performance/cpu-bound-vs-io-bound.md)
- [线程](notes/07-concurrency-performance/threading.md)
- [进程](notes/07-concurrency-performance/multiprocessing.md)
- [`asyncio`](notes/07-concurrency-performance/asyncio.md)
- [task、取消、超时与异常传播](notes/07-concurrency-performance/tasks-cancellation-timeouts.md)
- [profiling](notes/07-concurrency-performance/profiling.md)
- [NumPy / PyTorch 的性能边界](notes/07-concurrency-performance/numpy-pytorch-boundaries.md)
- [C / Rust extension](notes/07-concurrency-performance/c-rust-extension.md)

## 生态与项目实践

- [本层 README](notes/08-ecosystem-projects/README.md)
- NumPy / Pandas
- PyTorch
- FastAPI
- SQLAlchemy
- Pydantic
- pytest
- packaging

## 阶段项目

`projects/` 用于放置每一层的综合练习。项目不追求大，但要能检验这一层的核心模型是否真的理解。

- [第一章：Mini Pipeline](projects/01-runtime-model/mini_pipeline/README.md)

## 代码片段

`snippets/` 用于放置可复用的小脚本、小示例和最小复现。
