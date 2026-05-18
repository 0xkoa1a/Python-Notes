# 测试辅助

标准库的测试辅助工具不一定替代 pytest，但理解它们能帮助你写更小、更稳的测试边界。

**`unittest.mock` 用来替换外部依赖，`tempfile` 用来隔离文件系统，`doctest` 用来验证文档示例。测试辅助的核心是控制边界。**

## 1. `unittest.mock.Mock`

```python
from unittest.mock import Mock

sender = Mock()
sender.send.return_value = True

result = sender.send("hello")

print(result) # True
sender.send.assert_called_once_with("hello")
```

`sender.send` 是 mock 自动创建的子 Mock。它记录调用信息，便于断言交互。

## 2. `patch`

```python
from unittest.mock import patch

with patch("module.requests.get") as mock_get:
    # mock_get 替换 module 中名为 requests.get 的对象
    mock_get.return_value.text = "ok"
    ...
```

关键原则：patch 使用地点，而不是定义地点。

如果代码里写：

```python
from requests import get
```

你要 patch 的通常是当前模块里的 `get`，不是 `requests.get`。

## 3. 临时目录

```python
from tempfile import TemporaryDirectory
from pathlib import Path

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    path = root / "data.txt"
    path.write_text("hello", encoding="utf-8")
```

退出 `with` 后临时目录清理。测试文件系统逻辑时，临时目录比写真实项目目录安全。

## 4. `doctest`

文档中的示例也可以测试：

```python
def add(x, y):
    """
    >>> add(1, 2)
    3
    """
    return x + y
```

运行 doctest 可以验证示例仍然正确。

`doctest` 适合简单、稳定、说明性的例子。不适合复杂业务测试。

## 5. mock 不要滥用

mock 适合替换外部边界：

- 网络请求。
- 文件系统。
- 数据库。
- 时间。
- 随机数。

不要把内部普通函数全 mock 掉。那样测试只验证你写了什么调用，而不是行为是否正确。

更好的优先级：

1. 纯函数直接测试结果。
2. 文件系统用临时目录。
3. 外部系统用 fake 或 mock。
4. 复杂交互再断言调用。

## 6. 检查表

写测试辅助时，按下面问：

1. 这个依赖是外部边界，还是内部实现？
2. patch 的路径是否是使用地点？
3. mock 是否断言了真正重要的交互？
4. 文件测试是否使用临时目录？
5. doctest 是否适合这个示例？
6. 是否可以用 fake 对象替代复杂 mock？

最小心智模型：

1. 测试辅助用于控制边界。
2. Mock 记录调用并替代依赖。
3. patch 要 patch 使用地点。
4. 临时目录隔离文件系统副作用。
5. 好测试优先验证行为，而不是实现细节。
