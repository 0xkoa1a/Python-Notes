# NumPy / PyTorch 的性能边界

NumPy 和 PyTorch 快，不是因为 Python 语法变快了，而是因为 Python 只负责调度，核心计算交给底层高效实现。

**Python 适合表达计算图、调度操作和组织实验；大规模数值计算应尽量落在数组/张量库的批量操作中，而不是 Python for-loop 中。**

## 1. Python 循环的成本

```python
total = 0
for x in values:
    total += x * x
```

每次循环都在 Python 层执行：

- 取对象。
- 做动态类型操作。
- 调用协议。
- 更新名字绑定。

次数大时，解释器开销显著。

## 2. 向量化

NumPy：

```python
import numpy as np

values = np.array([1, 2, 3])
result = values * values
```

`values * values` 一次 Python 调用进入底层数组循环。循环在 C 层执行。

PyTorch：

```python
import torch

x = torch.tensor([1.0, 2.0, 3.0])
y = x * x
```

同样，Python 负责发起张量操作，底层负责执行。

## 3. 批量操作比逐元素操作重要

坏：

```python
out = []
for x in tensor:
    out.append(x.item() * 2)
```

好：

```python
out = tensor * 2
```

逐元素 `.item()` 会把数据从张量世界拉回 Python 标量，破坏批量计算。

## 4. 数据搬运成本

GPU 场景中，数据搬运可能比计算更贵：

```python
x_cpu = x_gpu.cpu()
```

频繁 CPU/GPU 来回转换会拖慢程序。

原则：

- 尽量让数据停留在同一设备。
- 批量搬运，避免循环里搬运。
- 不要在训练循环中频繁 `.item()`、`.cpu()`、`.numpy()`。

## 5. 自动微分边界

PyTorch 中：

```python
loss.backward()
```

依赖前面操作构建的计算图。某些 Python 操作会切断图：

```python
value = tensor.item() # 变成 Python 标量，不再带梯度信息
```

理解边界：

- 张量操作可被 autograd 跟踪。
- Python 控制流可以组织计算，但 Python 标量不在计算图中。
- `detach()` 明确断开梯度。

## 6. 什么时候不用向量化

不是所有代码都必须向量化。向量化可能降低可读性，或者创建巨大中间数组。

判断：

- 数据规模小：清楚优先。
- 热点路径：测量后优化。
- 向量化会创建巨大中间对象：考虑分块、原地操作或专门库。
- 控制流复杂：可能需要 JIT、Numba、C++/CUDA 扩展。

## 7. 检查表

写数值代码时，按下面问：

1. 核心循环是否在 Python 层？
2. 是否能改成数组/张量批量操作？
3. 是否频繁 `.item()` 或 `.cpu()`？
4. 数据是否频繁跨设备搬运？
5. 是否意外切断 autograd 计算图？
6. 是否先测量过热点？

最小心智模型：

1. NumPy/PyTorch 快在底层循环。
2. Python 做调度，不做逐元素核心计算。
3. 批量操作减少解释器开销。
4. 数据搬运也是成本。
5. 性能边界要通过 profiling 确认。
