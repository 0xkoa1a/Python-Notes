# Config Object System

这是第三章“类与属性模型”的阶段项目。它不是一个完整配置库，而是一个围绕配置对象设计的练习：你要用类属性、实例属性、`property`、继承、`dataclass`、`slots` 和 `Protocol` 建立一套小而清楚的对象系统。

**这个项目的重点不是写更多类，而是看清：类对象保存默认行为，实例对象保存当前状态，属性访问把外部接口和内部实现连接起来。**

## 你要实现什么

公共接口固定为：

```python
from config_object_system import (
    AppConfig,
    DevelopmentConfig,
    ProductionConfig,
    DataclassAppConfig,
    ConfigError,
    ValidationError,
    SupportsConfigExport,
    dump_config,
)
```

测试运行命令：

```bash
uv run pytest projects/03-class-attribute-model/config_object_system/tests
```

当前骨架故意不会通过测试。你的任务是补完 `TODO`，让测试逐步变绿。

## 手写类：`AppConfig`

`AppConfig` 使用类属性表达默认值：

```python
class AppConfig:
    default_host = "127.0.0.1"
    default_port = 8000
    default_debug = False
    default_features = ()
```

构造实例时，默认值应从类属性读取。这样子类覆盖类属性后，父类构造逻辑也能自然使用子类默认值。

要求：

- `host` 必须是非空字符串。
- `port` 必须是 `1..65535` 的整数。
- `debug` 必须是 `bool`，不要把 `1` 当成合法值。
- `features` 构造时接受字符串 iterable，对外暴露为 tuple。
- 实例之间不能共享可变状态。
- `to_dict()` 返回普通可序列化 dict。
- `from_dict()` 是 `classmethod`，必须返回当前 `cls(...)`。
- `with_overrides(**changes)` 返回 `type(self)(...)`，保留子类类型。
- 手写类使用 `__slots__`，不能随意添加未知实例属性。

## 继承覆盖

`DevelopmentConfig` 和 `ProductionConfig` 通过覆盖类属性改变默认值：

```python
class DevelopmentConfig(AppConfig):
    default_debug = True
    default_features = ("reload",)


class ProductionConfig(AppConfig):
    default_host = "0.0.0.0"
    default_port = 80
    default_debug = False
```

这里的关键不是“子类有不同默认值”，而是：**默认值来自类属性查找，而不是父类构造器中的硬编码常量。**

## `property` 校验

`host`、`port`、`debug`、`features` 都应通过 `property` 管理。

例如：

```python
config.port = 8080
config.port = 0  # raise ValidationError
```

`property` 的意义是让外部继续使用 `config.port` 这种属性接口，而内部可以加入校验、复制、规范化等逻辑。

## `DataclassAppConfig`

你还要实现一个 `@dataclass(slots=True)` 版本，用来对比手写类：

- 字段和 `AppConfig` 一致。
- 用 `__post_init__` 做运行时校验。
- `features` 也要转换成 tuple，避免共享可变状态。
- 实现 `to_dict()`。

`dataclass` 可以减少样板代码，但它不会自动替你做运行时类型校验。

## `Protocol` 与结构化接口

`SupportsConfigExport` 是一个 `Protocol`，只要求对象有：

```python
def to_dict(self) -> dict[str, object]:
    ...
```

`dump_config(config)` 应接受任何满足这个结构的对象，不要求继承 `AppConfig`。

这用来练习：**接口不一定来自继承，也可以来自对象实际拥有的能力。**

## 学习检查点

实现时请反复问自己：

1. 默认值是从类对象读到的，还是写死在 `__init__` 里的？
2. 实例状态保存在什么属性上？
3. property setter 什么时候被调用？
4. `from_dict()` 里为什么应该使用 `cls`？
5. `with_overrides()` 里为什么应该使用 `type(self)`？
6. 子类覆盖类属性后，父类方法是否仍然尊重子类类型？
7. `dataclass` 帮你生成了什么，又没有帮你生成什么？
8. `Protocol` 表达的是继承关系，还是结构能力？

