# 日志、配置与 CLI

日志、配置和 CLI 是应用程序的外部边界：用户怎样传入意图，程序怎样读取环境，运行过程怎样被观察。

**CLI 负责把字符串参数解析成结构化输入；配置负责把外部环境变成内部对象；日志负责记录过程而不是替代用户输出。**

## 1. `argparse`

```python
import argparse

def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)
```

`argv=None` 表示默认读真实命令行。测试时可以传入列表。

```python
args = parse_args(["data.txt", "--verbose"])
```

## 2. `logging`

```python
import logging

logger = logging.getLogger(__name__)

def process(item):
    logger.info("processing %r", item)
```

库模块只创建 logger 并发日志，应用入口负责配置：

```python
def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level)
```

不要在库模块导入时调用 `basicConfig`。

## 3. 日志级别

常见级别：

- `DEBUG`：开发调试细节。
- `INFO`：正常运行过程。
- `WARNING`：可恢复但值得注意。
- `ERROR`：操作失败。
- `CRITICAL`：严重故障。

```python
logger.warning("config file %s not found, using defaults", path)
```

日志消息用 `%s` 参数化，让 logging 决定是否格式化。

## 4. 配置对象

```python
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    data_dir: str
    debug: bool = False

def load_config(env=os.environ) -> Config:
    # env 可以是真实 os.environ，也可以是测试传入的 dict
    return Config(
        data_dir=env.get("DATA_DIR", "data"),
        debug=env.get("DEBUG") == "1",
    )
```

内部代码接收 `Config`，不要到处读取环境变量。

## 5. `configparser`

INI 配置：

```python
import configparser

config = configparser.ConfigParser()
config.read("app.ini", encoding="utf-8")

host = config["server"]["host"]
port = config["server"].getint("port")
```

`configparser` 适合传统 INI。TOML 则用 `tomllib` 读取。

## 6. CLI 主函数

```python
def main(argv=None) -> int:
    args = parse_args(argv)
    configure_logging(args.verbose)
    config = load_config()
    return run(args.path, config)

if __name__ == "__main__":
    raise SystemExit(main())
```

`main` 返回退出码，入口把它交给 `SystemExit`。

## 7. 检查表

设计 CLI 和配置时，按下面问：

1. 参数解析是否能被测试？
2. 配置是否集中加载？
3. 业务逻辑是否依赖配置对象而不是环境变量？
4. 日志是否由入口统一配置？
5. 日志和用户输出是否分离？
6. main 是否返回退出码？

最小心智模型：

1. CLI 把字符串转成结构化参数。
2. 配置把外部环境转成内部对象。
3. 日志记录过程，print 输出结果。
4. 入口负责组装和退出码。
