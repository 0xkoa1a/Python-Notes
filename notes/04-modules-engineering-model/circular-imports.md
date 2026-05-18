# 循环导入

循环导入不是 Python 心情不好，而是模块图里出现了环。

**循环导入发生在模块 A 导入模块 B，同时模块 B 又直接或间接导入模块 A；如果某一方在另一方初始化完成前访问未创建的名字，就会看到部分初始化模块。**

解决循环导入的关键不是把 import 语句挪来挪去，而是重新审视依赖方向。

## 1. 最小循环导入

```python
# a.py
import b

VALUE_A = "A"
```

```python
# b.py
import a

print(a.VALUE_A)
```

执行：

```python
import a
```

流程：

1. 创建模块对象 `a`，放入 `sys.modules`。
2. 开始执行 `a.py`。
3. `a.py` 导入 `b`。
4. 创建模块对象 `b`，放入 `sys.modules`。
5. 执行 `b.py`。
6. `b.py` 导入 `a`，直接从 `sys.modules` 拿到部分初始化的 `a`。
7. `a.VALUE_A` 还没执行到赋值，于是失败。

这里的核心不是“不能互相 import”，而是访问发生得太早。

## 2. 错误信息里的 partially initialized

常见错误：

```text
ImportError: cannot import name 'X' from partially initialized module 'a'
```

或者：

```text
AttributeError: partially initialized module 'a' has no attribute 'X'
```

“partially initialized” 表示模块对象已经创建并放入缓存，但模块顶层代码还没执行完。

这个词直接指向 `sys.modules` 的导入缓存机制。

## 3. 循环导入通常暴露设计问题

示例：

```text
myapp/
├─ models.py
└─ services.py
```

```python
# models.py
from myapp.services import validate_user

class User:
    ...
```

```python
# services.py
from myapp.models import User
```

这说明 `models` 和 `services` 互相知道太多。

更清楚的方向通常是：

- `models` 定义数据结构，不依赖服务。
- `services` 使用模型。
- 校验逻辑如果属于模型不变量，放进模型。
- 如果是复杂业务规则，放进服务，但不要让模型导入服务。

## 4. 修复方式一：提取共同依赖

如果 A 和 B 都需要某个东西，把它提到第三个模块：

```text
before:
A -> B
B -> A

after:
A -> common
B -> common
```

例子：

```text
myapp/
├─ types.py
├─ parser.py
└─ formatter.py
```

`parser.py` 和 `formatter.py` 都依赖 `types.py`，但不互相依赖。

这通常是最干净的修法。

## 5. 修复方式二：反转依赖

如果低层模块导入高层模块，通常应该反过来。

坏方向：

```text
domain -> api
```

好方向：

```text
api -> domain
```

低层领域模型不应该知道 HTTP 路由、CLI、数据库适配器。高层入口组合低层能力。

循环导入经常是层次方向混乱的信号。

## 6. 修复方式三：延迟导入

有时可以把导入放进函数内部：

```python
def create_user(data):
    from myapp.validators import validate_user

    validate_user(data)
```

这样导入发生在函数调用时，不在模块初始化时。

这可以解决某些实际问题，但它是局部缓解，不是结构性答案。使用前先问：

```text
为什么这个模块必须在顶层互相依赖？
```

延迟导入适合：

- 避免昂贵导入。
- 可选依赖。
- 某些插件加载。
- 临时打破初始化时机问题。

不适合掩盖混乱依赖图。

## 7. 修复方式四：只为类型检查导入

类型标注可能制造运行时循环：

```python
# user.py
from myapp.team import Team

class User:
    team: Team
```

可以用：

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from myapp.team import Team

class User:
    team: "Team"
```

解释：

- `TYPE_CHECKING` 在运行时是 `False`，类型检查器会认为是 `True`。
- 这让类型检查器看到导入，而运行时不执行这个导入。
- `from __future__ import annotations` 让标注延迟求值，减少运行时依赖。

这是类型层依赖和运行时依赖分离的常见手法。

## 8. 修复方式五：依赖注入

不要让模块自己导入具体实现，而是由外部传入依赖：

```python
class UserService:
    def __init__(self, repository):
        # repository 是外部注入的依赖对象
        self.repository = repository
```

入口层组合：

```python
repository = SqlUserRepository(...)
service = UserService(repository)
```

这样 `UserService` 不需要导入具体数据库实现，循环依赖和测试困难都会减少。

## 9. 检查表

遇到循环导入，按下面问：

1. 哪两个或哪些模块形成了环？
2. 错误是否来自部分初始化模块？
3. 哪个名字被访问得太早？
4. 是否有共同依赖可以提取？
5. 是否存在低层模块导入高层模块？
6. 是否只是类型标注需要导入？
7. 延迟导入是在修结构，还是掩盖结构问题？
8. 是否可以用依赖注入反转依赖？

最小心智模型：

1. 循环导入是模块依赖图有环。
2. 模块会在执行完成前进入 `sys.modules`。
3. 部分初始化模块来自过早访问。
4. 最好通过重构依赖方向解决循环导入。
5. 延迟导入是工具，不是架构原则。
