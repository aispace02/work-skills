---
name: pretty-mermaid
description: |
  使用 Mermaid 语法创建或渲染高质量、现代美观的图表（支持 SVG、PNG 与终端 ASCII/Unicode 字符画预览）。
  当用户要求创建流程图、时序图、类图、状态图、ER图、XY图、架构图、生命周期图，或提到 "mermaid"、".mmd"、"画图"、"流程图"、"时序图"、"类图"、"架构图" 时使用。
  具备两大能力：
  1. 内置 Node.js 本地极速高颜值渲染器（15 款现代精美主题如 tokyo-night, dracula 等，零浏览器依赖，免 Puppeteer / Chromium）；
  2. 融合 26 种官方 Mermaid 图表语法参考手册（OFFICIAL_SYNTAX_GUIDE.md）与排错避坑指南。
---

# Pretty Mermaid 画图技能

使用 Mermaid 文本语法创建结构化图表，并提供美化与渲染能力。优先产出文档友好的矢矢量 **SVG** 或高清 **PNG**，在终端环境下亦支持 **ASCII / Unicode** 字符画即时预览。

## 工作目录约定

本技能根目录记为 `<skill-root>`。在当前技能目录下运行内置脚本（或使用其绝对路径调用）。图表源码 `.mmd` 及输出图像应当保存在用户指定或正在编辑的项目目录（如 `assets/` 目录），不要将渲染器源码拷贝至用户业务代码中。

## 工作流程

1. **识别图表类型与需求**：
   - 根据用户诉求确定最贴切的图表类型。
   - 核心 6 类常用图表（流程图、时序图、状态图、类图、ER 图、XY 柱状/折线图）使用**内置美化渲染器**。
   - 特殊/冷门图表（如 GitGraph、C4 架构图、数据包 Packet、思维导图 Mindmap 等 26 类官方图表）查阅 `references/OFFICIAL_SYNTAX_GUIDE.md`。

2. **查阅语法与避坑**：
   - 常用语法：阅读 `references/DIAGRAM_TYPES.md`。
   - 全量 26 类官方语法：按需检索 `references/OFFICIAL_SYNTAX_GUIDE.md`。
   - 避坑与排错（括号转义、节点命名、箭头语法）：阅读 `references/TROUBLESHOOTING.md`。

3. **编写 `.mmd` 源码**：
   - 将内容保存为规范的 `.mmd` 文件。
   - 保持节点 ID 简明（无特殊字符与空格），文案置于引号标签中，如 `A["User (Client)"]`。

4. **执行渲染**：
   - **推荐主路径（内置免浏览器高颜值渲染）**：
     调用 `<skill-root>/scripts/render.mjs`，搭配预设精美主题（默认推荐 `tokyo-night` 或 `dracula`、浅色推荐 `github-light`）。
   - **扩展路径（冷门图表）**：
     使用 `npx @mermaid-js/mermaid-cli mmdc -i input.mmd -o output.svg -w 1600`。

5. **验证并嵌入文档**：
   - 检查生成文件无误。在 Markdown 讲义/文档中以图片形式引用（例如 `![架构图](assets/arch.svg)`）。

---

## 核心图表类型速查

| 需求场景 | 推荐图表 | 起始关键字 | 推荐渲染器 |
| :--- | :--- | :--- | :--- |
| 业务流程、分支决策、调用流 | 流程图 (Flowchart) | `flowchart TD` 或 `flowchart LR` | 内置美化引擎 |
| 模块/对象交互、时序调用 | 时序图 (Sequence) | `sequenceDiagram` | 内置美化引擎 |
| 生命周期、状态机、RAII 转换 | 状态图 (State) | `stateDiagram-v2` | 内置美化引擎 |
| 类继承结构、接口关系、属性 | 类图 (Class) | `classDiagram` | 内置美化引擎 |
| 实体关系、数据库模型 | ER 图 (ERD) | `erDiagram` | 内置美化引擎 |
| 趋势对比、基准性能数据柱状图 | XY 图表 (XY Chart) | `xychart-beta` | 内置美化引擎 |
| Git 分支历史、合并流 | Git 图 | `gitGraph` | 官方 mmdc |
| 系统全景与容器架构 | C4 架构图 | `C4Context` | 官方 mmdc |
| 网络协议头与数据包 | 数据包图 | `packet-beta` | 官方 mmdc |
| 任务排期与里程碑 | 甘特图 | `gantt` | 官方 mmdc |

---

## 常用命令（从 `<skill-root>` 运行）

### 1. 查看 15 款内置美化主题
```bash
node scripts/themes.mjs
```
内置主题包括：`tokyo-night`、`tokyo-night-storm`、`tokyo-night-light`、`dracula`、`nord`、`nord-light`、`catppuccin-mocha`、`catppuccin-latte`、`github-dark`、`github-light`、`solarized-dark`、`solarized-light`、`zinc-dark`、`zinc-light`、`one-dark`。

### 2. 渲染高质感 SVG（默认推荐）
```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output diagram.svg \
  --theme tokyo-night
```

### 3. 渲染高清 PNG
```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output diagram.png \
  --format png \
  --width 1600 \
  --theme tokyo-night
```

### 4. 终端直接输出字符画预览 (ASCII / Unicode)
```bash
node scripts/render.mjs \
  --input diagram.mmd \
  --output diagram.txt \
  --format ascii \
  --color-mode none
```

### 5. 批量并行渲染整个目录
```bash
node scripts/batch.mjs \
  --input-dir ./diagrams \
  --output-dir ./output \
  --theme dracula
```

---

## 资料参考清单

- `references/DIAGRAM_TYPES.md`: 常用 6 类图表的高级美化选项与语法
- `references/THEMES.md`: 15 款主题色板与自定义配色规范
- `references/OFFICIAL_SYNTAX_GUIDE.md`: 26 类官方图表最全语法知识库（源自 `anymermaid`）
- `references/TROUBLESHOOTING.md`: 语法排障、Puppeteer 沙箱避坑与跨平台指令
- `UPSTREAM.md`: 上游仓库地址与版本同步说明
