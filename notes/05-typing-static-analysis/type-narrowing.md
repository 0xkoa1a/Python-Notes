# 类型收窄

类型收窄解决的问题是：一个名字在某个位置可能有多种类型，但经过判断后，我们知道它在某个分支里更具体。

**类型检查器不会读心；它根据 `isinstance`、`is None`、`return`、`raise`、`assert` 等控制流，把联合类型缩小成更具体的类型。**

这让 `T | None`、`object`、联合类型都能安全使用。

## 1. `None` 收窄

```python
def upper(text: str | None) -> str:
    if text is None:
        return ""

    # 这里 text 已经被收窄为 str
    return text.upper()
```

如果没有判断，`text.upper()` 不安全，因为 `None` 没有 `upper`。

## 2. `isinstance` 收窄

```python
def length(value: str | list[int]) -> int:
    if isinstance(value, str):
        # 这里 value 是 str
        return len(value)

    # 这里 value 是 list[int]
    return len(value)
```

类型检查器根据分支排除不可能类型。

## 3. `return` 和 `raise` 帮助收窄

```python
def require_user(user: User | None) -> User:
    if user is None:
        raise ValueError("user required")

    # 如果执行到这里，user 不可能是 None
    return user
```

`raise` 终止当前控制流，所以后续分支可以认为 `user` 是 `User`。

## 4. `assert` 收窄

```python
def process(value: object) -> str:
    assert isinstance(value, str)
    return value.upper()
```

`assert` 告诉类型检查器：后面可以把 `value` 当成 `str`。

但不要用 `assert` 处理用户输入。`assert` 可以被优化模式移除。外部数据应显式校验并抛异常。

## 5. 字面量和判别联合

```python
from typing import Literal, TypedDict

class Ok(TypedDict):
    kind: Literal["ok"]
    value: int

class Err(TypedDict):
    kind: Literal["err"]
    message: str

Result = Ok | Err

def handle(result: Result) -> str:
    if result["kind"] == "ok":
        # 这里 result 被收窄为 Ok
        return str(result["value"])
    return result["message"]
```

`kind` 字段是判别标记。类型检查器可以根据它区分联合成员。

## 6. 自定义 TypeGuard

```python
from typing import TypeGuard

def is_str_list(value: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in value)

items: list[object] = ["a", "b"]

if is_str_list(items):
    # 这里 items 被收窄为 list[str]
    print(items[0].upper())
```

`TypeGuard` 告诉检查器：如果函数返回 `True`，参数类型可以看作更具体的类型。

要谨慎使用。错误的 `TypeGuard` 会欺骗类型检查器。

## 7. `cast`

```python
from typing import cast

value: object = load_value()
user = cast(User, value)
```

`cast` 只影响静态检查器，不做运行时检查。

```python
user = cast(User, value)  # value 运行时不会自动变成 User
```

只有当你比检查器知道更多，而且已经通过别的方式保证正确时，才使用 `cast`。

## 8. 检查表

处理联合类型时，按下面问：

1. 使用前是否收窄到具体类型？
2. `None` 是否用 `is None` 判断？
3. `isinstance` 是否足够表达运行时事实？
4. `assert` 是否只用于内部不变量？
5. 是否需要判别字段？
6. `TypeGuard` 是否真实可靠？
7. `cast` 是否只是掩盖类型设计问题？

最小心智模型：

1. 联合类型需要控制流收窄。
2. 类型检查器根据判断理解分支。
3. `return` 和 `raise` 会结束分支。
4. `cast` 不做运行时转换。
5. 收窄是让动态对象进入静态约束的桥。
