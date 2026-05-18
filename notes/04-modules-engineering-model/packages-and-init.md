# 包与 `__init__.py`

包解决的问题是：当模块变多以后，如何把一组模块组织成一个有名字空间边界的整体。

**包本身也是模块对象；目录里的 `__init__.py` 定义包对象的初始化逻辑和门面 API；子模块通过包名形成层级命名空间。**

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

## 3. `__init__.py` 不是访问控制边界

一个非常经典的误区是：以为没有写进 `__init__.py` 的子模块，外界就不能导入。

**这是错的。`__init__.py` 不是防火墙，也不是严格白名单。只要调用者知道完整模块路径，并且模块能被导入系统找到，就可以精确导入包里的子模块。**

例如：

```text
my_package/
├─ __init__.py        # 空文件
├─ public_module.py
└─ hidden_module.py
```

即使 `__init__.py` 是空的，外部仍然可以写：

```python
import my_package.hidden_module

my_package.hidden_module.secret_func()
```

或者：

```python
from my_package.hidden_module import secret_func
```

这完全合法。Python 没有 Java 那种严格的 `private` / `public` 模块访问控制。更接近 Python 风格的说法是：大家都是成年人，约定比强制更多。

如果你想表达“这是内部模块，不属于稳定公共 API”，标准做法是使用单下划线命名：

```text
my_package/
├─ __init__.py
├─ public_module.py
└─ _hidden_module.py
```

调用者仍然可以强行导入：

```python
import my_package._hidden_module
```

但单下划线是在告诉读者、IDE、文档工具和类型工具：这是内部实现，外部代码不要依赖它。它防君子，不防强行访问。

## 4. 包对象的属性

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

## 5. 在 `__init__.py` 中暴露公共 API

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

这能让公共 API 更短。它的真正意义是门面模式：把内部较深的实现路径包装成更友好、更稳定的顶层 API。

例如内部类可能实际在：

```text
my_package/core/engine/processor.py
```

如果不包装，用户要写：

```python
from my_package.core.engine.processor import DataProcessor
```

在包顶层包装后：

```python
# my_package/__init__.py
from .core.engine.processor import DataProcessor
```

用户就可以写：

```python
from my_package import DataProcessor
```

这不是安全隐藏内部模块，而是给用户提供舒服的公共入口。但要谨慎：`__init__.py` 导入越多，包导入越重，也越容易引发循环导入。

经验：

- 小包可以在 `__init__.py` 暴露核心对象。
- 大包应避免 `__init__.py` 过度导入。
- 内部模块之间尽量直接导入需要的内部模块，不依赖包顶层重新导出。
- 不要把“没有从 `__init__.py` 暴露”误解成“外部不能导入”。

## 6. `__all__`

`__all__` 控制星号导入，不控制精确导入：

```python
# myapp/__init__.py

from . import public_module
from . import hidden_module

__all__ = ["public_module"]
```

```python
from myapp import *

print(public_module) # 成功
print(hidden_module) # NameError，星号导入没有导出这个名字
```

`from myapp import *` 只会导入 `__all__` 中列出的名字。

但这不阻止调用者精确导入：

```python
import myapp.hidden_module
```

日常代码不推荐 `import *`。但 `__all__` 仍然可以作为公共 API 文档：告诉读者这个模块刻意暴露哪些名字。

如果没有定义 `__all__`，星号导入默认导入 `__init__.py` 命名空间中不以下划线开头的名字。它仍然不会自动递归导入包里的所有子模块。

## 7. 子包

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

## 8. 命名空间包

现代 Python 支持没有 `__init__.py` 的命名空间包。它允许同一个包名分布在多个目录或发行包中。

这对插件系统和大型分发包有用，但对普通学习项目或应用项目，建议先使用显式 `__init__.py`。

原因很简单：显式边界更容易理解，也减少工具差异带来的困惑。

## 9. 包设计原则

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

## 10. 检查表

设计包时，按下面问：

1. 这组模块是否形成清晰边界？
2. `__init__.py` 是否足够轻？
3. 是否误把 `__init__.py` 当成访问控制白名单？
4. 包顶层是否只暴露稳定公共 API？
5. `__all__` 是否只被理解为星号导入控制？
6. 内部模块是否用单下划线表达“非公共 API”？
7. 子模块之间是否过度依赖包顶层重新导出？
8. 包名是否表达职责，而不是“utils”式杂物箱？
9. 是否真的需要命名空间包？

最小心智模型：

1. 包是模块对象。
2. 包用目录组织子模块。
3. `__init__.py` 初始化包对象。
4. `__path__` 决定子模块搜索位置。
5. `__init__.py` 暴露的是门面 API，不是访问控制。
6. `__all__` 主要影响 `from package import *`。
7. 包提供命名空间边界和工程边界。
