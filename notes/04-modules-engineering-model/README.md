# 模块、导入与工程模型

这一层的目标是理解 Python 项目如何从文件变成可运行的模块图。

后续笔记建议覆盖：

1. [模块对象](module-objects.md)
2. [`sys.path`](sys-path.md)
3. [`sys.modules`](sys-modules.md)
4. [包与 `__init__.py`](packages-and-init.md)
5. [绝对导入与相对导入](absolute-and-relative-imports.md)
6. [`python file.py` 与 `python -m package.module`](script-vs-module-execution.md)
7. [循环导入](circular-imports.md)
8. [项目结构](project-structure.md)
9. [测试、配置、日志与 CLI](tests-config-logging-cli.md)

核心信念：import 不是文本粘贴，而是模块对象的创建、缓存和名字绑定。
