# NL-Find 项目任务计划

## 项目概述

**NL-Find** - 基于 LLM 的自然语言文件搜索工具

将自然语言查询转换为文件系统搜索命令，同时提供 CLI 和 GUI 两种交互方式。

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.11+ |
| GUI | PyQt6 |
| CLI | Typer |
| LLM | LangChain + OpenAI/Ollama |
| 配置 | Pydantic Settings |

---

## 开发阶段

### Phase 1: 核心引擎 ✅

- [x] 搭建项目结构
- [x] 实现 LLM 解析器 (`llm_parser.py`)
- [x] 实现搜索执行器 (`executor.py`)
- [x] 编写核心模块单元测试 (20 passed)

### Phase 2: CLI 界面 ✅

- [x] 实现 Typer CLI 应用
- [x] 支持单次查询和直接模式
- [x] 添加参数：路径、输出格式、排序

### Phase 3: GUI 界面 ✅

- [x] 主窗口布局（文件管理器风格）
- [x] 目录树组件
- [x] 文件列表组件（表格视图）
- [x] 搜索栏组件
- [ ] 文件预览面板（可选）

### Phase 4: 完善与打包

- [x] 配置管理系统
- [ ] 集成测试
- [ ] PyInstaller 打包
- [ ] 编写用户文档

---

## 里程碑

| 里程碑 | 目标 | 预计完成 |
|--------|------|----------|
| M1 | CLI 可用 | Phase 2 结束 |
| M2 | GUI 可用 | Phase 3 结束 |
| M3 | 发布 v1.0 | Phase 4 结束 |
