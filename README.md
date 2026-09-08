# Work Skills

工作过程中收集/自建的 agent skills 仓库,供各项目按需选取(符号链接或拷贝)。

收录自:china-stock-app(A 股监控)、nuo-qian-map-lib(C++/Qt 地图库)、第三方仓库、本机工具。

## 目录与分类

```text
go/            Go 工程技能(评审/并发/错误处理/接口/lint/性能/风格/测试/modern-go)
cpp/           C++/Qt/CMake 技能包(评审/架构/逆向/重构/性能/测试)
frontend/      前端技能(HQChart 行情图表)
trading/       量化交易技能(板块成员搜集)
architecture/  架构文档技能(C4)
writing/       文档与表达技能(中文润色/通俗科普/可视化)
tools/         工具型技能与推荐工具
```

## 技能清单

### Go(`go/`)— 上游:[samber/cc-skills-golang](https://github.com/samber/cc-skills-golang)(2026-09-07 收录)

| Skill | 用途 |
| --- | --- |
| go-code-review | 评审主清单(格式/错误/命名/并发/接口/测试…),含 pre-review.sh |
| go-concurrency | goroutine 生命周期、通道、互斥、原子操作 |
| go-error-handling | 错误策略/wrapping(%w)/错误流 |
| go-interfaces | 接口归消费者、接收者类型 |
| go-linting | golangci-lint 配置与 CI 接入 |
| go-performance | strconv/容量/传值/字符串拼接(热路径) |
| go-style-core | 风格原则(清晰>简洁)、嵌套、裸返回 |
| go-testing | 表驱动/got-want 语序/httptest |
| golang-testing | 深度测试方法论(testify/goleak/fuzz) |
| use-modern-go | Modern Go Guidelines CLI(按 go.mod 版本出新惯用法) |

### C++/Qt(`cpp/`)— 来源:`cpp-qt-codex-skills-pack`(经 nuo-qian-map-lib 项目引入,2026-09-08 收录,上游未注明)

| Skill | 用途 |
| --- | --- |
| cpp-codebase-analysis | 只读代码库侦察 |
| cpp-language-review | 语言惯用法/RAII/类型安全评审 |
| cpp-architecture-review | 架构/依赖/Qt 边界评审 |
| cpp-reverse-engineering | 陌生/遗留项目逆向理解 |
| cmake-architecture-review | target/依赖/构建系统审计 |
| cpp-refactor-review | 重构后回归评审 |
| cpp-performance-review | 证据驱动性能审计 |
| cpp-test-review | 测试架构与覆盖评审 |

`README-pack.md` 为该技能包原始安装说明。

### 前端(`frontend/`)

| Skill | 来源 | 用途 |
| --- | --- | --- |
| hqchart | [jones2000/HQChart](https://github.com/jones2000/HQChart) 官方 skill(Apache-2.0) | K线/分时图数据对接、SetOption 参数、指标编写 |

### 交易(`trading/`)

| Skill | 来源 | 用途 |
| --- | --- | --- |
| board-collector | 自建(china-stock-app) | 搜集 A 股板块成员,东财倒排+网络搜索交叉验证→人工确认入库 |

### 架构(`architecture/`)

| Skill | 来源 | 用途 |
| --- | --- | --- |
| c4-codebase-architecture | [lmammino/c4-codebase-architecture-skill](https://github.com/lmammino/c4-codebase-architecture-skill)(MIT) | 逆向代码库产出 C4 架构文档 |

### 文档与表达(`writing/`)

| Skill | 来源 | 用途 |
| --- | --- | --- |
| notes-humanizer | 未注明(经 china-stock-app 收录) | 中文文档润色/去 AI 味(含 patterns.md 模式库) |
| eli5 | [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community/tree/main/eli5)(Apache-2.0) | /eli5 话题→大图少字 HTML 通俗科普 |
| show-me | [humanlayer/skills](https://github.com/humanlayer/skills/tree/main/plugins/show-me)(MIT) | 伪代码/调用树/组件树/Mermaid 精确可视化 |

### 工具(`tools/`)

| 工具 | 来源 | 用途 |
| --- | --- | --- |
| graphify | 本机 CLI(`~/.local/bin/graphify`,skill 为安装器生成) | 代码库/文档→知识图谱,架构调研/调用链查询(`graphify query`) |
| mermaid-cli(推荐) | `npm i -g @mermaid-js/mermaid-cli` | 渲染各 skill 产出的 Mermaid 图为 PNG/SVG |
| draw.io / excalidraw(推荐) | 桌面版或 [app.diagrams.net](https://app.diagrams.net) | 手工架构图补绘 |

## 安装到项目

```bash
# 符号链接(推荐,随源更新)
ln -s /path/to/work-skills/go/go-code-review <项目>/.zcode/skills/go-code-review
# 或拷贝
cp -r /path/to/work-skills/cpp/cpp-architecture-review <项目>/.agents/skills/
```

注意:`.zcode/skills/`、`.agents/skills/`、`.codex/skills/` 为常见发现路径;含 `references/` 的 skill 必须整体链接/拷贝目录。

## 上游更新检查

定期(建议每月)逐个核对本表"来源"列:

```bash
# 例:检查 go skills 上游
git clone --depth 1 https://github.com/samber/cc-skills-golang /tmp/upstream-go
diff -r /tmp/upstream-go/skills go/   # 视上游目录结构而定
```

已知的更新注意点:

- go/ 系列:上游 samber/cc-skills-golang 持续演进,且本地已按项目惯例做过定制(如 go-testing 与 golang-testing 并存),更新时逐文件 diff 而非覆盖;
- hqchart:随 jones2000/HQChart 大版本更新 references/ 数据格式文档;
- c4/show-me/eli5:上游稳定,低频检查即可;
- cpp/README-pack.md:上游 pack 未注明出处,无法自动跟踪;若原作者发布仓库请回填链接。

## 自建 skill 约定

- `SKILL.md` frontmatter `name` 仅小写字母/数字/连字符;
- 第三方 skill 保留其 LICENSE 文件;自建/来源不明者在本表注明;
- 每个新收录条目更新本 README 对应表格与收录日期。
