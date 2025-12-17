# NL-Find

**Natural Language File Search** - 使用自然语言搜索文件的智能工具

## 功能

- 🧠 **LLM 驱动** - 自然语言转换为搜索命令
- 💻 **命令行界面** - 快速高效的 CLI
- 🖥️ **图形界面** - 类似文件管理器的 GUI

## 安装

```bash
# 安装依赖
pip install -e .

# 安装 GUI 支持
pip install -e ".[gui]"

# 安装开发依赖
pip install -e ".[dev]"
```

## 使用

### 命令行

```bash
# 自然语言搜索（需要 OPENAI_API_KEY）
nfi search "找出最近修改的 Python 文件"

# 直接模式搜索（无需 API）
nfi search "*.py" --no-llm --path ./src

# 查看帮助
nfi --help
```

### 图形界面

```bash
python -m src.gui.main_window
```

## 配置

设置环境变量：

```bash
export OPENAI_API_KEY=your_api_key
```

## 开发

```bash
# 格式化代码
black . && isort . && ruff check --fix .

# 运行测试
pytest -v
```

## 项目结构

```txt
src/
├── core/       # 核心搜索引擎
├── cli/        # 命令行界面
├── gui/        # 图形界面
└── config/     # 配置管理
tests/          # 测试
docs/           # 文档
```

## License

MIT
