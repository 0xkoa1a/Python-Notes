# 包与 `__init__.py`

包解决的问题是：当模块变多以后，如何把一组模块组织成一个有名字空间边界的整体。

**包本身也是模块对象；目录里的 `__init__.py` 定义包对象的初始化逻辑和公开入口；子模块通过包名形成层级命名空间。**

这不是文件夹技巧，而是大型 Python 项目建立边界的方式。

## 1. 什么是包

一个普通包通常长这样：

```text
myapp/
├─ __init__.py
├─ config.py
└─ users.py
```

导入：

```python
import myapp
import myapp.config
```

`myapp` 是包对象，也是模块对象。`myapp.config` 是包里的子模块对象。

包的意义是给模块增加层级命名空间：

```text
config.py          # 顶层模块名 config，容易和别的 config 冲突
myapp.config       # 包内模块名，更明确
```

## 2. `__init__.py` 的作用

`__init__.py` 是包初始化文件。导入包时会执行它：

```python
# myapp/__init__.py
print("loading myapp")
```

```python
import myapp # 执行 myapp/__init__.py
```

`__init__.py` 可以为空。空文件也有意义：它明确告诉读者和工具，这是一个包边界。

常见用途：

- 声明包版本。
- 暴露少量公共 API。
- 做轻量初始化。
- 给类型检查器和打包工具提供清晰边界。

不适合做：

- 连接数据库。
- 加载巨大配置。
- 启动服务。
- 导入整个世界。

因为任何 `import myapp` 都会执行它。

## 3. 包对象的属性

```python
import myapp

print(myapp.__name__)    # "myapp"
print(myapp.__package__) # "myapp"
print(myapp.__path__)    # 子模块搜索路径
```

`__path__` 是包特有的。导入子模块时，Python 会在包的 `__path__` 中寻找：

```python
import myapp.users
```

搜索的是：

```text
myapp.__path__/users.py
myapp.__path__/users/__init__.py
```

## 4. 在 `__init__.py` 中暴露公共 API

内部结构：

```text
myapp/
├─ __init__.py
└─ users.py
```

```python
# myapp/users.py

class User:
    pass
```

可以在 `__init__.py` 中导出：

```python
# myapp/__init__.py

from .users import User
```

调用方：

```python
from myapp import User
```

这能让公共 API 更短。但要谨慎：`__init__.py` 导入越多，包导入越重，也越容易引发循环导入。

经验：

- 小包可以在 `__init__.py` 暴露核心对象。
- 大包应避免 `__init__.py` 过度导入。
- 内部模块之间尽量直接导入需要的内部模块，不依赖包顶层重新导出。

## 5. `__all__`

`__all__` 控制星号导入：

```python
# myapp/__init__.py

from .users import User

__all__ = ["User"]
```

```python
from myapp import *
```

只会导入 `__all__` 中列出的名字。

日常代码不推荐 `import *`。但 `__all__` 仍然可以作为公共 API 文档：告诉读者这个模块刻意暴露哪些名字。

## 6. 子包

包可以嵌套：

```text
myapp/
├─ __init__.py
├─ api/
│  ├─ __init__.py
│  └─ routes.py
└─ domain/
   ├─ __init__.py
   └─ users.py
```

导入：

```python
import myapp.api.routes
from myapp.domain.users import User
```

每个包含 `__init__.py` 的目录都是一个包。每层包都有自己的模块对象和命名空间。

## 7. 命名空间包

现代 Python 支持没有 `__init__.py` 的命名空间包。它允许同一个包名分布在多个目录或发行包中。

这对插件系统和大型分发包有用，但对普通学习项目或应用项目，建议先使用显式 `__init__.py`。

原因很简单：显式边界更容易理解，也减少工具差异带来的困惑。

## 8. 包设计原则

好的包结构应该让依赖方向清楚：

```text
myapp/
├─ domain/      # 领域模型，尽量少依赖外部
├─ services/    # 业务逻辑
├─ adapters/    # 数据库、HTTP、文件系统等外部适配
└─ cli.py       # 命令行入口
```

不要只按“文件类型”分包：

```text
models/
utils/
helpers/
common/
```

这些名字容易变成杂物箱。更好的包名应该表达领域或职责。

## 9. 检查表

设计包时，按下面问：

1. 这组模块是否形成清晰边界？
2. `__init__.py` 是否足够轻？
3. 包顶层是否只暴露稳定公共 API？
4. 子模块之间是否过度依赖包顶层重新导出？
5. 包名是否表达职责，而不是“utils”式杂物箱？
6. 是否真的需要命名空间包？

最小心智模型：

1. 包是模块对象。
2. 包用目录组织子模块。
3. `__init__.py` 初始化包对象。
4. `__path__` 决定子模块搜索位置。
5. 包提供命名空间边界和工程边界。
