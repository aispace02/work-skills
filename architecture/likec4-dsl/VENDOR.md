# likec4-dsl skill 来源与同步说明

- 来源：https://github.com/likec4/likec4 仓库 `skills/likec4-dsl/`（MIT License）
- 上游版本：v1.59.3（commit `f4c030724`，2026-09-17）
- 引入日期：2026-09-18
- 本仓库改动：仅删除 `evals/`（上游内部评测用），SKILL.md 与 `references/` 未修改

## 同步方法

上游更新后从本地 clone（`/home/hxf0223/work/ai/likec4`，先 `git pull`）重新覆盖本目录（保留本文件）：

```bash
rm -rf .agents/skills/likec4-dsl/SKILL.md .agents/skills/likec4-dsl/references
cp -r /home/hxf0223/work/ai/likec4/skills/likec4-dsl .agents/skills/
rm -rf .agents/skills/likec4-dsl/evals
```

注意：CLI 通过 `npx likec4@<版本>` 固定版本使用（见 `notes/arch/README.md`），升级 skill 时同步升级文档中的固定版本号。
