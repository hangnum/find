# NL-Find 测试规范

## 测试框架

- **pytest** - 测试运行器
- **pytest-cov** - 覆盖率统计
- **pytest-asyncio** - 异步测试支持

---

## 目录结构

```txt
tests/
├── conftest.py          # 共享 fixtures
├── unit/                # 单元测试
│   ├── test_parser.py
│   ├── test_executor.py
│   └── test_models.py
├── integration/         # 集成测试
│   └── test_search_flow.py
└── fixtures/            # 测试数据
    └── sample_files/
```

---

## 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 测试文件 | `test_<module>.py` | `test_parser.py` |
| 测试函数 | `test_<行为>_<场景>` | `test_parse_returns_query_for_valid_input` |
| Fixtures | 描述性名称 | `sample_directory`, `mock_llm` |

---

## 编写规范

### 基本结构 (AAA 模式)

```python
def test_search_finds_pdf_files():
    # Arrange - 准备
    executor = SearchExecutor()
    params = SearchParams(extensions=[".pdf"])
    
    # Act - 执行
    results = executor.execute(params)
    
    # Assert - 断言
    assert all(r.path.suffix == ".pdf" for r in results)
```

### 使用 Fixtures

```python
# conftest.py
@pytest.fixture
def temp_directory(tmp_path):
    """创建临时测试目录"""
    (tmp_path / "test.pdf").touch()
    (tmp_path / "test.py").touch()
    return tmp_path

# test_executor.py
def test_search_in_directory(temp_directory):
    executor = SearchExecutor()
    results = executor.execute(SearchParams(path=temp_directory))
    assert len(results) == 2
```

### Mock LLM 调用

```python
@pytest.fixture
def mock_llm(mocker):
    """模拟 LLM 响应，避免真实 API 调用"""
    return mocker.patch(
        "src.core.llm_parser.call_llm",
        return_value='{"extensions": [".py"]}'
    )

def test_parser_with_mock(mock_llm):
    parser = LLMParser()
    query = parser.parse("找 Python 文件")
    assert query.extensions == [".py"]
```

---

## 运行命令

```bash
# 运行所有测试
pytest

# 带覆盖率
pytest --cov=src --cov-report=html

# 只运行单元测试
pytest tests/unit/

# 运行特定测试
pytest tests/unit/test_parser.py -v

# 跳过需要 API 的测试
pytest -m "not requires_api"
```

---

## 覆盖率要求

| 模块 | 最低覆盖率 |
|------|------------|
| `src/core/` | 80% |
| `src/cli/` | 70% |
| `src/gui/` | 50% |

---

## 测试标记

```python
@pytest.mark.slow
def test_large_directory_scan():
    """耗时测试"""
    ...

@pytest.mark.requires_api
def test_real_llm_parsing():
    """需要真实 API 的测试"""
    ...
```
