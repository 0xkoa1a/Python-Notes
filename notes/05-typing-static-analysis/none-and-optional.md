# `None` 与可选类型

`None` 不是“没有类型”，它是一个具体的单例对象。类型标注里只要一个值可能是 `None`，就必须把这件事写出来。

**`T | None` 表示这个名字可能绑定到 `T` 对象，也可能绑定到 `None`；使用前必须通过判断把类型收窄到非 `None`。**

这能把很多运行时 `AttributeError: 'NoneType' object has no attribute ...` 提前暴露出来。

## 1. 可选类型

```python
def find_user(name: str) -> str | None:
    if name == "Alice":
        return "user-id-1"
    return None
```

返回类型 `str | None` 表示调用者必须处理找不到的情况：

```python
user_id = find_user("Bob")

if user_id is not None:
    print(user_id.upper())
```

不要写成：

```python
print(user_id.upper())  # user_id 可能是 None
```

静态检查器会提醒你。

## 2. `Optional[T]`

老写法：

```python
from typing import Optional

def find_user(name: str) -> Optional[str]:
    ...
```

现代写法：

```python
def find_user(name: str) -> str | None:
    ...
```

两者含义相同。现在更推荐 `T | None`，更直观。

## 3. 默认值为 `None` 不等于参数类型自动可选

```python
def connect(timeout: float | None = None) -> None:
    ...
```

如果默认值是 `None`，类型也应该显式包含 `None`。

这表达两件事：

- 调用者可以不传 timeout。
- 函数内部要处理 `timeout is None` 的分支。

## 4. `None` 是哨兵

`None` 常用来表示“没有提供值”：

```python
def normalize(items: list[int] | None = None) -> list[int]:
    if items is None:
        items = []
    return sorted(items)
```

判断时用 `is None`，不是 `== None`，也不是 `if not items`。

```python
if items is None:
    ...
```

因为空列表 `[]` 也是假值，但它和“没传”不是同一回事。

## 5. 可选类型和空容器不同

```python
def first(items: list[str]) -> str | None:
    if not items:
        return None
    return items[0]
```

这里：

- `items: list[str]` 表示调用者必须传列表。
- 返回 `str | None` 表示列表可能为空，所以没有第一个元素。

不要把“参数可以省略”和“容器可以为空”混在一起。

## 6. 用异常还是返回 `None`

两种 API 风格：

```python
def find_user(name: str) -> User | None:
    ...
```

和：

```python
def get_user(name: str) -> User:
    ...
    raise UserNotFound(name)
```

选择依据：

- 找不到是常见分支：返回 `None` 合理。
- 找不到表示逻辑错误或异常情况：抛异常更清楚。
- 调用者如果必须立刻处理失败，异常可能更合适。

命名也要诚实：

- `find_*` 常暗示可能找不到。
- `get_*` 常暗示应该存在，不存在可能抛异常。

## 7. 检查表

处理 `None` 时，按下面问：

1. 这个名字是否真的可能是 `None`？
2. 类型标注是否写成 `T | None`？
3. 使用前是否 `is not None` 收窄？
4. 空容器和 `None` 是否被混淆？
5. 返回 `None` 是否比抛异常更适合？
6. 函数名是否表达了可能失败？

最小心智模型：

1. `None` 是具体对象。
2. `T | None` 是显式可选类型。
3. 可选值使用前需要收窄。
4. `is None` 判断是否缺失。
5. 空值和缺失值不是同一个概念。
