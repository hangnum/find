# NL-Find Git 规范

## 分支策略

```
main          # 稳定发布版本
├── dev       # 开发分支
│   ├── feat/xxx    # 功能分支
│   ├── fix/xxx     # 修复分支
│   └── refactor/xxx # 重构分支
```

| 分支 | 用途 | 合并目标 |
|------|------|----------|
| `main` | 生产就绪代码 | - |
| `dev` | 开发集成 | `main` |
| `feat/*` | 新功能开发 | `dev` |
| `fix/*` | Bug 修复 | `dev` 或 `main` |
| `refactor/*` | 代码重构 | `dev` |

---

## Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(parser): 支持日期范围查询` |
| `fix` | Bug 修复 | `fix(executor): 修复路径编码问题` |
| `docs` | 文档更新 | `docs: 更新 README` |
| `style` | 代码格式 | `style: 格式化代码` |
| `refactor` | 重构 | `refactor(gui): 拆分主窗口组件` |
| `test` | 测试相关 | `test: 添加解析器单元测试` |
| `chore` | 构建/工具 | `chore: 更新依赖` |
| `perf` | 性能优化 | `perf: 优化大目录扫描` |

### Scope 范围

- `core` - 核心引擎
- `cli` - 命令行界面
- `gui` - 图形界面
- `config` - 配置相关
- `parser` - LLM 解析器
- `executor` - 搜索执行器

### 示例

```bash
# 简单提交
git commit -m "feat(cli): 添加交互式搜索模式"

# 带正文的提交
git commit -m "fix(parser): 修复中文路径解析失败

根本原因是 Path 对象在 Windows 下的编码问题。
使用 pathlib 统一处理路径。

Closes #42"
```

---

## 提交前检查

```bash
# 1. 格式化代码
black . && isort .

# 2. Lint 检查
ruff check .

# 3. 运行测试
pytest

# 4. 提交
git add .
git commit -m "feat: ..."
```

---

## PR 规范

### 标题格式

与 commit 相同：`type(scope): description`

### PR 描述模板

```markdown
## 变更内容
简述本 PR 的主要改动

## 相关 Issue
Closes #xxx

## 测试
- [ ] 单元测试通过
- [ ] 手动测试通过

## 截图（如有 UI 变更）
```

---

## 版本管理

使用语义化版本 [SemVer](https://semver.org/)：

```
MAJOR.MINOR.PATCH
  │     │     └── 修复向后兼容的 bug
  │     └──────── 添加向后兼容的功能
  └────────────── 不兼容的 API 变更
```

**示例**：`1.0.0` → `1.0.1` (bug fix) → `1.1.0` (new feature) → `2.0.0` (breaking change)
