# `TypedDict`

`TypedDict` 解决的问题是：很多 Python 数据来自 JSON、配置、API 响应，它们运行时是普通字典，但键和值有固定结构。

**`TypedDict` 给字典形状加静态类型：它不改变运行时对象，仍然是 `dict`；它只让类型检查器知道有哪些键、每个键是什么类型。**

这很适合描述边界数据，但不要把它误解成运行时验证工具。

## 1. 最小 TypedDict

```python
from typing import TypedDict

class UserPayload(TypedDict):
    id: str
    name: str
    age: int

def greet(user: UserPayload) -> str:
    return f"hello {user['name']}"
```

调用：

```python
payload: UserPayload = {"id": "u1", "name": "Alice", "age": 20}
```

运行时：

```python
print(type(payload))  # <class 'dict'>
```

`TypedDict` 不创建新字典类型。

## 2. 必填键与非必填键

默认所有键都是必填：

```python
class UserPayload(TypedDict):
    id: str
    name: str
```

缺少 `name` 时静态检查器会报错。

可以使用 `NotRequired`：

```python
from typing import NotRequired, TypedDict

class UserPayload(TypedDict):
    id: str
    name: str
    nickname: NotRequired[str]
```

`nickname` 可以不存在。

也可以使用 `Required` 配合 `total=False`：

```python
from typing import Required, TypedDict

class PatchUser(TypedDict, total=False):
    id: Required[str]
    name: str
    age: int
```

这里 `id` 必填，`name` 和 `age` 可选。

## 3. 访问可选键

可选键不能直接假设存在：

```python
def display(user: UserPayload) -> str:
    if "nickname" in user:
        # 这个分支中类型检查器知道 nickname 键存在
        return user["nickname"]
    return user["name"]
```

也可以用 `.get()`：

```python
nickname = user.get("nickname")
```

此时 `nickname` 类型通常是 `str | None`。

## 4. TypedDict vs dataclass

`TypedDict` 适合字典形状：

```python
payload["name"]
```

`dataclass` 适合对象模型：

```python
user.name
```

选择依据：

- 数据来自 JSON/API，准备原样传递：`TypedDict`。
- 数据进入内部领域模型，需要方法、不变量、属性：`dataclass` 或普通类。
- 需要运行时验证和解析：Pydantic 等验证库。

## 5. 嵌套结构

```python
class Address(TypedDict):
    city: str
    zip_code: str

class UserPayload(TypedDict):
    id: str
    address: Address
```

使用：

```python
def city(user: UserPayload) -> str:
    return user["address"]["city"]
```

嵌套 `TypedDict` 能描述复杂 JSON，但过深时可读性会下降。内部代码可能更适合转换成对象。

## 6. 运行时验证边界

`TypedDict` 不会验证外部数据：

```python
data = load_json()
user: UserPayload = data  # 静态检查器未必能证明 data 形状正确
```

你需要在边界验证：

```python
def parse_user(data: object) -> UserPayload:
    if not isinstance(data, dict):
        raise TypeError("user payload must be a dict")
    # 这里应继续检查键和值类型
    return data  # 实际项目中可用验证库处理
```

静态类型描述和运行时数据验证是两件事。

## 7. 检查表

使用 `TypedDict` 时，按下面问：

1. 数据运行时是否确实是 dict？
2. 键集合是否相对稳定？
3. 哪些键必填，哪些键可选？
4. 可选键访问前是否检查存在？
5. 是否需要运行时验证？
6. 数据是否应该转换成 dataclass 或领域对象？

最小心智模型：

1. `TypedDict` 描述字典形状。
2. 运行时对象仍是 `dict`。
3. 它服务静态检查，不做运行时验证。
4. 可选键要显式处理。
5. 外部数据进入系统时仍需要验证。
