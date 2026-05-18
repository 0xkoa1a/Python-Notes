# `python file.py` 与 `python -m package.module`

Python 文件既可以被当作脚本直接运行，也可以被当作模块运行。这两种方式看起来都在执行同一份代码，但运行时身份不同。

**`python file.py` 按文件路径执行脚本；`python -m package.module` 按模块名执行模块。后者会保留包上下文，更适合运行包内代码。**

理解这点，才能稳定处理入口、相对导入和项目运行方式。

## 1. 直接运行文件

```bash
python scripts/run.py
```

这表示：把 `scripts/run.py` 当作顶层脚本执行。

此时常见情况：

- `__name__ == "__main__"`
- `__package__` 可能为空或 `None`
- `sys.path[0]` 是脚本所在目录

脚本文件所在目录会影响导入搜索路径。

## 2. 以模块方式运行

```bash
python -m myapp.scripts.run
```

这表示：按模块名 `myapp.scripts.run` 找到并执行。

此时：

- `__name__ == "__main__"`
- `__package__ == "myapp.scripts"`
- 包上下文存在
- 相对导入可以正常工作

模块方式运行适合包内入口。

## 3. `__name__ == "__main__"`

常见入口保护：

```python
def main() -> int:
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

含义：

- 文件被直接执行或用 `-m` 作为入口执行时，`__name__` 是 `"__main__"`。
- 文件被普通 import 时，`__name__` 是模块名。

这能防止导入模块时直接执行 CLI 逻辑。

不要把大量业务逻辑直接写在 `if __name__ == "__main__"` 下面。更好的结构是放进 `main()`，入口只负责调用。

## 4. 为什么直接运行包内文件容易出问题

结构：

```text
myapp/
├─ __init__.py
└─ tools/
   ├─ __init__.py
   ├─ helper.py
   └─ run.py
```

`run.py`：

```python
from .helper import work

def main():
    work()

if __name__ == "__main__":
    main()
```

直接运行：

```bash
python myapp/tools/run.py
```

可能失败，因为 `run.py` 没有作为 `myapp.tools` 包的一部分运行。

正确：

```bash
python -m myapp.tools.run
```

这样 `__package__` 是 `myapp.tools`，相对导入有上下文。

## 5. `__main__.py`

包可以定义 `__main__.py`：

```text
myapp/
├─ __init__.py
└─ __main__.py
```

运行：

```bash
python -m myapp
```

会执行：

```text
myapp/__main__.py
```

这适合让整个包成为可运行入口。

`__main__.py` 通常很薄：

```python
from .cli import main

raise SystemExit(main())
```

真正 CLI 逻辑放在 `cli.py` 或应用层函数中。

## 6. 入口函数返回退出码

推荐：

```python
def main(argv=None) -> int:
    # argv 是可选参数，测试时可以传入自定义参数列表
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

`SystemExit(code)` 会把返回码交给操作系统。

这样测试时可以直接调用：

```python
def test_main():
    assert main(["--help"]) == 0
```

比在模块导入时直接解析真实命令行更容易测试。

## 7. 运行方式应该写进文档

如果项目要求：

```bash
python -m myapp
```

就不要在文档里写：

```bash
python myapp/__main__.py
```

运行方式是工程接口的一部分。不同运行方式会改变模块身份和导入上下文。

## 8. 检查表

遇到脚本运行问题，按下面问：

1. 当前是按文件路径运行，还是按模块名运行？
2. `__name__` 是什么？
3. `__package__` 是什么？
4. 是否需要相对导入？
5. `sys.path[0]` 是项目根，还是脚本目录？
6. 是否应该提供 `__main__.py`？
7. CLI 逻辑是否放进可测试的 `main()`？

最小心智模型：

1. `python file.py` 执行文件路径。
2. `python -m package.module` 执行模块名。
3. 包内模块优先用 `-m` 运行。
4. `__name__ == "__main__"` 表示入口执行。
5. `__package__` 决定相对导入上下文。
