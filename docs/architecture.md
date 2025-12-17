# NL-Find 项目架构

## 系统架构图

```txt
┌─────────────────────────────────────────────────────────────┐
│                      用户界面层                              │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   CLI (Typer)       │    │   GUI (PyQt6)               │ │
│  │   - 命令行交互      │    │   - 文件管理器风格           │ │
│  │   - 批处理模式      │    │   - 可视化搜索结果           │ │
│  └──────────┬──────────┘    └──────────────┬──────────────┘ │
└─────────────┼──────────────────────────────┼────────────────┘
              │                              │
              ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      核心引擎层                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                  SearchEngine                           ││
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ││
│  │  │  LLMParser    │→│CommandGenerator│→│SearchExecutor │ ││
│  │  │  自然语言解析  │ │  命令生成     │ │  搜索执行     │ ││
│  │  └───────────────┘ └───────────────┘ └───────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
              │                              │
              ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      基础设施层                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │
│  │   LLM Provider  │ │   File System   │ │   Config      │ │
│  │   OpenAI/Ollama │ │   OS API        │ │   Settings    │ │
│  └─────────────────┘ └─────────────────┘ └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 目录结构

```txt
d:/code/find/
├── src/
│   ├── core/                 # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── models.py         # 数据模型 (Pydantic)
│   │   ├── llm_parser.py     # LLM 自然语言解析
│   │   ├── command_gen.py    # 搜索命令生成
│   │   ├── executor.py       # 搜索执行
│   │   └── exceptions.py     # 自定义异常
│   │
│   ├── cli/                  # 命令行界面
│   │   ├── __init__.py
│   │   └── app.py            # Typer CLI 入口
│   │
│   ├── gui/                  # 图形界面
│   │   ├── __init__.py
│   │   ├── app.py            # PyQt6 应用入口
│   │   ├── main_window.py    # 主窗口
│   │   ├── widgets/          # UI 组件
│   │   │   ├── search_bar.py
│   │   │   ├── file_list.py
│   │   │   ├── dir_tree.py
│   │   │   └── preview.py
│   │   └── styles/           # QSS 样式
│   │       └── dark.qss
│   │
│   └── config/               # 配置管理
│       ├── __init__.py
│       └── settings.py       # Pydantic Settings
│
├── tests/                    # 测试
│   ├── test_parser.py
│   ├── test_executor.py
│   └── conftest.py
│
├── docs/                     # 文档
│   ├── plan.md
│   ├── code_style.md
│   └── architecture.md
│
├── config.example.yaml       # 配置示例
├── pyproject.toml            # 项目配置
├── requirements.txt          # 依赖
└── README.md
```

---

## 核心模块说明

### 1. LLMParser

**职责**: 将自然语言转换为结构化查询

```python
class LLMParser:
    def parse(self, query: str) -> SearchQuery:
        """
        输入: "找出最近一周修改的大于 10MB 的 PDF"
        输出: SearchQuery(
            extensions=[".pdf"],
            min_size=10*1024*1024,
            modified_after=datetime.now() - timedelta(days=7)
        )
        """
```

### 2. CommandGenerator

**职责**: 将 SearchQuery 转换为可执行的搜索参数

```python
class CommandGenerator:
    def generate(self, query: SearchQuery) -> SearchParams:
        """将结构化查询转换为具体的搜索参数"""
```

### 3. SearchExecutor

**职责**: 执行文件系统搜索

```python
class SearchExecutor:
    def execute(self, params: SearchParams) -> list[FileInfo]:
        """遍历文件系统，返回匹配的文件列表"""
```

---

## 数据流

```txt
用户输入 "找出最近修改的 Python 文件"
          │
          ▼
    ┌───────────┐
    │ LLMParser │  调用 LLM API
    └─────┬─────┘
          │
          ▼
    SearchQuery(extensions=[".py"], modified_after=...)
          │
          ▼
    ┌─────────────────┐
    │ CommandGenerator │
    └────────┬────────┘
          │
          ▼
    SearchParams(glob="**/*.py", filters=[...])
          │
          ▼
    ┌────────────────┐
    │ SearchExecutor │  遍历文件系统
    └───────┬────────┘
          │
          ▼
    list[FileInfo]  返回给 CLI/GUI 显示
```

---

## GUI 组件架构

```txt
MainWindow
├── SearchBar          # 搜索输入
├── HSplitter
│   ├── DirectoryTree  # 左侧目录树
│   └── VSplitter
│       ├── FileList   # 文件列表（表格/图标视图）
│       └── Preview    # 预览面板（可选）
└── StatusBar          # 状态信息
```

---

## 扩展点

| 扩展点 | 说明 |
|--------|------|
| LLM Provider | 可添加新的 LLM 提供商 |
| Search Backend | 可集成 Everything、fd 等工具 |
| File Preview | 可添加新的文件类型预览器 |
| Export Format | 可添加新的结果导出格式 |
