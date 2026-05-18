# 文本与数据格式

文本和数据格式模块解决的是边界转换问题：外部世界给你的是字符串、JSON、CSV、TOML、正则匹配结果，内部代码需要结构化对象。

**解析和序列化都应该使用标准库工具，而不是靠手写字符串切分凑出来。**

## 1. `json`

```python
import json

text = '{"name": "Alice", "age": 20}'
data = json.loads(text)

print(data["name"])  # data 是普通 dict/list/str/int 等组合
```

写出：

```python
payload = {"name": "Alice", "age": 20}
text = json.dumps(payload, ensure_ascii=False, indent=2)
```

文件：

```python
from pathlib import Path
import json

path = Path("user.json")
data = json.loads(path.read_text(encoding="utf-8"))
```

外部 JSON 解析后仍需要验证形状和类型。

## 2. `csv`

```python
import csv
from pathlib import Path

with Path("users.csv").open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # row 是 dict[str, str]，CSV 字段默认都是字符串
        print(row["name"])
```

写 CSV：

```python
with Path("out.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 20})
```

`newline=""` 是 `csv` 官方推荐，避免换行处理被平台默认行为干扰。

## 3. `tomllib`

读取 TOML 配置：

```python
import tomllib
from pathlib import Path

with Path("pyproject.toml").open("rb") as f:
    data = tomllib.load(f)
```

`tomllib` 只负责读取，不负责写 TOML。配置读取后仍是普通字典，需要转换成内部配置对象。

## 4. `re`

正则适合模式匹配，不适合解析复杂嵌套语言。

```python
import re

pattern = re.compile(r"(?P<name>\w+)=(?P<value>\d+)")
match = pattern.fullmatch("age=20")

if match:
    # groupdict 返回命名捕获组字典
    print(match.groupdict())  # {'name': 'age', 'value': '20'}
```

常用：

- `fullmatch`：整个字符串匹配。
- `match`：从开头匹配。
- `search`：任意位置搜索。
- `findall` / `finditer`：找多个。

优先用 `fullmatch` 表达“整个输入必须符合格式”。

## 5. `pickle`

`pickle` 可以序列化 Python 对象，但不安全：

```python
import pickle

data = pickle.dumps({"x": 1})
obj = pickle.loads(data)
```

不要反序列化不可信来源的 pickle。它可以执行任意代码。

适合：

- 自己控制的缓存。
- 本地临时数据。
- 同一信任边界内的 Python 对象。

不适合：

- 网络输入。
- 用户上传文件。
- 长期稳定数据格式。

## 6. 检查表

处理文本和数据格式时，按下面问：

1. 数据格式是否应该由标准库解析？
2. 文本编码是否明确？
3. 外部数据解析后是否验证？
4. CSV 字段是否仍是字符串？
5. 正则是否用了合适的 `fullmatch` / `search`？
6. pickle 数据来源是否可信？

最小心智模型：

1. 外部数据进入系统需要解析。
2. 解析结果不等于已验证对象。
3. JSON/CSV/TOML 都会变成普通 Python 数据结构。
4. pickle 只用于可信边界。
