# 异常机制

异常不是“程序出错时打印一段红字”。异常是一套控制流机制，用来从当前执行路径跳出，并沿调用栈寻找能处理它的代码。

**异常机制的统一模型是：代码抛出异常对象；解释器沿调用栈传播异常；匹配到处理器就转入处理逻辑；无论是否异常，`finally` 都用于收束资源和状态。**

理解这个模型以后，`try/except/else/finally`、异常链、`raise from`、自定义异常都能统一起来。

## 1. 异常是对象

异常也是对象：

```python
err = ValueError("bad value")
print(type(err))    # <class 'ValueError'>
print(err.args)     # ('bad value',)
```

抛出异常：

```python
raise ValueError("bad value")
```

捕获异常：

```python
try:
    int("abc")
except ValueError as exc:
    print(exc)
```

`except ValueError as exc` 中的 `exc` 绑定到被抛出的异常对象。

异常类型形成继承层次：

```python
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ValueError
    ├── TypeError
    ├── RuntimeError
    └── ...
```

日常业务代码通常捕获 `Exception` 及其子类，不要轻易捕获 `BaseException`，否则可能拦截 `KeyboardInterrupt`、`SystemExit` 这类应让程序退出的信号。

## 2. 异常传播：沿调用栈向外找处理器

```python
def c():
    raise ValueError("boom")

def b():
    c()

def a():
    b()

a()
```

异常从 `c` 抛出，如果 `c` 不处理，就传播到 `b`；`b` 不处理，就传播到 `a`；再不处理，就到顶层，解释器打印 traceback 并终止当前程序。

捕获：

```python
def a():
    try:
        b()
    except ValueError as exc:
        print("handled:", exc)
```

这不是“跳转到最近的 except 语句”这么粗糙，而是：

**异常沿调用栈向外传播，直到找到第一个类型匹配的 `except`。**

## 3. `try/except` 匹配规则

`except` 按从上到下顺序匹配：

```python
try:
    ...
except ValueError:
    ...
except Exception:
    ...
```

更具体的异常应放前面。否则会被更宽泛的异常先捕获：

```python
try:
    ...
except Exception:
    ...
except ValueError:
    ...  # 基本到不了
```

可以捕获多个异常：

```python
try:
    ...
except (ValueError, TypeError) as exc:
    print(exc)
```

不要写过宽的捕获：

```python
try:
    do_work()
except Exception:
    pass
```

这会吞掉真实错误，让程序进入未知状态。

如果确实要捕获并继续，应明确范围和原因：

```python
try:
    config = load_config(path)
except FileNotFoundError:
    config = default_config()
```

## 4. `else`：没有异常时执行

`try/except/else` 中，`else` 只在 `try` 块没有异常时执行：

```python
try:
    value = int(text)
except ValueError:
    print("not an int")
else:
    print(value * 2)
```

为什么不直接写在 `try` 里？

```python
try:
    value = int(text)
    print(value * 2)
except ValueError:
    print("not an int")
```

区别在于：如果 `print(value * 2)` 这部分也可能抛出 `ValueError`，它会被同一个 `except` 捕获，导致错误来源不清楚。

`else` 的价值是缩小 `try` 块范围：

```python
try:
    value = int(text)
except ValueError:
    print("not an int")
else:
    use(value)
```

这样 `except ValueError` 只对应 `int(text)` 的失败。

## 5. `finally`：无论如何都会执行

`finally` 用于收束资源或恢复状态：

```python
f = open("data.txt")
try:
    data = f.read()
finally:
    f.close()
```

无论 `try` 中是否抛异常，`finally` 都会执行。

即使 `try` 中有 `return`，`finally` 也会执行：

```python
def f():
    try:
        return 1
    finally:
        print("cleanup")

print(f())
```

输出：

```text
cleanup
1
```

不要在 `finally` 中随便 `return`，因为它会覆盖异常或原始返回值：

```python
def f():
    try:
        1 / 0
    finally:
        return 42

print(f())  # 42
```

这里 `ZeroDivisionError` 被 `finally` 的 `return` 吞掉了。这种代码非常危险。

## 6. 四段组合的执行语义

完整结构：

```python
try:
    risky()
except ValueError:
    handle()
else:
    success()
finally:
    cleanup()
```

语义：

- `try` 执行可能失败的最小代码。
- `except` 处理匹配异常。
- `else` 在没有异常时执行。
- `finally` 无论是否异常都执行。

几种情况：

```text
try 无异常 -> else -> finally
try 有匹配异常 -> except -> finally
try 有不匹配异常 -> finally -> 异常继续传播
except 或 else 再抛异常 -> finally -> 新异常传播
```

`finally` 的职责是清理，不是正常业务分支。

## 7. 重新抛出异常

在 `except` 中用裸 `raise` 可以重新抛出当前异常，并保留原 traceback：

```python
try:
    do_work()
except ValueError:
    log_error()
    raise
```

不要写成：

```python
except ValueError as exc:
    raise exc
```

这可能改变 traceback，让调试信息变差。需要重新抛出当前异常时，用裸 `raise`。

## 8. 异常链：一个异常来自另一个异常

处理异常时又抛出新异常，Python 会保留异常上下文：

```python
try:
    int("abc")
except ValueError:
    raise RuntimeError("parse failed")
```

traceback 会显示：

```text
During handling of the above exception, another exception occurred:
```

这叫隐式异常链。新异常的 `__context__` 指向原异常。

## 9. `raise from`：显式异常链

如果新异常是对旧异常的语义包装，使用 `raise from`：

```python
def parse_age(text):
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(f"invalid age: {text!r}") from exc
```

traceback 会显示：

```text
The above exception was the direct cause of the following exception:
```

新异常的 `__cause__` 指向原异常。

`raise from` 的价值是让错误层次清楚：

- 底层错误：`int(text)` 解析失败。
- 上层语义：年龄字段非法。

如果故意不想暴露底层异常链，可以用：

```python
raise ValueError("invalid age") from None
```

这会抑制上下文显示。但不要滥用，隐藏原因会降低可调试性。

## 10. 自定义异常

自定义异常通常继承 `Exception`：

```python
class ConfigError(Exception):
    pass
```

使用：

```python
def load_config(path):
    if not path.exists():
        raise ConfigError(f"config not found: {path}")
```

自定义异常的价值不是“看起来更高级”，而是给调用者提供语义化的捕获边界：

```python
try:
    config = load_config(path)
except ConfigError as exc:
    report(exc)
```

可以设计异常层次：

```python
class AppError(Exception):
    pass

class ConfigError(AppError):
    pass

class DatabaseError(AppError):
    pass
```

调用者可以选择捕获具体错误：

```python
except ConfigError:
    ...
```

也可以捕获应用层错误：

```python
except AppError:
    ...
```

## 11. 异常信息应包含调试上下文

坏信息：

```python
raise ValueError("bad value")
```

更有用：

```python
raise ValueError(f"invalid port {port!r}; expected 1..65535")
```

异常信息应该回答：

- 哪个值错了？
- 为什么错？
- 期望是什么？
- 如果有外部资源，路径、URL、字段名是什么？

不要把异常信息写成只有开发者当下才懂的暗号。

## 12. EAFP 与 LBYL

Python 常见风格是 EAFP：

```text
Easier to Ask Forgiveness than Permission
```

也就是先做，失败再捕获异常：

```python
try:
    value = d[key]
except KeyError:
    value = default
```

对比 LBYL：

```text
Look Before You Leap
```

先检查再做：

```python
if key in d:
    value = d[key]
else:
    value = default
```

两者都可以。选择依据不是宗教，而是语义：

- 如果失败是正常分支，且异常范围清楚，EAFP 很自然。
- 如果检查能更清楚表达业务约束，LBYL 更好。
- 在并发或外部资源场景中，先检查再使用可能有竞态，EAFP 更可靠。

例如文件删除：

```python
try:
    path.unlink()
except FileNotFoundError:
    pass
```

比先 `exists()` 再删除更稳，因为检查后文件也可能被别人删掉。

## 13. 不要用异常做普通循环控制

迭代协议内部用 `StopIteration` 表示结束，这是协议的一部分。但业务代码中不要把异常当普通分支滥用：

```python
try:
    value = parse(text)
except ValueError:
    value = default
```

这是合理的，因为解析失败就是异常边界。

但如果每次循环都用异常判断普通条件，可能降低可读性和性能：

```python
for item in items:
    try:
        ...
    except SomeExpectedCase:
        ...
```

如果 `SomeExpectedCase` 其实是大量发生的普通情况，考虑显式分支或调整数据结构。

## 14. `assert` 不是运行时错误处理

`assert` 用于表达内部不变量：

```python
assert total >= 0
```

不要用它处理用户输入：

```python
assert age >= 0
```

因为 Python 可以用优化模式运行：

```bash
python -O app.py
```

优化模式会移除 assert 语句。

用户输入、外部数据、配置错误应显式抛异常：

```python
if age < 0:
    raise ValueError(f"age must be non-negative: {age}")
```

## 15. `ExceptionGroup` 与 `except*`

并发任务中可能同时出现多个异常。现代 Python 支持 `ExceptionGroup`：

```python
raise ExceptionGroup(
    "multiple errors",
    [ValueError("bad value"), TypeError("bad type")],
)
```

可以用 `except*` 分组处理：

```python
try:
    ...
except* ValueError as group:
    # group 是只包含匹配到的 ValueError 的 ExceptionGroup 子组
    # group.exceptions 是这个子组里具体异常对象组成的元组
    handle_values(group.exceptions)
except* TypeError as group:
    # 这里的 group 是只包含 TypeError 的 ExceptionGroup 子组
    handle_types(group.exceptions)
```

普通代码不一定常用它，但理解它有助于阅读 `asyncio.TaskGroup` 等并发代码。

## 16. 设计异常边界

工程代码中最重要的不是“会 raise”，而是设计异常边界。

底层函数应该抛出具体异常：

```python
def read_user(path):
    ...
```

中间层可以包装成领域异常：

```python
try:
    user = read_user(path)
except OSError as exc:
    raise UserLoadError(f"failed to load user from {path}") from exc
```

顶层入口负责转成用户可见信息：

```python
try:
    main()
except AppError as exc:
    print(exc)
    raise SystemExit(1)
```

不要在太底层直接 `print` 并退出；不要在太高层丢失底层原因。异常链就是为这种分层准备的。

## 17. 检查表

遇到异常机制问题，按下面问：

1. 抛出的异常对象是什么类型？
2. 它会沿调用栈传播到哪里？
3. 哪个 `except` 会最先匹配？
4. 捕获范围是否太宽？
5. `else` 是否能缩小 `try` 的范围？
6. `finally` 是否只做清理，是否意外吞掉异常？
7. 重新抛出时是否应该用裸 `raise`？
8. 新异常是否应该用 `raise from` 保留原因？
9. 自定义异常是否表达了清晰的业务边界？
10. 异常信息是否包含足够上下文？

最小心智模型：

1. 异常是对象。
2. `raise` 抛出异常对象。
3. 异常沿调用栈向外传播。
4. `except` 按类型和顺序匹配。
5. `else` 表示无异常路径。
6. `finally` 表示无论如何都执行的收束逻辑。
7. `raise from` 表达异常因果链。
8. 自定义异常用于建立语义边界。

异常机制不是把错误藏起来，而是让错误以结构化方式穿过程序边界。
