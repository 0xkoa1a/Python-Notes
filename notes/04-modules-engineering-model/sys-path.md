# `sys.path`

`sys.path` 回答的问题是：当你写 `import x` 时，Python 到哪些地方找 `x`。

**`sys.path` 是模块搜索路径列表；导入系统会按顺序在这些路径中寻找模块和包；很多“明明文件在这里却 import 不到”的问题，本质上是搜索路径问题。**

这不是工程小细节。它直接决定项目应该如何运行、测试、打包。

## 1. `sys.path` 是什么

```python
import sys

for path in sys.path:
    print(path)
```

`sys.path` 是字符串列表。每个元素通常是一个目录路径，导入系统会在这些目录下查找模块。

更精确地说，`sys.path` 主要用于查找**顶层模块名或顶层包名**。

当你写：

```python
import config
```

Python 会把 `config` 当作顶层名字，沿 `sys.path` 从前到后查找。对每一个搜索目录 `path`，它会尝试找类似这些目标：

```text
path/config.py
path/config/__init__.py
```

真实导入系统还会处理内置模块、扩展模块、缓存文件、导入钩子等情况。日常理解先抓住这条主线：**对顶层名字，Python 按 `sys.path` 顺序找，第一个匹配到的模块或包胜出。**

这解释了两个事实：

- 搜索路径顺序会影响导入结果。
- 同名模块可能被更靠前的路径遮蔽。

## 2. 顶层模块和包内子模块的搜索不同

写：

```python
import myapp.users
```

Python 不是直接在 `sys.path` 里找：

```text
path/myapp/users.py
```

然后一步到位。更准确的流程是：

1. 先把 `myapp` 当作顶层名字，在 `sys.path` 中查找。
2. 找到 `myapp` 包后，执行 `myapp/__init__.py`，创建包对象。
3. 再在 `myapp.__path__` 中查找子模块 `users`。

也就是：

```text
sys.path
  └─ 找顶层包 myapp
       └─ myapp.__path__
            └─ 找子模块 users
```

所以：

```python
import package
print(package.__path__) # 包搜索子模块的位置
```

`sys.path` 决定顶层包从哪里来；包对象的 `__path__` 决定它的子模块从哪里来。

`from myapp import users` 也类似：先导入或取得包对象 `myapp`，再尝试在包中找到或加载子模块 `users`。

## 3. `sys.path` 到底包含哪些路径

`sys.path` 不是凭空出现的。Python 启动时会根据启动方式、环境变量、安装环境和虚拟环境初始化它。

一个典型的 `sys.path` 大致由这些部分组成：

1. **`sys.path[0]`：启动入口相关路径**

   这是最容易导致导入问题的位置。它可能是当前工作目录，也可能是脚本所在目录，具体取决于你怎么启动 Python。

2. **`PYTHONPATH` 环境变量中的路径**

   如果设置了 `PYTHONPATH`，其中的目录会被加入 `sys.path`。这会影响所有在该环境下启动的 Python 程序，因此不适合作为项目内部的默认方案。

3. **标准库路径**

   例如 Python 安装目录下的 `Lib`。`json`、`pathlib`、`asyncio` 这类标准库模块通常来自这里。

4. **平台相关的标准库和扩展模块路径**

   例如用于存放 `.pyd`、`.so`、`lib-dynload` 等二进制扩展模块的位置。它们也是 import 能找到 C 扩展模块的原因之一。

5. **虚拟环境或解释器环境的 `site-packages`**

   第三方库通常安装在这里，比如 `requests`、`pytest`、`pydantic`。如果启用了虚拟环境，这里的路径会指向虚拟环境，而不是系统 Python 的全局环境。

6. **`.pth` 文件添加的路径**

   `site-packages` 中的 `.pth` 文件可以把额外目录加入 `sys.path`。可编辑安装 `pip install -e .` 常常就依赖这种机制，让 Python 从你的源码目录导入包。

7. **zip 包或由导入钩子支持的路径项**

   `sys.path` 的元素通常是目录，但也可以是 zip 文件等可被导入系统识别的路径项。更高级的导入钩子还可以改变路径项如何被解释。

可以用下面的代码观察当前解释器的真实搜索路径：

```python
import sys

for index, path in enumerate(sys.path):
    # index 是搜索顺序；越靠前，优先级越高
    # path 是一个搜索位置；空字符串 "" 代表当前工作目录
    print(index, repr(path))
```

还要注意一个边界：不是所有模块都来自 `sys.path`。内置模块、冻结模块、已经加载进 `sys.modules` 的模块，会先经过更高层的导入机制处理。日常工程里最常见的文件导入问题，仍然主要落在 `sys.path` 和包的 `__path__` 上。

## 4. 当前工作目录什么时候会进入 `sys.path`

这是一个极其重要的问题，因为它直接决定了你运行代码时会不会遇到 `ModuleNotFoundError`。

当前工作目录，也就是你在终端里敲下回车时所在的目录，通常叫 **CWD**。Python 启动时会设置 `sys.path[0]`，而 `sys.path[0]` 有很高的优先级：导入系统会优先看这里。

**CWD 是否进入 `sys.path[0]`，完全取决于你启动 Python 的方式。**

会把 CWD 放进搜索路径的常见方式有三种。

第一种是直接进入交互式解释器：

```bash
python
```

此时：

```python
import sys

print(sys.path[0]) # ""，空字符串代表当前工作目录
```

第二种是用 `-c` 执行一段代码：

```bash
python -c "import sys; print(repr(sys.path[0]))"
```

此时 `sys.path[0]` 通常也是 `""`，也就是当前工作目录。

第三种是用 `-m` 运行模块：

```bash
python -m my_package.scripts.run_tools
```

此时 `sys.path[0]` 通常会被设置为当前工作目录的绝对路径。

所以，如果你站在项目根目录运行：

```bash
cd my_project
python -m my_package.scripts.run_tools
```

项目根目录会进入搜索路径，顶层包 `my_package` 就能被找到。

## 5. 用文件路径运行脚本时，CWD 通常不会进入 `sys.path[0]`

坑点在这里。

如果你通过文件路径运行脚本：

```bash
python script.py
python ./tests/test_script.py
python /var/www/my_project/main.py
```

此时 `sys.path[0]` 通常不是当前工作目录，而是**脚本文件所在的物理目录**。

例如：

```text
my_project/                  # 当前终端停在这里，也就是 CWD
├─ my_package/
│  ├─ __init__.py
│  └─ tools.py
└─ scripts/
   └─ run_tools.py
```

`scripts/run_tools.py` 中写：

```python
import my_package.tools
```

如果你在项目根目录运行：

```bash
python scripts/run_tools.py
```

它仍然可能报错：

```text
ModuleNotFoundError: No module named 'my_package'
```

原因是：你是通过文件路径运行脚本的，Python 会把 `sys.path[0]` 设置为 `my_project/scripts/`。导入系统会先在 `scripts/` 下面找顶层包 `my_package`，但那里没有这个目录。

当前工作目录虽然是 `my_project/`，但它没有因为这个启动方式自动成为 `sys.path[0]`。

你可以在脚本里临时验证：

```python
import os
import sys

print(os.getcwd())      # 当前工作目录：终端现在所在的位置
print(sys.path[0])      # 导入搜索路径的第一个位置：脚本运行方式决定它
print(sys.path[:3])     # 前几个搜索位置：帮助判断 Python 第一眼看哪里
```

更推荐的运行方式是把脚本放进包里，然后从项目根目录用 `-m` 运行：

```text
my_project/
└─ my_package/
   ├─ __init__.py
   ├─ tools.py
   └─ scripts/
      ├─ __init__.py
      └─ run_tools.py
```

```bash
cd my_project
python -m my_package.scripts.run_tools
```

这样 `my_package` 是从项目根目录这个搜索路径下被找到的，导入关系更稳定。

## 6. 当前工作目录的影响

交互式运行或 `python -c` 时，当前工作目录通常进入 `sys.path`。

```bash
cd project
python
```

此时项目根目录可能在搜索路径中。

换个目录运行，同样的 import 可能失败。这种问题常见于：

- 在 IDE 里能跑，命令行不能跑。
- 在项目根能跑，进入子目录不能跑。
- 本地能跑，CI 不能跑。

根因通常是运行入口和 `sys.path` 不一致。

还有一个细节：`sys.path` 中有时会出现空字符串 `""`，它表示当前工作目录。当前工作目录变了，这个空字符串代表的位置也会变。

## 7. 不要随手修改 `sys.path`

有时会看到：

```python
import sys
sys.path.append("..")
```

这能临时解决导入问题，但通常是工程结构或运行方式没有理顺。

问题：

- 路径依赖当前工作目录。
- 测试和部署环境容易不一致。
- 导入来源变得不透明。
- 可能导入到同名错误模块。

更好的选择：

- 使用包结构。
- 从项目根用 `python -m ...` 运行。
- 在可编辑模式安装项目。
- 配置测试工具的 Python path。

## 8. 可编辑安装

如果运行普通安装命令：`pip install .`（没有 -e），pip 会将你当前目录下的所有代码复制一份，打包并存放到 Python 环境的 site-packages 目录下。这意味着，如果你发现代码有个 Bug 并修改了源文件，你再次运行代码时，执行的依然是 site-packages 里旧的、被复制过去的代码。你必须每次改完代码都重新 `pip install .` 一次。

开发项目时常用可编辑安装：

```bash
python -m pip install -e .
```

或者用项目当前包管理工具执行等价操作。

当你加上 -e 参数（即 --editable）后，pip 改变了策略：它不再复制文件。

它会在 Python 的 site-packages 目录中创建一个“快捷方式”（通常是一个指向你当前源代码绝对路径的 .egg-link 或 .pth 文件）。

每当 Python 尝试 import my_package 时，它会顺着这个快捷方式，直接来到你当前的开发目录读取文件。这就实现了“代码修改，实时生效”，你再也不用反复执行安装命令了。

## 9. 同名遮蔽

搜索路径顺序可能导致同名模块遮蔽标准库或第三方库。

坏例子：

```text
project/
└─ json.py
```

代码：

```python
import json
```

可能导入本地 `json.py`，而不是标准库 `json`。

避免用标准库或常见第三方库名字命名自己的模块：

- `json.py`
- `typing.py`
- `asyncio.py`
- `logging.py`
- `requests.py`
- `pytest.py`

## 10. 检查导入来源

调试导入问题时：

```python
import module

print(module.__file__) # module 实际从哪个文件加载
```

如果是包：

```python
import package
print(package.__path__) # 包搜索子模块的位置
```

也可以打印搜索路径：

```python
import sys
print(sys.path)
```

这些信息能快速判断：Python 找的是不是你以为的那个模块。

## 11. 检查表

遇到 import 找不到或导入错对象时，按下面问：

1. 当前从哪个目录运行程序？
2. `sys.path[0]` 是什么？
3. `sys.path` 中是否有空字符串 `""`，它当前代表哪里？
4. 当前是交互式、`-c`、`-m`，还是文件路径运行？
5. 如果是文件路径运行，`sys.path[0]` 是否变成了脚本所在目录？
6. 项目根目录是否在 `sys.path` 中？
7. 当前导入的是顶层模块，还是包内子模块？
8. 如果是包内子模块，包的 `__path__` 是什么？
9. 模块实际来自哪个 `__file__`？
10. 是否有本地文件遮蔽标准库或第三方库？
11. 是否应该用 `python -m` 运行？
12. 是否应该把项目安装到环境中？

最小心智模型：

1. `sys.path` 决定顶层模块和顶层包的搜索位置。
2. 包内子模块通过包对象的 `__path__` 搜索。
3. 搜索顺序会影响导入结果，第一个匹配胜出。
4. `sys.path[0]` 由启动方式决定，不总是当前工作目录。
5. 交互式、`-c`、`-m` 更容易把当前目录放进搜索路径；文件路径运行脚本时，优先进入的是脚本所在目录。
6. 修改 `sys.path` 是最后手段，不是默认工程方案。
7. 好项目结构应该让导入来源稳定可解释。
