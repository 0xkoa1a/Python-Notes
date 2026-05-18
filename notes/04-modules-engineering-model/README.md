# 模块、导入与工程模型

这一层的目标是理解 Python 项目如何从文件变成可运行的模块图。

后续笔记建议覆盖：

1. 模块对象
2. `sys.path`
3. `sys.modules`
4. 包与 `__init__.py`
5. 绝对导入与相对导入
6. `python file.py` 与 `python -m package.module`
7. 循环导入
8. 项目结构
9. 测试、配置、日志与 CLI

核心信念：import 不是文本粘贴，而是模块对象的创建、缓存和名字绑定。
