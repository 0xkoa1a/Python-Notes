# Python 笔记

Special case 来源于理解的肤浅。深入的理解带来统一和简单。

这个文件是总入口。正式笔记按主题拆分到 `notes/`，可执行实验放到 `labs/`，可复用代码片段放到 `snippets/`。

## 语言核心机制

- [对象模型](notes/01-language-core/object-model.md)
- [作用域与名字解析](notes/01-language-core/scope-and-binding.md)
- [函数机制](notes/01-language-core/functions.md)
- [迭代协议](notes/01-language-core/iteration.md)
- [上下文管理器](notes/01-language-core/context-manager.md)
- [异常机制](notes/01-language-core/exceptions.md)

## 数据模型与魔术方法

- 特殊方法总览
- 属性访问
- 描述符协议
- 类创建机制

## 面向对象的 Python 风格

- 类属性与实例属性
- 方法、property 与 dataclass
- 继承、MRO 与组合
- `abc` 与 `typing.Protocol`

## 类型标注与静态检查

- 基础类型标注
- 泛型
- 结构化类型
- 类型检查器

## 标准库进阶

- `collections`
- `itertools`
- `functools`
- `pathlib`
- `subprocess`
- `logging`
- 并发相关标准库

## 并发、异步与性能模型

- GIL
- 线程、进程与 asyncio
- 性能分析
- C 扩展与系统边界

## 工程化与项目组织

- 项目结构
- 包管理
- 测试
- CLI
- 配置、日志与发布

## 生态与实践专题

- NumPy / Pandas
- Web 后端
- 数据验证
- 自动化脚本
- 实验框架

## 实验室

`labs/` 用于放置 notebook 或临时实验。实验结论沉淀后，再回写到对应 Markdown 笔记。

## 代码片段

`snippets/` 用于放置可复用的小脚本、小示例和最小复现。
