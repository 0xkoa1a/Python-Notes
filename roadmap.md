# Python 进阶路线图

Special case 来源于理解的肤浅。深入的理解带来统一和简单。

这份路线图不追求把 Python 特性列成百科目录，而是围绕少数几个运行模型组织学习。每一层都回答一个问题：**这个机制背后的统一模型是什么？**

正式笔记放在 `notes/`，章节综合练习放在 `projects/`，可复用代码片段放在 `snippets/`。

## 总体结构

```text
notes/
├─ 01-runtime-model/
├─ 02-class-object-model/
├─ 03-data-model-protocols/
├─ 04-modules-engineering-model/
├─ 05-typing-static-analysis/
├─ 06-stdlib-capabilities/
├─ 07-concurrency-performance/
└─ 08-ecosystem-projects/
```

`notes/` 是长期沉淀，`projects/` 是阶段性综合练习。二者使用同一套编号，方便互相映射。

## 第一层：运行时模型

目标：从“会写 Python”进入“知道 Python 为什么这样运行”。

这一层建立 Python 的底层心智模型：

- 对象模型：对象、身份、类型、值、引用、可变性、浅拷贝、深拷贝。
- 名字模型：命名空间、绑定、LEGB、闭包、`global`、`nonlocal`、late binding。
- 函数模型：函数对象、调用帧、参数绑定、默认参数、函数属性、装饰器。
- 迭代运行时：可迭代对象、迭代器、生成器、惰性计算、`yield from`。
- 资源模型：`with`、上下文管理器、`__enter__`、`__exit__`、`contextlib`。
- 异常模型：异常对象、传播、匹配、异常链、`raise from`、`finally` 收束。

核心信念：**默认参数、闭包 late binding、浅拷贝共享内部对象、生成器一次性消费，都不是 special case。它们都是对象、名字、作用域、协议和控制流模型的自然结果。**

可验证现象：

- `id`、`is`、`==`、aliasing、copy、deepcopy。
- 闭包 cell、late binding、默认参数求值时机。
- 生成器暂停与恢复、迭代器消费状态。
- `raise from`、traceback、异常链。
- `with` 与 `try/finally` 的等价关系。

阶段项目：写一个 mini 数据处理 pipeline：文件读取使用上下文管理器，数据流使用生成器，错误使用自定义异常和异常链表达。

## 第二层：类与对象模型

目标：先理解 Python 的类、实例、属性、方法和继承，再进入各种魔术方法。

这一层建立 Python OOP 的日常模型：

重点包括：

- 类对象与实例对象。
- 类属性与实例属性。
- 实例方法、类方法、静态方法。
- 绑定方法与 `self` 的来源。
- `property` 与受控属性访问。
- 继承、MRO、多重继承。
- 组合优先于继承。
- `dataclass`。
- `slots`。
- `abc` 与抽象基类。
- `typing.Protocol` 与结构化接口的运行时位置。

核心信念：**Python 的类首先是运行时对象，其次才是“类型模板”。属性查找、方法绑定、描述符和 MRO 构成了 Python OOP 的真实模型。**

阶段项目：写一个配置对象系统：支持默认值、属性校验、继承覆盖、序列化，并比较手写类、`dataclass`、`Protocol` 的取舍。

## 第三层：数据模型协议

目标：理解 Python 如何用协议把语法连接到对象行为。

这一层建立在第二层的类模型之上。不要按“魔术方法表”死背，而要按协议分组：

- 表示协议：`__repr__`、`__str__`、`__format__`。
- 布尔与长度协议：`__bool__`、`__len__`。
- 容器协议：`__contains__`、`__getitem__`、`__setitem__`、切片。
- 自定义类型的迭代协议：`__iter__`、`__next__`、`__reversed__`、`__getitem__` fallback。
- 调用协议：`__call__`。
- 比较协议：`__eq__`、`__lt__` 等。
- 哈希协议：`__hash__` 与不可变性。
- 属性访问协议：`__getattr__`、`__getattribute__`、`__setattr__`。
- 描述符协议：`__get__`、`__set__`、`__delete__`。
- 对象创建协议：`__new__`、`__init__`。
- 类创建协议：metaclass、`__init_subclass__`、class decorator。

核心信念：**Python 的多态不是主要靠继承层次，而是靠对象是否实现某个协议。语法调用协议，协议调用对象。**

阶段项目：写一个小型 `RecordSet` 容器，支持 repr、长度、索引、切片、迭代、过滤和比较。

## 第四层：模块、导入与工程模型

目标：理解 Python 项目如何从文件变成可运行的模块图。

这一层应该独立出来，因为大量工程问题都来自 import 机制理解不深。

重点包括：

- 模块也是对象。
- 文件如何加载为模块对象。
- `sys.path`。
- `sys.modules` 与 import 缓存。
- 包与 `__init__.py`。
- 绝对导入与相对导入。
- `python file.py` 与 `python -m package.module`。
- 脚本入口与 `if __name__ == "__main__"`。
- 循环导入。
- 包结构设计。
- `pyproject.toml`。
- 虚拟环境与依赖管理。
- 测试目录组织。
- CLI 入口。
- 配置、日志、错误边界。

核心信念：**import 不是文本粘贴，而是模块对象的创建、缓存和名字绑定。工程结构的很多问题，本质上是模块图和依赖方向的问题。**

阶段项目：把一个单文件脚本整理成可测试、可运行、可安装的小包，包含 CLI、配置、日志和测试。

## 第五层：类型标注与静态分析

目标：理解 Python 类型标注是在动态对象模型上叠加的可选静态约束。

重点包括两条线。

第一条线是表达接口：

- 基础类型：`list[int]`、`dict[str, int]`、`tuple[int, str]`。
- 可选类型：`T | None`。
- 函数类型：`Callable`。
- 泛型：`TypeVar`、`Generic`。
- 结构化数据：`TypedDict`。
- 字面量类型：`Literal`。
- 类型别名。
- `Protocol`。
- `Self`。

第二条线是理解检查器：

- 类型标注默认不改变运行时行为。
- mypy / pyright 检查的是静态近似模型。
- nominal typing 与 structural typing。
- duck typing 与 `Protocol` 的关系。
- 类型收窄：`isinstance`、`assert x is not None`。
- 渐进式类型系统：哪里值得标，哪里不值得过度标。

核心信念：**类型标注不是为了把 Python 变成 Java 或 Rust，而是为了在动态语言中给大型项目提供可读、可检查、可维护的接口边界。**

阶段项目：给一个已有小工具补全类型标注，并通过 pyright 或 mypy 检查。

## 第六层：标准库能力

目标：把标准库按“解决什么工程问题”组织，而不是按模块名背目录。

重点分组：

- 数据结构：`collections`、`heapq`、`bisect`、`array`。
- 迭代与函数式工具：`itertools`、`functools`、`operator`。
- 路径与文件系统：`pathlib`、`os`、`shutil`、`tempfile`。
- 进程与系统交互：`subprocess`、`sys`、`platform`。
- 文本与数据格式：`re`、`json`、`csv`、`tomllib`、`pickle`。
- 时间、随机与数学：`datetime`、`time`、`random`、`math`、`statistics`。
- 日志与配置：`logging`、`argparse`、`configparser`。
- 调试与检查：`pdb`、`traceback`、`inspect`、`dis`。
- 并发基础：`threading`、`multiprocessing`、`concurrent.futures`、`asyncio`。
- 测试辅助：`unittest.mock`、`doctest`。

核心信念：**标准库不是杂物间，而是一套工程能力工具箱。学习标准库的正确单位不是模块名，而是任务能力。**

阶段项目：写一个命令行文件整理工具：递归扫描、规则匹配、dry-run、日志、错误报告、配置文件。

## 第七层：并发、异步与性能模型

目标：理解 Python 的性能边界和并发选择。

重点包括：

- GIL 是什么，限制什么，不限制什么。
- CPU-bound 与 IO-bound。
- 线程适合什么。
- 进程适合什么。
- `asyncio` 适合什么。
- 协程、事件循环、awaitable、task。
- `concurrent.futures`。
- `asyncio.TaskGroup`。
- 取消、超时、异常传播。
- `timeit`、`cProfile`、`tracemalloc`。
- NumPy / PyTorch 为什么快。
- C 扩展、Rust extension、pybind11、Cython 的位置。

核心信念：**Python 适合做调度层、胶水层和实验层；性能关键路径要么交给高效库，要么换执行模型。**

阶段项目：写一个并发下载器或批量任务执行器，支持线程模式、async 模式、超时、重试、日志和性能统计。

## 第八层：生态与项目实践

目标：把前面的模型应用到真实生态工具和项目中。

重点包括：

- NumPy / Pandas：向量化、数据结构、缺失值、IO。
- PyTorch：张量、autograd、模块、训练循环。
- FastAPI：类型标注、依赖注入、Pydantic、异步边界。
- SQLAlchemy：对象关系映射、session、事务。
- Pydantic：运行时数据验证。
- pytest：fixture、参数化、mock、临时目录。
- rich / typer：CLI 体验。
- packaging：构建、发布、版本。
- Jupyter：探索、可视化、实验记录。

核心信念：**高级库不是黑盒。它们大量复用 Python 的对象模型、协议、类型标注、上下文管理器、装饰器和工程结构。**

阶段项目：做一个完整小应用：CLI 或 Web API，包含项目结构、类型标注、测试、日志、配置、错误处理和文档。

## 写作规范

每篇正式笔记建议遵循这个结构：

```text
# 主题名

## 核心模型
## 错误直觉
## 正确理解
## 关键例子
## 与其他主题的关系
## 检查表
## 最小心智模型
```

代码示例要承担解释责任：

- 如果示例引入了新对象，注释说明它是什么。
- 如果示例依赖协议，注释说明协议入口在哪里。
- 如果示例展示异常、闭包、迭代器、上下文管理器等运行时对象，注释说明关键变量绑定到什么。
- 注释要解释不直观的运行时含义，不要重复代码表面含义。

例如：

```python
try:
    ...
except* ValueError as group:
    # group 是只包含 ValueError 的 ExceptionGroup 子组
    # group.exceptions 是这个子组中具体异常对象组成的元组
    handle_values(group.exceptions)
except* TypeError as group:
    # 这里的 group 是只包含 TypeError 的 ExceptionGroup 子组
    handle_types(group.exceptions)
```

强调性文字使用 **加粗**，不使用引用块。

## 学习节奏

推荐每一层按这个节奏推进：

1. 写正式笔记，先建立统一模型。
2. 在 `projects/` 做阶段项目，用测试把行为要求固定下来。
3. 实现项目时做必要的最小验证，把稳定结论回写到笔记。
4. 回顾哪些现象曾经像 special case，现在能否被统一解释。

真正的进步不是记住更多 Python 小技巧，而是让越来越多现象被越来越少的模型解释。
