# `sys.modules`

`sys.modules` 回答的问题是：为什么模块通常只导入一次，以及导入过程中为什么会出现“部分初始化模块”。

**`sys.modules` 是模块缓存字典；键是模块名，值是模块对象；导入系统会先查缓存，已有模块对象时直接复用。**

理解它以后，重复 import、模块级状态、循环导入都会清楚很多。

## 1. 模块缓存

```python
import sys
import math

print(sys.modules["math"]) # math 模块对象
```

`sys.modules` 是一个字典：

```text
module name -> module object
```

导入大致流程：

1. 看 `sys.modules` 里是否已有模块名。
2. 如果有，直接返回已有模块对象。
3. 如果没有，创建模块对象并放入缓存。
4. 执行模块代码，填充模块命名空间。

## 2. 重复导入不会重复执行顶层代码

```python
# config.py
print("loading")
VALUE = 1
```

```python
import config # 打印 loading
import config # 通常不再打印
```

第二次导入时，`config` 已经在 `sys.modules` 中，导入系统直接复用模块对象。

这就是模块级状态共享的原因：

```python
# state.py
items = []
```

```python
import state
state.items.append("a")
```

另一个地方：

```python
import state
print(state.items) # ['a']
```

两个导入方看到的是同一个模块对象。

## 3. `from module import name` 也依赖缓存

```python
from state import items
```

这并不是绕过模块缓存。它仍然先加载或复用 `state` 模块对象，然后把当前命名空间中的 `items` 绑定到 `state.items` 当时指向的对象。

```python
import state
from state import items

state.items.append("a")
print(items) # ['a']，items 和 state.items 指向同一个列表对象

state.items = []
print(items) # ['a']，当前名字仍绑定到旧列表
```

要区分“修改共享对象”和“重新绑定模块属性”。

## 4. 部分初始化模块

导入系统会在执行模块代码之前，把新模块对象放入 `sys.modules`。这听起来奇怪，但它是处理递归导入的必要机制。

问题是：如果模块还没执行完，别人就从缓存拿到了它，就会看到部分初始化状态。

示意：

```python
# a.py
import b
VALUE_A = "A"
```

```python
# b.py
import a
print(a.VALUE_A) # a 还没执行到 VALUE_A 赋值
```

可能报错：

```text
AttributeError: partially initialized module 'a' has no attribute 'VALUE_A'
```

这不是 import 随机坏了，而是模块对象已经进缓存，但模块代码还没执行完。

## 5. 重新加载模块

可以用 `importlib.reload` 重新执行模块代码：

```python
import importlib
import config

importlib.reload(config) # 重新执行 config 模块顶层代码
```

但 reload 很少用于正常工程逻辑。它会带来复杂问题：

- 旧对象引用不会自动更新。
- 已经从模块中 `from import` 出来的名字仍指向旧对象。
- 类重新定义后，旧实例仍属于旧类对象。

示例：

```python
from config import VALUE
import importlib
import config

config.VALUE = 2
importlib.reload(config)

print(VALUE) # 仍是之前绑定的对象
```

reload 更适合 REPL、开发工具、插件系统中的特殊场景。

## 6. 不要随便改 `sys.modules`

测试或高级框架有时会操作 `sys.modules`，但普通业务代码不要这样做。

删除缓存：

```python
del sys.modules["config"]
```

下一次 import 可能重新加载模块，但已有模块对象引用不会消失。

更危险的是塞假模块：

```python
sys.modules["config"] = fake_module
```

这会影响整个进程后续导入。除非你在写测试隔离、导入钩子或插件系统，否则不要这么做。

## 7. 检查表

遇到模块缓存问题，按下面问：

1. 模块是否已经在 `sys.modules` 中？
2. 重复 import 是否只是复用缓存？
3. 模块级状态是否被多个地方共享？
4. `from module import name` 是否绑定到了旧对象？
5. 是否遇到了部分初始化模块？
6. 问题是否其实来自循环导入？
7. 是否真的需要 reload？

最小心智模型：

1. `sys.modules` 是模块缓存。
2. 模块名映射到模块对象。
3. 导入前先查缓存。
4. 模块对象会在代码执行前进入缓存。
5. 这解释了循环导入中的部分初始化问题。
