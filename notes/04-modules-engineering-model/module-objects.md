# 模块对象

模块是 Python 工程结构的基本单位。一个 `.py` 文件被导入后，不只是“代码被粘贴进来”，而是会产生一个模块对象。

**模块对象是运行时对象；模块顶层名字保存在模块对象的命名空间中；`import` 的结果是把某个名字绑定到模块对象或模块对象中的成员。**

理解模块对象以后，`import`、脚本入口、包、循环导入、测试结构都会简单很多。

## 1. 什么是模块

最常见的模块来源是一个 `.py` 文件：

```text
math_utils.py
```

文件内容：

```python
PI = 3.14159

def area(radius):
    return PI * radius ** 2
```

导入：

```python
import math_utils

print(math_utils.PI)
print(math_utils.area(2))
```

这里 `math_utils` 是一个名字，绑定到导入系统创建的模块对象。

模块对象里有一个命名空间，保存 `PI`、`area` 等顶层名字。

## 2. 模块命名空间

模块顶层变量、函数、类都进入模块命名空间：

```python
# users.py

DEFAULT_ROLE = "guest"

class User:
    pass

def create_user():
    return User()
```

导入后：

```python
import users

print(users.DEFAULT_ROLE)
print(users.User)
print(users.create_user)
```

可以把模块命名空间理解为：

```text
module users
  ├─ DEFAULT_ROLE -> "guest"
  ├─ User         -> class object
  └─ create_user  -> function object
```

模块不是目录文本，它是一个带属性的对象。

## 3. 模块对象的内置属性

模块有很多有用属性：

```python
import users

print(users.__name__)    # 模块名，例如 "users"
print(users.__file__)    # 模块文件路径
print(users.__package__) # 所属包名
print(users.__dict__)    # 模块命名空间字典
```

这些属性帮助导入系统、调试工具、测试框架理解模块身份。

示例：

```python
def debug_module(module):
    # module 是模块对象，不是模块名字符串
    print("name:", module.__name__)
    print("file:", getattr(module, "__file__", None))
```

有些模块没有 `__file__`，例如部分内置模块。用 `getattr` 更稳。

## 4. `import module` 与 `from module import name`

```python
import users
```

这会把名字 `users` 绑定到模块对象。

```python
from users import User
```

这会先加载模块对象 `users`，然后把当前命名空间中的名字 `User` 绑定到 `users.User` 当前指向的对象。

区别很重要：

```python
import users
from users import DEFAULT_ROLE

users.DEFAULT_ROLE = "member"

print(users.DEFAULT_ROLE) # member
print(DEFAULT_ROLE)       # guest，当前名字仍绑定到旧对象
```

`from users import DEFAULT_ROLE` 不是建立一个“实时链接”。它只是一次名字绑定。

## 5. 模块顶层代码会执行

导入模块时，模块顶层代码会执行一次：

```python
# config.py

print("loading config")

VALUE = 42
```

导入：

```python
import config  # 会打印 loading config
```

所以模块顶层应该主要放定义和轻量初始化，不要放昂贵副作用：

- 不要在导入时启动服务。
- 不要在导入时读取巨大文件。
- 不要在导入时连接数据库。
- 不要在导入时执行真实业务流程。

这些动作应该放进函数或入口点中。

## 6. 模块是单例式缓存对象

同一个模块通常只加载一次，后续 import 复用缓存。缓存机制在 `sys.modules` 一节展开。

现在先记住：

```python
import config
import config
```

顶层代码通常不会执行两次。两个 `import config` 绑定到的是同一个模块对象。

这解释了为什么模块级可变状态会被共享：

```python
# state.py
items = []
```

任何地方导入 `state`，看到的都是同一个模块对象中的 `items`。

## 7. 模块适合放什么

模块是工程切分单位，适合放一组内聚的定义：

- 一组相关函数。
- 一个领域模型。
- 一组配置解析逻辑。
- 一个 CLI 入口。
- 一组测试辅助。
- 一个协议或接口定义。

模块不应该变成“杂物箱”。如果模块名叫 `utils.py`，里面什么都有，通常说明边界还没想清楚。

更好的名字：

```text
paths.py
config.py
parsing.py
repositories.py
serializers.py
```

模块名应该表达职责。

## 8. 检查表

遇到模块相关问题，按下面问：

1. 当前名字绑定到模块对象，还是模块里的某个对象？
2. 模块顶层代码是否有副作用？
3. 模块状态是否会被多个导入方共享？
4. 使用 `import module` 更清楚，还是 `from module import name` 更清楚？
5. 模块名是否表达了明确职责？
6. 模块边界是否减少了依赖混乱？

最小心智模型：

1. 模块是运行时对象。
2. `.py` 文件导入后产生模块对象。
3. 模块顶层名字保存在模块命名空间。
4. `import` 是名字绑定，不是文本粘贴。
5. 模块顶层代码在导入时执行。
6. 模块级状态会被导入方共享。
