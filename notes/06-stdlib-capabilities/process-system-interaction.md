# 进程与系统交互

Python 常作为胶水语言调用外部程序。标准库里 `subprocess` 是核心工具。

**调用外部进程时，要明确区分参数列表、shell 字符串、标准输入输出、返回码、超时和错误处理。**

这类代码如果写得随意，很容易出现路径、转义、安全和阻塞问题。

## 1. `subprocess.run`

```python
import subprocess

result = subprocess.run(
    ["python", "--version"],
    capture_output=True,
    text=True,
)

print(result.returncode) # 进程退出码
print(result.stdout)     # 标准输出字符串
print(result.stderr)     # 标准错误字符串
```

参数推荐传列表，而不是拼接字符串。列表中每个元素是一个参数，避免空格和转义问题。

## 2. 检查失败

```python
subprocess.run(["python", "--version"], check=True)
```

`check=True` 表示返回码非 0 时抛出 `CalledProcessError`。

```python
try:
    subprocess.run(["false"], check=True)
except subprocess.CalledProcessError as exc:
    # exc.returncode 是子进程退出码
    print(exc.returncode)
```

## 3. 超时

```python
try:
    subprocess.run(["slow-command"], timeout=5, check=True)
except subprocess.TimeoutExpired as exc:
    # exc 是超时异常对象，表示子进程没有在期限内结束
    print("timeout", exc)
```

外部命令可能卡住，生产脚本里要考虑 timeout。

## 4. 避免不必要的 shell

不推荐：

```python
subprocess.run(f"cat {path}", shell=True)
```

如果 `path` 来自用户输入，会有 shell 注入风险。

推荐：

```python
subprocess.run(["cat", str(path)])
```

只有确实需要 shell 特性，如管道、重定向、通配符扩展时，才考虑 `shell=True`，并确保输入可信。

## 5. 环境变量和工作目录

```python
import os
import subprocess

env = os.environ.copy()
env["MODE"] = "test"

subprocess.run(
    ["tool", "run"],
    cwd="project", # 子进程工作目录
    env=env,       # 子进程环境变量
    check=True,
)
```

不要让子进程隐式依赖当前进程的工作目录和环境，除非这是刻意设计。

## 6. `sys` 和平台信息

```python
import sys
import platform

print(sys.executable)  # 当前 Python 解释器路径
print(sys.argv)        # 命令行参数列表
print(platform.system()) # Windows / Linux / Darwin
```

调用当前解释器时，优先使用 `sys.executable`：

```python
subprocess.run([sys.executable, "-m", "pip", "--version"])
```

这能避免调用到另一个 Python。

## 7. 检查表

调用外部系统时，按下面问：

1. 参数是否用列表传递？
2. 是否真的需要 `shell=True`？
3. 是否处理返回码？
4. 是否需要 capture 输出？
5. 是否设置 timeout？
6. 是否明确 cwd 和 env？
7. 是否应该使用 `sys.executable`？

最小心智模型：

1. 子进程是外部边界。
2. 参数列表比 shell 字符串安全清楚。
3. 返回码是错误边界。
4. 超时和环境要显式考虑。
