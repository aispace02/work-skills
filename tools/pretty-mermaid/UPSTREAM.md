# Upstream Repositories & Sync Guide

本技能包融合了以下两个优质开源 Mermaid 技能仓库的能力与资产：

## 1. 核心运行时与美化渲染器 (Pretty-mermaid-skills)

- **仓库地址**: [https://github.com/imxv/Pretty-mermaid-skills](https://github.com/imxv/Pretty-mermaid-skills)
- **协议**: MIT
- **收录 Commit**: `e234ab73c2992f03c36db04fd55ebb90abca9c45` (2026-10-02)
- **主要贡献**:
  - 本地轻量化 Node.js 渲染管线（基于 `beautiful-mermaid`，免 Puppeteer / Chromium 依赖）
  - 15 款专业精美主题（tokyo-night, dracula, nord, solarized 等）
  - SVG、PNG 与终端 ASCII/Unicode 字符画渲染脚本（`scripts/render.mjs`, `batch.mjs` 等）
  - 6 种主流图表（Flowchart, Sequence, State, Class, ER, XY chart）的美化支持

### 更新同步方法：
```bash
git clone https://github.com/imxv/Pretty-mermaid-skills.git /tmp/pretty-mermaid
# 检查 scripts/ 与 package.json 更新
diff -ru scripts/ /tmp/pretty-mermaid/scripts/
```

---

## 2. 全量语法手册与避坑指南 (anymermaid)

- **仓库地址**: [https://github.com/anyforge/anymermaid](https://github.com/anyforge/anymermaid)
- **协议**: Apache-2.0
- **收录 Commit**: `371654d4f83432066e979adebebaa06eadb8330a` (2026-10-02)
- **主要贡献**:
  - 26 种官方图表完整语法参考库（收录于 `references/OFFICIAL_SYNTAX_GUIDE.md`）
  - 8 种时序图箭头歧义规范、类图/ER图管道符冲突避坑
  - CLI 参数优化（`-w 1600 -s 3`）、无头/Linux 沙箱排障知识（收录于 `references/TROUBLESHOOTING.md`）

### 更新同步方法：
```bash
git clone https://github.com/anyforge/anymermaid.git /tmp/anymermaid
# 检查语法手册更新
diff -u references/OFFICIAL_SYNTAX_GUIDE.md /tmp/anymermaid/skills/anymermaid-skill/references/syntax.md
```
