# Protocol RecordSet

这是第二章“协议与数据模型”的阶段项目。它不是一个完整的数据分析库，而是一个刻意缩小的容器练习：你要通过实现少数几个对象，让 Python 的语法自然接入你的类型。

**这个项目的重点不是记住魔术方法名字，而是理解：语法调用协议，协议调用对象。**

## 你要实现什么

核心对象是 `RecordSet`：一个不可变风格的数据记录集合。每条记录是一个 `dict[str, object]`：

```python
records = RecordSet(
    [
        {"name": "Ada", "score": 100},
        {"name": "Lin", "score": 88},
        {"name": "Guido", "score": 95},
    ]
)
```

公共接口固定为：

```python
from protocol_recordset import Field, RecordSet, where
```

测试运行命令：

```bash
uv run pytest projects/02-protocol-data-model/protocol_recordset/tests
```

当前骨架故意不会通过测试。你的任务是补完 `TODO`，让测试逐步变绿。

## 协议目标

### 表示协议

`repr(recordset)` 应包含：

- 类名 `RecordSet`
- 记录数量
- 字段名，例如 `name`、`score`

这不是为了好看，而是为了调试。`repr(obj)` 会调用 `obj.__repr__()`。

### 布尔与长度协议

```python
len(recordset)
bool(recordset)
```

要求：

- `len(recordset)` 返回记录数量。
- 空 `RecordSet` 在布尔上下文中为假。
- 可以只实现 `__len__`，让布尔判断通过长度协议自然发生。

### 容器协议

`RecordSet` 要支持三类 `[]` 访问：

```python
recordset[0]        # 返回单条记录的副本
recordset[-1]       # 支持负数索引
recordset[1:3]      # 返回新的 RecordSet
recordset["score"]  # 返回某一列的值列表
```

`obj[key]` 会调用 `obj.__getitem__(key)`。这里的关键练习是：同一个协议入口可以根据 key 的类型表达不同语义。

要求：

- 整数索引返回记录副本。
- 切片返回新的 `RecordSet`。
- 字符串字段访问返回列表。
- 缺失字段抛出 `KeyError`。
- 不支持的 key 类型抛出 `TypeError`。

### 迭代协议

```python
for record in recordset:
    ...
```

要求：

- `__iter__` 每次返回新的迭代器。
- 每次迭代产出的记录都应该是副本，避免外部修改污染内部状态。

### 调用协议

```python
high_scores = recordset(lambda record: record["score"] >= 90)
```

`obj(...)` 会调用 `obj.__call__(...)`。在这个项目里，`recordset(predicate)` 应等价于 `recordset.filter(predicate)`。

### 比较与哈希协议

要求：

- 两个 `RecordSet` 按记录内容相等。
- 顺序也属于内容的一部分。
- 和其他类型比较时，`RecordSet.__eq__` 应返回 `NotImplemented`。
- `RecordSet` 应显式不可哈希，因为它表达的是包含字典记录的集合语义。

### 查询字段对象

`where("score") >= 90` 应返回一个可调用谓词对象：

```python
predicate = where("score") >= 90
predicate({"name": "Ada", "score": 100})  # True
```

`Field` 不是完整查询语言。它只是一个轻量对象，用来练习：

- 对象保存字段名。
- 比较运算符可以返回对象，而不一定立即返回布尔值。
- 返回的谓词对象实现 `__call__`，因此可以像函数一样调用。

## 学习检查点

实现时请反复问自己：

1. 这个语法实际调用了哪个协议方法？
2. `__getitem__` 收到的 key 是什么对象？
3. 迭代时产出的是内部字典本身，还是副本？
4. 构造时是否复制了输入记录，避免外部 aliasing？
5. `__eq__` 遇到不认识的类型时，是返回 `False`，还是返回 `NotImplemented`？
6. `where("score") >= 90` 这一步返回的是布尔值，还是一个将来可调用的谓词对象？
7. 为什么定义值相等后，需要认真考虑 `__hash__`？

