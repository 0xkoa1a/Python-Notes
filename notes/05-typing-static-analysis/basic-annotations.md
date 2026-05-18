# 基础类型标注

类型标注解决的问题不是“让 Python 变成静态语言”，而是让函数、变量和数据结构的接口更清楚。

**类型标注是写在动态对象模型旁边的说明和约束：运行时对象仍然按 Python 规则运行，静态检查器则根据标注提前发现不一致。**

## 1. 标注函数接口

```python
def add(x: int, y: int) -> int:
    return x + y
```

这表示调用者应该传入两个 `int`，函数应该返回 `int`。默认运行时不会强制检查：

```python
print(add("a", "b"))  # 运行时仍可能输出 "ab"
```

类型检查器会指出这和标注不一致。

## 2. 标注变量

```python
count: int = 0
name: str = "Alice"
```

变量标注说明这个名字预期绑定什么类型的对象。它不冻结名字，也不改变赋值语义。

```python
count = "zero"  # 运行时可以，但静态检查器会报错
```

## 3. 容器类型

现代 Python 直接使用内置泛型：

```python
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 90}
point: tuple[int, int] = (1, 2)
tags: set[str] = {"python", "typing"}
```

读法：

- `list[str]`：元素是 `str` 的列表。
- `dict[str, int]`：键是 `str`，值是 `int`。
- `tuple[int, int]`：长度固定为 2，两个元素都是 `int`。

任意长度同类型元组：

```python
coords: tuple[int, ...] = (1, 2, 3)
```

`...` 表示后续可以有任意多个 `int`。

## 4. 返回 `None`

没有有意义返回值的函数标注为 `None`：

```python
def log_message(message: str) -> None:
    print(message)
```

`None` 是返回值类型，不是“没有返回类型”。这个函数仍然返回 `None`。

## 5. 类型别名

复杂类型可以命名：

```python
UserId = str
ScoreTable = dict[str, int]

def get_score(scores: ScoreTable, user_id: UserId) -> int:
    return scores[user_id]
```

类型别名提高可读性，但不要滥用。`UserId = str` 对静态检查器来说通常仍是 `str`，并不会自动变成强类型 ID。

需要更强区分时，可以考虑 `NewType`：

```python
from typing import NewType

UserId = NewType("UserId", str)

def load_user(user_id: UserId) -> None:
    ...

load_user(UserId("u-1"))
```

`NewType` 主要服务静态检查，运行时开销很低，本质上仍是原始值。

## 6. 类型标注存在哪里

函数标注保存在 `__annotations__`：

```python
def add(x: int, y: int) -> int:
    return x + y

print(add.__annotations__)
# {'x': <class 'int'>, 'y': <class 'int'>, 'return': <class 'int'>}
```

`__annotations__` 是运行时字典，很多框架会读取它，例如 FastAPI、Pydantic、CLI 框架等。

但读取标注不等于 Python 自动检查标注。检查要么来自外部静态工具，要么来自框架主动做运行时验证。

## 7. `Any`

```python
from typing import Any

def dump(value: Any) -> str:
    return repr(value)
```

`Any` 表示“静态检查器不要追究这里的具体类型”。它很方便，也很危险。

使用 `Any` 的合理场景：

- 外部动态数据边界。
- 逐步迁移旧代码。
- 真正接受任意对象的调试函数。

但 `Any` 会传播：

```python
def get_data() -> Any:
    ...

x = get_data()
x.not_existing().whatever()  # 类型检查器可能不报
```

所以 `Any` 应该尽量限制在边界，并尽快转换成明确类型。

## 8. 检查表

写基础标注时，按下面问：

1. 函数输入输出是否清楚？
2. 容器元素类型是否明确？
3. `None` 返回是否显式标出？
4. 类型别名是否真的提高理解？
5. 是否用了过多 `Any`？
6. 运行时验证和静态检查是否被混淆？

最小心智模型：

1. 类型标注描述接口。
2. 标注默认不改变运行时行为。
3. 静态检查器读取标注发现不一致。
4. 框架可以选择在运行时读取标注。
5. `Any` 是逃生门，不是默认答案。
