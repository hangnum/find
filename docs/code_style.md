# NL-Find 代码风格规范

## 核心原则

1. **简洁 > 复杂** - 优先选择简单直接的实现
2. **可读 > 简短** - 代码是写给人看的
3. **显式 > 隐式** - 避免魔法方法和隐藏逻辑

---

## Python 规范

### 格式化

- 使用 **Black** 自动格式化（行宽 88）
- 使用 **isort** 排序 imports
- 使用 **Ruff** 进行 lint 检查

```bash
# 一键格式化
black . && isort . && ruff check --fix .
```

### 类型注解

所有公共函数必须有类型注解：

```python
# ✅ Good
def search_files(path: Path, pattern: str) -> list[FileInfo]:
    ...

# ❌ Bad
def search_files(path, pattern):
    ...
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | snake_case | `llm_parser.py` |
| 类 | PascalCase | `SearchExecutor` |
| 函数/变量 | snake_case | `parse_query()` |
| 常量 | UPPER_SNAKE | `MAX_RESULTS` |
| 私有成员 | 单下划线前缀 | `_internal_cache` |

### Imports 顺序

```python
# 1. 标准库
import os
from pathlib import Path

# 2. 第三方库
from pydantic import BaseModel

# 3. 本项目模块
from nl_find.core.models import SearchQuery
```

### 文档字符串

使用 Google 风格：

```python
def parse_query(query: str) -> SearchQuery:
    """将自然语言转换为搜索查询。

    Args:
        query: 用户输入的自然语言查询

    Returns:
        解析后的 SearchQuery 对象

    Raises:
        ParseError: 当 LLM 无法理解查询时
    """
```

---

## 项目规范

### 错误处理

- 使用自定义异常类，定义在 `src/core/exceptions.py`
- 避免裸露的 `except:`
- 在边界处记录日志

```python
# ✅ Good
try:
    result = llm.parse(query)
except LLMConnectionError as e:
    logger.error(f"LLM 连接失败: {e}")
    raise

# ❌ Bad
try:
    result = llm.parse(query)
except:
    pass
```

### 日志

使用 `loguru` 或标准库 `logging`：

```python
from loguru import logger

logger.info("开始搜索: {}", query)
logger.debug("找到 {} 个文件", len(results))
```

### 配置

- 敏感信息（API Key）使用环境变量
- 用户配置使用 `config.yaml`
- 使用 Pydantic Settings 读取配置

---

## 提交规范

使用 Conventional Commits：

```txt
feat: 添加文件预览功能
fix: 修复搜索路径解析错误
docs: 更新 README
refactor: 重构 LLM 解析器
test: 添加搜索执行器测试
```
