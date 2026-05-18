# 项目结构

项目结构不是文件摆放审美，而是依赖方向、运行入口、测试边界和发布方式的表达。

**好的 Python 项目结构让导入稳定、职责清楚、测试容易、入口明确；坏结构会让 `sys.path`、循环导入、脚本运行方式和配置加载纠缠在一起。**

结构的目标不是复杂，而是让增长时不混乱。

## 1. 从脚本到项目

单文件脚本可以很简单：

```text
script.py
```

当出现这些信号时，就该考虑项目结构：

- 函数越来越多，难以导航。
- 同一逻辑被多个脚本复制。
- 需要测试。
- 需要配置文件。
- 需要 CLI 参数。
- 需要被别的代码导入。
- 需要打包或部署。

这时应把“可复用逻辑”和“入口脚本”分开。

## 2. 推荐基本结构

```text
project/
├─ pyproject.toml
├─ README.md
├─ src/
│  └─ myapp/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ cli.py
│     ├─ config.py
│     └─ domain/
│        ├─ __init__.py
│        └─ users.py
└─ tests/
   └─ test_users.py
```

`src/` 布局的意义：

- 防止测试时意外导入当前目录下的未安装包。
- 迫使你像真实用户一样导入包。
- 更容易发现打包配置问题。

不使用 `src/` 也可以，但要理解它解决的问题。

## 3. 入口和库代码分离

不要把所有逻辑写进 CLI 文件：

```python
# bad cli.py
import argparse

parser = argparse.ArgumentParser()
args = parser.parse_args()

# 大量业务逻辑直接写在顶层
```

更好的结构：

```python
# cli.py

def main(argv=None) -> int:
    # argv 是可选参数，便于测试传入自定义命令行参数
    args = parse_args(argv)
    return run(args)
```

```python
# __main__.py
from .cli import main

raise SystemExit(main())
```

入口负责解析和组装，业务逻辑放在可导入、可测试的函数或类里。

## 4. 按职责分模块

坏结构常见名字：

```text
utils.py
helpers.py
common.py
misc.py
```

这些模块不是一定不能存在，但它们很容易变成垃圾抽屉。

更好的命名按职责：

```text
config.py       # 配置加载和解析
paths.py        # 路径计算
parsing.py      # 文本解析
repositories.py # 数据访问抽象或实现
serializers.py  # 序列化
cli.py          # 命令行入口
```

模块名应该让读者预测里面有什么。

## 5. 分层依赖

一个常见依赖方向：

```text
CLI / API / jobs
        ↓
services
        ↓
domain
        ↓
small utilities
```

外层依赖内层，内层不依赖外层。

例如：

```text
cli.py         -> services.py
services.py    -> domain/users.py
domain/users.py 不应该导入 cli.py
```

这样领域代码可以被 CLI、Web API、测试同时复用。

## 6. 配置与副作用边界

导入模块时不要立刻读取环境、打开文件、连接数据库：

```python
# bad
DATABASE_URL = os.environ["DATABASE_URL"]
connection = connect(DATABASE_URL)
```

更好：

```python
def load_config(env=os.environ):
    # env 是可替换依赖，测试时可以传入普通字典
    return Config(database_url=env["DATABASE_URL"])

def create_connection(config):
    return connect(config.database_url)
```

这样导入模块不会产生外部副作用，测试也更容易。

## 7. 内部 API 与公共 API

包顶层 `__init__.py` 可以暴露公共 API：

```python
from .domain.users import User

__all__ = ["User"]
```

但内部模块之间不一定要通过包顶层绕一圈：

```python
# 内部模块可以直接导入真实来源
from myapp.domain.users import User
```

公共 API 是给包使用者的稳定界面。内部结构可以更细，但不要让外部依赖所有内部路径。

## 8. `pyproject.toml`

现代 Python 项目通常用 `pyproject.toml` 作为项目元数据和工具配置入口：

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.11"

[project.scripts]
myapp = "myapp.cli:main"
```

`project.scripts` 可以生成命令行入口。安装后可以运行：

```bash
myapp
```

它会调用 `myapp.cli:main`。

## 9. 检查表

设计项目结构时，按下面问：

1. 哪些代码是可复用库，哪些只是入口？
2. 导入是否依赖当前工作目录？
3. 模块名是否表达职责？
4. 是否有 `utils` 式杂物箱正在变大？
5. 依赖方向是否从外层指向内层？
6. 导入模块是否产生外部副作用？
7. 测试是否能导入真实包？
8. CLI 是否通过可测试的 `main()` 暴露？

最小心智模型：

1. 项目结构表达依赖方向。
2. 入口代码和业务逻辑应分离。
3. 模块职责要清楚。
4. 导入时副作用要少。
5. `src/` 布局帮助暴露打包和导入问题。
