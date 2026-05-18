# 路径、文件与系统

路径和文件操作是 Python 最常见的自动化场景。标准库提供了比字符串拼路径更安全、更清楚的工具。

**`pathlib.Path` 把路径作为对象建模；`shutil` 处理文件树操作；`tempfile` 处理临时资源；这些工具让文件系统代码更接近领域动作，而不是字符串拼接。**

## 1. `pathlib.Path`

```python
from pathlib import Path

root = Path("data")
path = root / "users" / "alice.json"

print(path.name)    # alice.json
print(path.suffix)  # .json
print(path.parent)  # data/users
```

`/` 运算符用于拼接路径，不是字符串除法。它返回新的 `Path` 对象。

## 2. 读写文本

```python
from pathlib import Path

path = Path("message.txt")
path.write_text("hello", encoding="utf-8")

text = path.read_text(encoding="utf-8")
```

显式写 `encoding` 是好习惯，避免不同系统默认编码差异。

## 3. 遍历目录

```python
from pathlib import Path

root = Path("src")

for path in root.rglob("*.py"):
    # path 是匹配到的 Path 对象
    print(path)
```

`glob` 只看当前层或模式指定层级，`rglob` 递归。

## 4. 创建和删除

```python
path = Path("logs/app.log")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text("log", encoding="utf-8")
```

删除文件：

```python
path.unlink(missing_ok=True)
```

删除目录树用 `shutil.rmtree`，要非常谨慎：

```python
import shutil

shutil.rmtree("build")
```

删除递归目录前确认目标路径，避免误删。

## 5. 复制和移动

```python
import shutil
from pathlib import Path

src = Path("data/input.txt")
dst = Path("backup/input.txt")

dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)  # copy2 会尽量保留元数据
```

移动：

```python
shutil.move(str(src), str(dst))
```

`shutil` 很多 API 接收 path-like 对象，也可以传字符串。

## 6. 临时文件和目录

```python
from tempfile import TemporaryDirectory
from pathlib import Path

with TemporaryDirectory() as tmp:
    # tmp 是临时目录路径字符串
    path = Path(tmp) / "data.txt"
    path.write_text("hello", encoding="utf-8")

# with 退出后临时目录会被清理
```

临时资源适合测试和中间文件，不要自己随便拼 `/tmp/xxx`。

## 7. 检查表

写文件系统代码时，按下面问：

1. 是否用 `Path` 表达路径？
2. 文本读写是否显式 encoding？
3. 目录创建是否考虑父目录和已存在情况？
4. 删除操作是否确认目标？
5. 测试是否使用临时目录？
6. 是否把路径作为参数传入，而不是写死？

最小心智模型：

1. 路径是对象，不只是字符串。
2. 文件系统操作有副作用，要明确边界。
3. `pathlib` 处理路径，`shutil` 处理高级文件操作。
4. 临时资源交给 `tempfile` 管理。
