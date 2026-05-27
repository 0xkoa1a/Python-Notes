# Mini Pipeline

这是第一章“运行时模型”的阶段项目。它不是给你直接使用的库，而是一个需要你亲手补完的练习。

目标是写一个小型惰性数据处理 pipeline：从文本文件读取记录，逐行解析，按条件过滤，转换记录，最后汇总结果。

**这个项目的重点不是把代码写短，而是让对象、名字、函数、迭代器、上下文管理器和异常链一起工作。**

## 你要实现什么

输入文件中每条有效记录占一行：

```text
Ada,100
Guido,95
Lin,88
```

规则：

- 空行跳过。
- 去掉首尾空白后以 `#` 开头的行跳过。
- 有效行格式为 `name,score`。
- `name` 去掉首尾空白后必须非空。
- `score` 去掉首尾空白后必须能解析为整数。
- 行号从 1 开始，包含空行和注释行。

公共接口固定为：

```python
from mini_pipeline import (
    PipelineError,
    SourceOpenError,
    RecordParseError,
    open_records,
    parse_records,
    filter_records,
    map_records,
    collect_summary,
)
```

## 文件职责

- `src/mini_pipeline/errors.py`：自定义异常。
- `src/mini_pipeline/io.py`：文件打开上下文管理器。
- `src/mini_pipeline/pipeline.py`：惰性数据流函数。
- `src/mini_pipeline/cli.py`：可选命令行入口。
- `tests/`：pytest 验收测试。

## 运行测试

在仓库根目录运行：

```bash
uv run pytest projects/01-runtime-model/mini_pipeline/tests
```

当前骨架故意不会通过测试。你的目标是补完 `TODO`，让测试逐步变绿。

## 必须满足的行为

### `open_records(path)`

`open_records(path)` 必须能作为上下文管理器使用：

```python
with open_records(path) as lines:
    first_line = next(lines)
```

要求：

- 进入 `with` 时打开文件。
- `lines` 是可迭代的行对象，通常就是文件对象本身。
- 退出 `with` 后文件必须关闭。
- 打开失败时抛出 `SourceOpenError`。
- `SourceOpenError.__cause__` 必须保留底层 `OSError`，也就是使用 `raise ... from exc`。

### `parse_records(lines)`

`parse_records(lines)` 必须返回生成器或其他惰性迭代器：

```python
records = parse_records(lines)
```

这里的 `records` 只是一个“将来会产出记录的对象”。调用 `parse_records` 时不应该立刻读取 `lines`。

每条记录用字典表示：

```python
{"name": "Ada", "score": 100}
```

解析失败时抛出 `RecordParseError`，并保留：

- `line_number`：出错行号。
- `raw_line`：原始行文本。
- `__cause__`：底层原因，例如 `ValueError`。

### `filter_records(records, predicate)`

返回惰性迭代器。只有当外部调用 `next()` 或开始 `for` 循环时，才消费 `records` 并调用 `predicate`。

```python
high_scores = filter_records(records, lambda record: record["score"] >= 90)
```

注意闭包 late binding：

```python
predicates = []
for threshold in [80, 90]:
    # threshold=threshold 会把当前对象绑定进默认参数。
    # 如果直接引用循环变量 threshold，多个闭包会共享同一个名字。
    predicates.append(lambda record, threshold=threshold: record["score"] >= threshold)
```

### `map_records(records, transform)`

返回惰性迭代器，对每条记录应用 `transform`：

```python
curved = map_records(records, lambda record: {**record, "score": record["score"] + 5})
```

这里 `{**record, ...}` 会创建新字典，避免意外修改原记录对象。

### `collect_summary(records)`

消费 `records`，返回汇总字典：

```python
{
    "count": 3,
    "total": 283,
    "average": 94.33333333333333,
    "names": ["Ada", "Guido", "Lin"],
}
```

空输入时：

```python
{
    "count": 0,
    "total": 0,
    "average": None,
    "names": [],
}
```

不要用可变默认参数保存 `names` 或其他状态。每次调用都应该创建新的列表或字典。

## 学习检查点

实现时请反复问自己：

1. 这个名字现在绑定到哪个对象？
2. 这个函数调用时有没有提前消费迭代器？
3. 这个容器里保存的是对象本身，还是对象引用？
4. 这个异常是否表达了当前层的语义？
5. 这个异常是否通过 `raise from` 保留了底层原因？
6. 这个上下文管理器是否在异常路径也会关闭资源？
7. 这个默认参数是否意外保存了跨调用共享状态？

