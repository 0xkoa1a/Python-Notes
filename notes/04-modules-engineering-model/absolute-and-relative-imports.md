# 绝对导入与相对导入

导入语句不只是“找到文件”。它表达当前模块依赖谁，以及这个依赖是从项目根命名空间出发，还是从当前包位置出发。

**绝对导入从顶层包名开始；相对导入从当前包位置开始；相对导入依赖模块的包上下文，因此不能脱离包运行。**

理解这点，很多 `attempted relative import with no known parent package` 都会消失。

## 1. 绝对导入

项目结构：

```text
myapp/
├─ __init__.py
├─ config.py
└─ users/
   ├─ __init__.py
   └─ service.py
```

在 `service.py` 中：

```python
from myapp.config import Settings
```

这是绝对导入。它从顶层包名 `myapp` 开始。

优点：

- 路径清晰。
- 移动到别的模块时更容易看懂依赖来源。
- 不依赖当前文件所在层级的点数。

缺点：

- 包名较长时略啰嗦。
- 项目根或安装方式不正确时会失败。

## 2. 相对导入

同样在 `myapp/users/service.py` 中：

```python
from ..config import Settings
from .models import User
```

含义：

- `.` 表示当前包 `myapp.users`。
- `..` 表示上一级包 `myapp`。

相对导入适合包内部紧密相关模块：

```python
from .models import User
from .repository import UserRepository
```

它强调：这些模块属于同一个包内局部结构。

## 3. 相对导入依赖 `__package__`

相对导入不是按文件系统路径简单计算。它依赖当前模块的包上下文：

```python
print(__name__)
print(__package__)
```

如果模块作为包的一部分被导入：

```bash
python -m myapp.users.service
```

`__package__` 通常是：

```text
myapp.users
```

相对导入知道 `.` 和 `..` 从哪里开始。

如果直接运行文件：

```bash
python myapp/users/service.py
```

它可能没有正确父包上下文。于是：

```python
from .models import User
```

会失败：

```text
ImportError: attempted relative import with no known parent package
```

这就是为什么包内模块不应该随便直接按文件路径运行。

## 4. 不要混淆文件路径和模块名

文件路径：

```text
myapp/users/service.py
```

模块名：

```text
myapp.users.service
```

导入系统关心模块名和搜索路径，不是你脑中的相对文件路径。

这两个运行方式不同：

```bash
python myapp/users/service.py
python -m myapp.users.service
```

前者把文件当脚本。后者把它当包里的模块。

## 5. 选择绝对还是相对

一般建议：

- 跨包导入：优先绝对导入。
- 同一小包内部：可以使用相对导入。
- 公共入口和应用层：绝对导入更清楚。
- 深层相对导入超过两层时，考虑结构是否过深。

清晰：

```python
from myapp.domain.users import User
```

也清晰：

```python
from .models import User
```

不太舒服：

```python
from ....domain.users import User
```

点数太多通常说明当前模块放得太深，或者依赖方向不自然。

## 6. 不推荐隐式相对导入

Python 3 中，包内写：

```python
import models
```

不会自动表示“导入当前包里的 models”。它会按 `sys.path` 找顶层 `models`。

包内导入同级模块，应写：

```python
from . import models
```

或者：

```python
from myapp.users import models
```

明确比猜测好。

## 7. 导入风格与依赖方向

导入语句会暴露依赖方向：

```python
# domain/users.py
from myapp.api.routes import router
```

这通常不对。领域层不应该依赖 API 层。

更自然：

```python
# api/routes.py
from myapp.domain.users import User
```

依赖方向应该从外层机制指向内层领域，而不是反过来。导入问题常常不是语法问题，而是架构边界问题。

## 8. 检查表

遇到导入风格问题，按下面问：

1. 当前模块的完整模块名是什么？
2. 当前模块的 `__package__` 是什么？
3. 这是跨包依赖，还是同包内部依赖？
4. 绝对导入是否更清楚？
5. 相对导入点数是否过多？
6. 是否直接运行了包内文件？
7. 导入方向是否违反工程层次？

最小心智模型：

1. 绝对导入从顶层包名开始。
2. 相对导入从当前包上下文开始。
3. 相对导入依赖 `__package__`。
4. 文件路径不等于模块名。
5. 导入语句表达依赖方向。
