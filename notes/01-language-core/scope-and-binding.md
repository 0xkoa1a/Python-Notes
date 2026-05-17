# 作用域与名字解析

Python 的作用域机制不是“变量在哪里都能找一找”这么简单。更准确的模型是：

**Python 程序在运行时维护多个命名空间；名字解析按照确定的顺序在这些命名空间中查找；赋值语句决定一个名字属于哪个作用域。**

只要抓住“命名空间 + 绑定 + 查找顺序 + 编译期作用域判定”这条线，`UnboundLocalError`、闭包、`nonlocal`、`global`、late binding 都不再是特殊规则。

## 1. 名字与命名空间

名字不是对象本身。名字存在于命名空间中，命名空间可以粗略理解为“名字到对象的映射”。

```python
x = 1
```

这句代码的含义是：在当前命名空间中，把名字 `x` 绑定到整数对象 `1`。

常见命名空间包括：

- 局部命名空间：函数调用时创建，用来保存局部变量和参数。
- 全局命名空间：模块级命名空间。
- 内置命名空间：`len`、`range`、`print`、`Exception` 等内置名字所在的命名空间。
- 类命名空间：执行类定义体时使用的命名空间。

命名空间是 Python 动态性的基础。模块、函数、类、对象属性，本质上都和“某个地方保存了一批名字绑定”有关。

## 2. LEGB：名字查找顺序

在普通表达式中读取一个名字时，Python 按 LEGB 顺序查找：

```text
Local -> Enclosing -> Global -> Builtins
```

- `Local`：当前函数的局部作用域。
- `Enclosing`：外层函数的作用域，只存在于嵌套函数中。
- `Global`：当前模块的全局作用域。
- `Builtins`：内置作用域。

例如：

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)

    inner()

outer()  # local
```

如果去掉 `inner` 里的 `x`：

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        print(x)

    inner()

outer()  # enclosing
```

再去掉 `outer` 里的 `x`：

```python
x = "global"

def outer():
    def inner():
        print(x)

    inner()

outer()  # global
```

如果全局也没有，才会去内置作用域找：

```python
print(len([1, 2, 3]))  # len 来自 builtins
```

## 3. 赋值决定局部作用域

Python 有一个非常重要的规则：

**如果一个名字在函数体内被赋值，并且没有声明为 `global` 或 `nonlocal`，那么这个名字在该函数中被视为局部名字。**

这条规则是在编译函数体时决定的，不是运行到赋值那一行才决定的。

看这个例子：

```python
x = 10

def f():
    print(x)
    x = 20

f()
```

结果不是打印 `10`，而是抛出：

```text
UnboundLocalError: cannot access local variable 'x' where it is not associated with a value
```

原因不是 LEGB 失效了，而是编译器看到函数体中有 `x = 20`，于是判定 `x` 是 `f` 的局部名字。执行 `print(x)` 时，Python 会在局部作用域找 `x`，但此时局部 `x` 还没有绑定对象。

统一理解：

```text
读取名字：按作用域规则查找。
赋值名字：在当前作用域创建或更新绑定。
函数体内出现赋值：该名字默认属于当前函数局部作用域。
```

## 4. `global`：修改模块级绑定

如果想在函数内部重新绑定模块级名字，需要用 `global`：

```python
count = 0

def inc():
    global count
    count += 1

inc()
print(count)  # 1
```

`global count` 的意思不是“从全局读取 `count`”。读取本来就会按 LEGB 找到全局名字。它真正改变的是赋值目标：

**`global` 告诉 Python：这个函数内对该名字的赋值，发生在模块全局命名空间。**

对比：

```python
count = 0

def bad_inc():
    count += 1

bad_inc()
```

这里 `count += 1` 包含读取和赋值。由于函数体中对 `count` 有赋值，`count` 被判定为局部名字；读取局部 `count` 时它还没有绑定，于是报 `UnboundLocalError`。

工程上，频繁使用 `global` 通常意味着状态边界不清晰。更好的做法往往是把状态放进对象、闭包、配置结构，或者显式作为参数传递。

## 5. `nonlocal`：修改外层函数绑定

`nonlocal` 用于嵌套函数。它表示：这个名字不是当前局部变量，而是来自最近的外层函数作用域。

```python
def make_counter():
    count = 0

    def inc():
        nonlocal count
        count += 1
        return count

    return inc

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
```

如果没有 `nonlocal`：

```python
def make_counter():
    count = 0

    def inc():
        count += 1
        return count

    return inc
```

`count += 1` 会让 `count` 被判定为 `inc` 的局部名字，于是读取时失败。

`nonlocal` 和 `global` 的区别：

- `global` 指向模块级命名空间。
- `nonlocal` 指向外层函数作用域。
- `nonlocal` 不能绑定到全局作用域，也不能凭空创建一个外层名字。

例如：

```python
def outer():
    def inner():
        nonlocal missing
        missing = 1
```

这会报语法错误，因为外层函数作用域中没有 `missing`。

## 6. 闭包：函数携带外层环境

闭包不是魔法。闭包是：

**一个内部函数引用了外层函数的局部名字；即使外层函数已经返回，被引用的绑定仍然被内部函数保存。**

```python
def make_adder(n):
    def add(x):
        return x + n

    return add

add10 = make_adder(10)
print(add10(5))  # 15
```

`make_adder(10)` 调用结束后，按普通直觉，局部变量 `n` 好像应该消失。但 `add` 需要继续使用 `n`，所以 Python 会把 `n` 放入闭包 cell 中，让返回的函数对象持有它。

可以观察：

```python
def make_adder(n):
    def add(x):
        return x + n

    return add

add10 = make_adder(10)

print(add10.__closure__)
print(add10.__closure__[0].cell_contents)  # 10
```

闭包保存的是绑定关系所在的 cell，不是简单复制一个值。这一点会直接导致 late binding 问题。

## 7. Late Binding：闭包引用的是名字，不是当时的值

经典例子：

```python
funcs = []

for i in range(3):
    def f():
        return i

    funcs.append(f)

print([fn() for fn in funcs])  # [2, 2, 2]
```

肤浅说法是：“Python 闭包有坑。”

深入理解是：

**闭包中的名字在函数调用时解析；这些函数共享同一个外层名字 `i`，循环结束后 `i` 绑定到 `2`。**

也就是说，三个 `f` 不是分别记住了 `0`、`1`、`2`。它们都引用同一个名字 `i`。

常见修复方式是用默认参数捕获当前对象：

```python
funcs = []

for i in range(3):
    def f(i=i):
        return i

    funcs.append(f)

print([fn() for fn in funcs])  # [0, 1, 2]
```

这里 `i=i` 的含义是：函数定义时计算默认参数，把当前 `i` 绑定的对象保存到函数对象的默认参数里。之后函数内部的参数名 `i` 是局部名字，不再查找外层循环变量。

也可以用工厂函数创建新的作用域：

```python
def make_func(i):
    def f():
        return i

    return f

funcs = [make_func(i) for i in range(3)]
print([fn() for fn in funcs])  # [0, 1, 2]
```

每次调用 `make_func` 都创建一个新的局部作用域，因此每个闭包持有不同的 `i` cell。

## 8. 循环不会创建新作用域

在 Python 中，`for`、`while`、`if` 不创建新的函数作用域：

```python
for i in range(3):
    x = i

print(i)  # 2
print(x)  # 2
```

这和 C++、Rust 的块作用域不同。Python 的基本作用域边界主要是：

- 模块
- 函数
- 类
- 推导式的内部作用域

`if` 也一样：

```python
if True:
    value = 42

print(value)  # 42
```

这不是例外，而是 Python 的作用域不是由任意花括号或缩进块决定，而是由特定语法结构决定。

## 9. 推导式有自己的作用域

Python 3 中，列表推导式、集合推导式、字典推导式和生成器表达式都有自己的内部作用域。

```python
i = 100
xs = [i for i in range(3)]

print(xs)  # [0, 1, 2]
print(i)   # 100
```

推导式内部的 `i` 不会泄漏到外层。

但推导式也可能遇到闭包 late binding：

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])  # [2, 2, 2]
```

推导式有自己的作用域，但其中的多个 lambda 仍然共享推导式作用域里的同一个 `i`。

修复方式仍然是捕获当前值：

```python
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])  # [0, 1, 2]
```

## 10. 类作用域有自己的特殊性

类定义体执行时会创建类命名空间：

```python
class User:
    species = "human"

    def name(self):
        return "Alice"
```

类体中的名字最终会成为类对象的属性：

```python
print(User.species)  # human
print(User.name)     # function object
```

但是类作用域和函数闭包不完全一样。方法体内部不会自动把类体名字当作 enclosing 作用域：

```python
class C:
    x = 10

    def f(self):
        return x

C().f()
```

这会找不到 `x`，因为方法 `f` 是函数对象，调用时它的 LEGB 中没有类体作用域作为普通 enclosing scope。应该写：

```python
class C:
    x = 10

    def f(self):
        return self.x
```

或者：

```python
class C:
    x = 10

    def f(self):
        return C.x
```

类体更像是“创建类对象时执行的一段代码”，它产生类命名空间；方法运行时则是普通函数调用。

## 11. `locals()` 与 `globals()`

`globals()` 返回当前模块全局命名空间的字典：

```python
x = 1
print(globals()["x"])  # 1
```

`locals()` 返回当前局部命名空间的映射：

```python
def f():
    x = 1
    print(locals())

f()  # {'x': 1}
```

不要把修改 `locals()` 当成可靠的局部变量修改方式：

```python
def f():
    locals()["x"] = 1
    print(x)
```

这不应该作为正常代码使用。局部变量通常由解释器优化管理，`locals()` 更多用于调试和元编程观察。

## 12. 名字遮蔽

内层名字可以遮蔽外层名字：

```python
len = 10
print(len)

len([1, 2, 3])  # TypeError: 'int' object is not callable
```

这里模块全局名字 `len` 遮蔽了内置函数 `len`。LEGB 顺序决定了 Python 先找到全局的 `len`，不会继续去 builtins 找。

恢复方式：

```python
del len
print(len([1, 2, 3]))  # 3
```

工程上应避免用这些名字作为变量名：

- `list`
- `dict`
- `set`
- `str`
- `id`
- `type`
- `sum`
- `max`
- `min`
- `input`
- `file`

不是因为语言禁止，而是因为它们会遮蔽常用内置对象，让代码读起来和运行起来都更脆弱。

## 13. 检查表

遇到名字解析问题，按这个顺序问：

1. 这个名字是在读取，还是在赋值？
2. 如果在函数体内赋值，有没有 `global` 或 `nonlocal`？
3. 这个名字属于 Local、Enclosing、Global 还是 Builtins？
4. 是否发生了名字遮蔽？
5. 闭包引用的是同一个外层名字，还是每次创建了新的作用域？
6. 循环是否被误以为创建了块级作用域？
7. 类体名字是否被误以为能在方法体内直接访问？

最小心智模型：

1. 名字存在于命名空间中。
2. 读取名字按 LEGB 查找。
3. 函数内赋值默认创建局部绑定。
4. `global` 改变赋值目标到模块命名空间。
5. `nonlocal` 改变赋值目标到外层函数作用域。
6. 闭包保存外层绑定，名字通常在调用时解析。
7. 循环和 `if` 不创建普通块级作用域。

理解作用域，就是理解 Python 如何把一个名字连接到一个对象。
