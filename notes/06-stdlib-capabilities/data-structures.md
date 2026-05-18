# 数据结构

标准库的数据结构解决的问题是：不用每次都拿 `list` 和 `dict` 硬凑。

**选择数据结构，就是选择操作成本和语义。`collections`、`heapq`、`bisect` 等模块提供了常见工程场景的现成模型。**

## 1. `defaultdict`

按键聚合时：

```python
from collections import defaultdict

groups: defaultdict[str, list[int]] = defaultdict(list)

for name, score in [("Alice", 90), ("Bob", 80), ("Alice", 95)]:
    # 第一次访问缺失 key 时，defaultdict 会调用 list() 创建默认值
    groups[name].append(score)

print(groups["Alice"])  # [90, 95]
```

`defaultdict(list)` 的核心是“缺失时自动创建空列表”。

## 2. `Counter`

计数：

```python
from collections import Counter

counts = Counter("abracadabra")

print(counts["a"])          # 5
print(counts.most_common(2)) # [('a', 5), ('b', 2)]
```

`Counter` 是专门的多重集合。比手写字典计数更清楚。

## 3. `deque`

双端队列：

```python
from collections import deque

q = deque()
q.append("right")
q.appendleft("left")

print(q.popleft()) # left
print(q.pop())     # right
```

`list.pop(0)` 是 O(n)，因为要移动后续元素。`deque.popleft()` 是 O(1)，适合队列。

固定长度缓存：

```python
recent = deque(maxlen=3)

for x in range(5):
    recent.append(x)

print(list(recent))  # [2, 3, 4]
```

## 4. `namedtuple`

轻量不可变记录：

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)

print(p.x)
print(p[0])
```

现代代码中，很多场景可以用 `dataclass(frozen=True)` 替代。`namedtuple` 仍常见于兼容老代码、简单元组返回值、标准库 API。

## 5. `heapq`

优先队列：

```python
import heapq

heap: list[tuple[int, str]] = []

heapq.heappush(heap, (3, "low"))
heapq.heappush(heap, (1, "high"))
heapq.heappush(heap, (2, "middle"))

priority, item = heapq.heappop(heap)
print(priority, item)  # 1 high
```

`heapq` 实现最小堆。元组会按字典序比较，所以 `(priority, item)` 常用作堆元素。

如果 item 不可比较，加入序号避免同优先级比较 item：

```python
counter = 0
heapq.heappush(heap, (priority, counter, item))
```

## 6. `bisect`

维护有序列表：

```python
import bisect

values = [1, 3, 5]
bisect.insort(values, 4)

print(values)  # [1, 3, 4, 5]
```

查插入位置：

```python
index = bisect.bisect_left(values, 3)
```

`bisect` 查找是 O(log n)，但插入列表仍是 O(n)，因为要移动元素。它适合中小规模有序列表，不适合高频大规模插入。

## 7. 选择表

常见选择：

- 需要按键查找：`dict`
- 需要去重和集合运算：`set`
- 需要保持顺序序列：`list`
- 需要队列两端操作：`deque`
- 需要计数：`Counter`
- 需要分组聚合：`defaultdict`
- 需要优先队列：`heapq`
- 需要有序列表查找插入点：`bisect`

## 8. 检查表

选择数据结构时，按下面问：

1. 最常见操作是什么：查找、插入、删除、排序、计数、队列？
2. 是否需要保持顺序？
3. 是否需要去重？
4. 是否需要按优先级取最小值？
5. 手写 dict/list 是否隐藏了已有抽象？
6. 数据规模是否让操作复杂度变重要？

最小心智模型：

1. 数据结构表达操作语义。
2. 标准库已经覆盖很多常见模式。
3. 不要用 `list` 和 `dict` 解决所有问题。
4. 复杂度和可读性都要考虑。
