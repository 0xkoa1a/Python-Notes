# Python 笔记

Special case 来源于理解的肤浅。深入的理解带来统一和简单。

这个文件是总入口。正式笔记按主题拆分到 `notes/`，可执行实验放到 `labs/`，阶段验收小项目放到 `projects/`，可复用代码片段放到 `snippets/`。

## 运行时模型

- [本层 README](notes/01-runtime-model/README.md)
- [对象模型](notes/01-runtime-model/object-model.md)
- [作用域与名字解析](notes/01-runtime-model/scope-and-binding.md)
- [函数机制](notes/01-runtime-model/functions.md)
- [迭代协议](notes/01-runtime-model/iteration.md)
- [上下文管理器](notes/01-runtime-model/context-manager.md)
- [异常机制](notes/01-runtime-model/exceptions.md)

## 协议与数据模型

- [本层 README](notes/02-protocol-data-model/README.md)
- [表示协议](notes/02-protocol-data-model/representation-protocol.md)
- [布尔与长度协议](notes/02-protocol-data-model/truth-length-protocol.md)
- [容器协议](notes/02-protocol-data-model/container-protocol.md)
- [迭代协议与数据模型](notes/02-protocol-data-model/iteration-data-model.md)
- [调用协议](notes/02-protocol-data-model/call-protocol.md)
- [比较与哈希协议](notes/02-protocol-data-model/comparison-hash-protocol.md)
- [属性访问协议](notes/02-protocol-data-model/attribute-access-protocol.md)
- [描述符协议](notes/02-protocol-data-model/descriptor-protocol.md)
- [对象创建与类创建协议](notes/02-protocol-data-model/object-class-creation.md)

## 类与属性模型

- [本层 README](notes/03-class-attribute-model/README.md)
- 类对象与实例对象
- 类属性与实例属性
- 方法绑定
- `property`
- 继承与 MRO
- `dataclass`
- `abc` 与 `Protocol`

## 模块、导入与工程模型

- [本层 README](notes/04-modules-engineering-model/README.md)
- 模块对象
- import 机制
- 包与 `__init__.py`
- 脚本入口与 `python -m`
- 循环导入
- 项目结构
- 测试、配置、日志、CLI

## 类型标注与静态分析

- [本层 README](notes/05-typing-static-analysis/README.md)
- 基础类型标注
- 泛型
- `Protocol`
- `TypedDict`
- 类型收窄
- mypy / pyright
- 渐进式类型系统

## 标准库能力

- [本层 README](notes/06-stdlib-capabilities/README.md)
- 数据结构
- 迭代与函数式工具
- 路径、文件与系统
- 文本与数据格式
- 日志、配置与 CLI
- 调试与检查

## 并发、异步与性能模型

- [本层 README](notes/07-concurrency-performance/README.md)
- GIL
- CPU-bound 与 IO-bound
- 线程、进程与 asyncio
- 任务、取消与超时
- profiling
- C / Rust extension 边界

## 生态与项目实践

- [本层 README](notes/08-ecosystem-projects/README.md)
- NumPy / Pandas
- PyTorch
- FastAPI
- SQLAlchemy
- Pydantic
- pytest
- packaging

## 实验室

`labs/` 用于放置 notebook 或临时实验。实验结论沉淀后，再回写到对应 Markdown 笔记。

## 阶段项目

`projects/` 用于放置每一层的综合练习。项目不追求大，但要能检验这一层的核心模型是否真的理解。

## 代码片段

`snippets/` 用于放置可复用的小脚本、小示例和最小复现。
