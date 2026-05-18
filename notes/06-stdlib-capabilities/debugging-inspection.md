# 调试与检查

调试和检查工具解决的问题是：当程序行为和你的模型不一致时，如何观察运行时事实。

**`pdb` 看执行状态，`traceback` 看异常路径，`inspect` 看对象结构，`dis` 看字节码。它们都是验证理解的显微镜。**

## 1. `pdb`

```python
breakpoint()
```

运行到这里会进入调试器。常用命令：

- `n`：下一行。
- `s`：进入函数。
- `c`：继续运行。
- `p expr`：打印表达式。
- `q`：退出。

`breakpoint()` 比手写 `import pdb; pdb.set_trace()` 更现代，也可通过环境变量禁用或替换。

## 2. `traceback`

捕获异常时保留堆栈：

```python
import traceback

try:
    1 / 0
except ZeroDivisionError:
    text = traceback.format_exc()
    print(text)
```

`format_exc()` 返回当前异常的 traceback 字符串，适合日志记录。

不要捕获异常后只打印 `"error"`，丢掉堆栈会让调试困难。

## 3. `inspect`

```python
import inspect

def f(x: int, y: str = "a") -> None:
    pass

sig = inspect.signature(f)
print(sig) # (x: int, y: str = 'a') -> None
```

`Signature` 对象描述函数参数和返回标注。框架常用它自动解析依赖或生成命令行参数。

查看对象成员：

```python
members = inspect.getmembers(f)
```

## 4. `dis`

`dis` 展示 Python 字节码：

```python
import dis

def add(x, y):
    return x + y

dis.dis(add)
```

字节码不是日常写代码必需，但它能帮助理解：

- 赋值和名字查找。
- 闭包。
- 函数调用。
- 某些性能差异。

不要过度从字节码推导跨实现结论。CPython 字节码是实现细节，但对理解 CPython 很有帮助。

## 5. `repr` 和最小复现

调试时优先让对象有清楚 `repr`：

```python
print(f"value={value!r}")
```

`!r` 能暴露换行、空格、引号、空字符串等细节。

比长篇猜测更有效的是最小复现：

```python
def test_bug():
    ...
```

把问题缩到几行代码，通常就能看见模型哪里错了。

## 6. 检查表

调试时，按下面问：

1. 我观察到的是对象真实状态，还是脑内假设？
2. 是否保留了完整 traceback？
3. 是否能用 `repr` 看见隐藏字符？
4. 是否能用 `inspect` 查看签名和属性？
5. 是否需要 `dis` 验证名字绑定或字节码行为？
6. 是否已经构造最小复现？

最小心智模型：

1. 调试是验证运行时事实。
2. traceback 是控制流历史。
3. inspect 暴露对象元信息。
4. dis 暴露 CPython 执行层细节。
5. 最小复现比猜测更可靠。
