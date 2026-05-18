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

当你写：

```python
import config
```

Python 会沿 `sys.path` 查找：

```text
path/config.py
path/config/__init__.py
```

找到后再加载模块。

## 2. 第一个路径为什么重要

运行脚本：

```bash
python scripts/run.py
```

`sys.path[0]` 通常是脚本所在目录 `scripts/`。

这会影响导入：

```text
project/
├─ app/
│  └─ config.py
└─ scripts/
   └─ run.py
```

如果 `run.py` 写：

```python
import app.config
```

可能失败，因为项目根目录未必在 `sys.path` 中。

这就是为什么工程代码经常推荐从项目根目录用模块方式运行：

```bash
python -m app.scripts.run
```

这一点会在脚本执行章节展开。

## 3. 当前工作目录的影响

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

## 4. 不要随手修改 `sys.path`

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

## 5. 可编辑安装

开发项目时常用可编辑安装：

```bash
python -m pip install -e .
```

或者用项目当前包管理工具执行等价操作。

这样项目包会以开发模式出现在环境中，导入不依赖当前目录运气：

```python
import my_package
```

可编辑安装的意义不是复制代码，而是让环境知道这个项目包的位置。

## 6. 同名遮蔽

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

## 7. 检查导入来源

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

## 8. 检查表

遇到 import 找不到或导入错对象时，按下面问：

1. 当前从哪个目录运行程序？
2. `sys.path[0]` 是什么？
3. 项目根目录是否在 `sys.path` 中？
4. 模块实际来自哪个 `__file__`？
5. 是否有本地文件遮蔽标准库或第三方库？
6. 是否应该用 `python -m` 运行？
7. 是否应该把项目安装到环境中？

最小心智模型：

1. `sys.path` 决定导入搜索位置。
2. 搜索顺序会影响导入结果。
3. 运行方式会改变搜索路径。
4. 修改 `sys.path` 是最后手段，不是默认工程方案。
5. 好项目结构应该让导入来源稳定可解释。
