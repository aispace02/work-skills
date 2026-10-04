# OpenAI Codex Desktop (Astra & Sol) 系统提示词深度评估与解构报告

## 一、文件来源与真实身份

- **来源仓库**：`elder-plinius/CL4R1T4S`（著名 AI 越狱与提示词逆向研究者 Pliny the Liberator 的公开情报库）。
- **文件定位**：
  - `GPT-6-Sol_Prompts.txt`（约 480 行）：Codex Desktop Agent 的基线指令版本（代号 Sol），包含核心人设、反 AI 腔调规范、自主执行策略、协作通道定义与令牌预算管理。
  - `GPT-6-Astra_Prompts.md`（1145+ 行）：Codex Desktop Agent 的完整进化版本（代号 Astra），在 Sol 的基础上大幅增强了**三阶段交互式规划模式（Plan Mode）**、**Guardian V2 安全分类器**、**计算机/浏览器使用确认准则**、**多 Agent 层次协同架构**与细粒度权限管控。
- **关于 "GPT-6" 的说明**：文中的 "GPT-6" 是内部开发代号/安全沙盒标记，其核心指令集是针对下一代长上下文、强工具调用能力 Coding Agent 设计的高密度工业级系统提示词。

---

## 二、核心价值研判（哪些极其宝贵）

这两个文件不是普通的问答提示词，而是顶级 AI 实验室经海量工程踩坑后沉淀的 **Agent 工程规范与人机交互协议**。其核心价值可拆解为四大维度：

### 1. 消除“AI 伪智与套话”（Anti-AI-Slop）的语言控制术（⭐ 极高价值）
这是撰写**高质量技术文档与专业教程**最值得全盘吸收的部分：
- **明令禁止的陈词滥调（AI Slop Words）**：
  - 严禁空洞词汇：`delve`（深入钻研）、`foster`（培养）、`leverage`（利用）、`it's worth noting`（值得注意的是）、`importantly`（重要的是）、`genuinely`、`Bottom Line:`。
  - 严禁机械化自问自答：`Question? Answer.`。
  - 严禁虚空对比套话：`This isn't about X. It's about Y.`（这不是关于 X，而是关于 Y）。
- **严禁无意义的对称防御修辞（Contrastive Framing）**：
  - 禁止主动抛出用户根本没问的反方论点（例如“我们将使用 A，而不是糟糕的 B”）。
- **段落连贯散文（Connected Prose）优于过度列表化**：
  - 严禁将所有内容碎片化为密密麻麻的嵌套无序列表；每个段落聚焦一个明确中心点，以连贯清晰的散文承载逻辑。
- **结论先行（Outcome-First）**：
  - 先给结果与影响，再展开推导与证据，杜绝按 AI 自身内部思考流水账罗列过程。

### 2. “探索优先于提问”与“决策完备的规划”（Explore First & Decision-Complete）（⭐ 极高价值）
这是解决 AI 写代码时“频繁问废话”或“自作主张写出不可运行代码”的根本法则：
- **区分两类未知（Two Kinds of Unknowns）**：
  1. **环境可探知事实（Discoverable Facts）**：编译参数、已有数据结构、项目依赖、API 签名、配置文件等。**铁律：探索优先，严禁向用户提问**。必须通过只读探索命令（rg, 查看文件）探明。
  2. **用户意图与工程权衡（Preferences & Tradeoffs）**：吞吐量 vs 延迟、同步 vs 异步、兼容性策略等。**及早提问，且必须给出 2~4 个互斥选项并附带推荐默认值**。
- **决策完备的计划（Decision-Complete Plan）**：
  - 交付给用户审阅的计划必须是“完全确定的”，执行者无需再进行二次架构猜测；若用户未指定细节，由 Agent 基于推荐假设推进并明确记录假设。

### 3. 行动偏好与自治闭环（Bias Towards Action）（⭐ 高价值）
- 用户只要表达了诉求（如 "can you...", "I want to...", "help me..."），就将其视作**执行指令**，而非简单回复“我可以做”然后停下来等命令。
- 在授权范围内的可逆操作（只读、单元测试、独立工作区修改），必须一直推进到**产生具体、可审阅的成果**后再请用户确认。

### 4. 守护安全与风险分级矩阵（Guardian Policy）（⭐ 中高价值）
- 区分低风险（本地只读、幂等构建、单文件临时修改）与高风险（凭证嗅探、宽泛破坏性命令 `rm -rf` 未做目标检查、生产分支强制推送、凭据外传）。

---

## 三、局限性与适配挑战

1. **专有工具生态耦合**：
   - 原文深度依赖 OpenAI Codex 沙盒的内置函数：`functions.request_user_input_async`、`functions.exec`、`clock.sleep`、`notes` 检查点工具。在通用场景（如 Claude Desktop、Cursor、Antigravity、Open WebUI、本地 Shell）中需要泛化为标准协议。
2. **本地模型上下文与算力约束（关键针对 Jetson Orin AGX）**：
   - Astra 完整提示词多达 1100 多行（数千 Token）。如果原封不动塞给部署在 Jetson Orin AGX 上的 `Qwen2.5/3-27B` 等本地模型：
     - 会显著拖慢首字延迟（TTFT）。
     - 会严重稀释中等尺寸本地模型的指令遵循注意力（Attention Dilution）。
   - **应对策略**：将庞大的 Guardian 审查和浏览器策略剥离，只保留**高密度、高确定性**的核心规则，分场景定制。
