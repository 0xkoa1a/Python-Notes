# 测试、配置、日志与 CLI

测试、配置、日志和 CLI 看起来是工程杂项，但它们都围绕同一个问题：程序如何和外部世界建立边界。

**测试要求逻辑可隔离；配置要求外部输入可显式注入；日志要求运行过程可观察；CLI 要求用户输入被解析成清晰的函数调用。**

这四件事做好了，Python 项目会从“能跑的脚本”变成“可维护的工具”。

## 1. 测试边界

可测试代码通常有两个特征：

- 核心逻辑是普通函数或类。
- 外部依赖通过参数传入，而不是在函数内部硬编码。

难测：

```python
def load_users():
    with open("users.json") as f:
        return parse_users(f.read())
```

更好：

```python
def load_users_from_text(text: str):
    return parse_users(text)

def load_users_from_file(path):
    with open(path, encoding="utf-8") as f:
        return load_users_from_text(f.read())
```

测试核心逻辑时不需要真实文件：

```python
def test_load_users_from_text():
    users = load_users_from_text('[{"name": "Alice"}]')
    assert users[0].name == "Alice"
```

## 2. 测试目录

常见结构：

```text
project/
├─ src/
│  └─ myapp/
└─ tests/
   ├─ test_config.py
   └─ test_users.py
```

测试文件命名清楚：

```text
test_<module>.py
```

测试函数命名表达行为：

```python
def test_parse_user_rejects_missing_name():
    ...
```

好的测试名本身就是文档。

## 3. 配置对象

不要让业务逻辑到处读环境变量：

```python
import os

def connect():
    url = os.environ["DATABASE_URL"]
    ...
```

更好：

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    database_url: str
    debug: bool = False

def load_config(env) -> Config:
    # env 是映射对象，可以是 os.environ，也可以是测试用 dict
    return Config(
        database_url=env["DATABASE_URL"],
        debug=env.get("DEBUG") == "1",
    )
```

入口层读取外部环境，内部逻辑接收 `Config` 对象：

```python
def run(config: Config) -> int:
    ...
```

这样配置来源可以替换，测试也不会依赖真实环境。

## 4. 日志不是 print

`print` 适合 CLI 输出给用户；`logging` 适合记录程序运行过程。

```python
import logging

logger = logging.getLogger(__name__)

def process(item):
    logger.info("processing item %r", item)
```

`__name__` 让日志带上模块名，便于定位来源。

不要在库模块里随便配置全局 logging：

```python
# 库代码中通常不要这样做
logging.basicConfig(level=logging.INFO)
```

配置日志应该由应用入口负责：

```python
def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level)
```

库负责发日志，入口负责决定日志怎么显示。

## 5. CLI 解析

最小 `argparse`：

```python
import argparse

def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)
```

`argv=None` 表示默认读取真实命令行；测试时可以传入列表：

```python
args = parse_args(["data.txt", "--verbose"])
```

主函数：

```python
def main(argv=None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)
    return run(args.path)
```

入口：

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

## 6. 用户输出与日志分离

CLI 有两类输出：

- 给用户看的结果。
- 给开发者或运维看的运行日志。

例如：

```python
def main(argv=None) -> int:
    args = parse_args(argv)
    result = run(args.path)
    print(result.summary) # 用户输出
    return 0
```

内部过程：

```python
logger.debug("loaded %d records", len(records))
```

不要把调试日志混进用户结果，也不要用 `print` 代替可配置日志。

## 7. 错误边界

底层抛具体异常：

```python
def parse_config(text):
    if not text:
        raise ValueError("empty config")
```

应用层转换为用户可理解的信息：

```python
def main(argv=None) -> int:
    try:
        args = parse_args(argv)
        return run(args)
    except ConfigError as exc:
        print(f"error: {exc}")
        return 2
```

不要在底层函数里直接 `sys.exit()`。底层应该抛异常，入口决定如何退出。

## 8. 测试 CLI

如果 `main` 接收 `argv`，就容易测试：

```python
def test_main_accepts_verbose(tmp_path):
    # tmp_path 是 pytest 提供的临时目录 Path 对象
    path = tmp_path / "data.txt"
    path.write_text("data", encoding="utf-8")

    code = main([str(path), "--verbose"])

    assert code == 0
```

这里测试的是入口函数，不需要真的启动子进程。

只有当你要测试安装后的命令行行为时，才需要更重的 subprocess 测试。

## 9. 检查表

工程入口设计时，按下面问：

1. 核心逻辑是否能不依赖真实文件、真实环境、真实命令行来测试？
2. 配置是否被集中加载成对象？
3. 库模块是否避免配置全局 logging？
4. CLI 是否通过 `main(argv=None)` 暴露？
5. 用户输出和日志是否分离？
6. 底层是否避免直接退出进程？
7. 测试是否覆盖错误路径？

最小心智模型：

1. 测试需要可替换边界。
2. 配置是外部输入，应显式注入。
3. 日志是可观察性，不是用户输出。
4. CLI 是把字符串参数转换成函数调用。
5. 入口层负责退出码，底层负责抛异常。
