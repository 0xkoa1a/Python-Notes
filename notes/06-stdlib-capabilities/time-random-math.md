# 时间、随机与数学

时间、随机和数学模块看起来分散，但它们都在处理“基础值的正确建模”：时间点、持续时间、随机性、数值计算。

**不要用字符串表示时间，不要用随机数做安全令牌，不要把浮点数当精确十进制。标准库提供了对应工具。**

## 1. `datetime`

```python
from datetime import datetime, timezone

now = datetime.now(timezone.utc)
print(now.isoformat())
```

带时区的 datetime 比 naive datetime 更明确。跨系统、日志、数据库中，优先使用 UTC。

解析 ISO 时间：

```python
dt = datetime.fromisoformat("2026-05-19T12:00:00+00:00")
```

## 2. `date`、`time`、`timedelta`

```python
from datetime import date, timedelta

today = date.today()
tomorrow = today + timedelta(days=1)
```

`timedelta` 表示持续时间或时间差，不表示具体时间点。

```python
elapsed = end - start  # elapsed 是 timedelta
```

## 3. `time`

测量耗时：

```python
import time

start = time.perf_counter()
do_work()
elapsed = time.perf_counter() - start
```

`perf_counter()` 适合计时。不要用 `datetime.now()` 做性能计时。

睡眠：

```python
time.sleep(0.5)
```

`sleep` 会阻塞当前线程。

## 4. `random` 与 `secrets`

普通随机：

```python
import random

print(random.choice(["a", "b", "c"]))
print(random.randint(1, 6))
```

`random` 适合模拟、抽样、测试数据，不适合安全令牌。

安全随机：

```python
import secrets

token = secrets.token_urlsafe(32)
```

密码、token、验证码等安全场景用 `secrets`。

## 5. `math` 与 `statistics`

```python
import math
import statistics

print(math.sqrt(9))
print(math.isclose(0.1 + 0.2, 0.3))
print(statistics.mean([1, 2, 3]))
```

浮点比较不要直接用 `==`：

```python
math.isclose(a, b, rel_tol=1e-9)
```

## 6. `decimal`

金额等十进制精确场景：

```python
from decimal import Decimal

price = Decimal("0.10")
total = price * 3

print(total)  # 0.30
```

不要用浮点字面量创建 Decimal：

```python
Decimal(0.1)    # 带入二进制浮点误差
Decimal("0.1")  # 更正确
```

## 7. 检查表

处理时间和数值时，按下面问：

1. 这是时间点，还是持续时间？
2. datetime 是否带时区？
3. 计时是否使用 `perf_counter`？
4. 随机数是否涉及安全？
5. 浮点比较是否用 `isclose`？
6. 金额是否应该用 `Decimal`？

最小心智模型：

1. 时间点和时间差是不同对象。
2. UTC 带时区时间更适合跨系统。
3. 性能计时用单调高精度时钟。
4. 安全随机用 `secrets`。
5. 十进制精确计算用 `Decimal`。
