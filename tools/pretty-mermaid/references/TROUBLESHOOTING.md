# Mermaid 常见错误排查与避坑指南 (Troubleshooting)

整理自 `anymermaid` 的实战沉淀与避坑经验。

## 1. 语法常见陷阱

| 现象 / 报错 | 常见诱因 | 解决方案 |
| :--- | :--- | :--- |
| **解析错误 (Parse error)** | 节点 ID 含有空格、横杠或未加引号的特殊符号 | 节点 ID 必须保持连贯（如 `userLogin` 或 `user_login`），显示文本放在括号内：`userLogin["用户登录 (User Login)"]` |
| **标签括号引起语法混乱** | 标签文字中包含 `()`、`[]`、`{}` | 必须用英文双引号包裹整个标签文字：`A["Node with (Parentheses)"]` |
| **Markdown 管道符 `|` 冲突** | 在表格内或带有 `|` 的文字破坏了结构 | 类图、ER 图属性关系中避免裸写 `|`，使用引号或代码块隔离 |
| **时序图箭头歧义** | 混淆实线与虚线返回箭头 | 实线同步调用使用 `->>`，虚线异步/返回使用 `-->>`，双向使用 `<->>` |
| **流程图方向缺失** | 仅写 `flowchart` 未指定方向 | 第一行必须指定方向：`flowchart TD` (上下) 或 `flowchart LR` (左右) |

## 2. 官方 CLI (mmdc) 环境排错（备用路径）

若使用官方 `mmdc` (`@mermaid-js/mermaid-cli`) 渲染额外 20 种复杂图表时遇到问题：

### Puppeteer 沙箱权限报错 (Linux / Docker / CI / WSL)
- **报错信息**: `Failed to launch the browser process` / `No usable sandbox`
- **解决方案**: 创建 `puppeteer-config.json`：
  ```json
  {
    "args": ["--no-sandbox", "--disable-setuid-sandbox"]
  }
  ```
  执行时带上：`mmdc -p puppeteer-config.json -i diagram.mmd -o diagram.svg`

### Linux / Docker 下中文字体乱码
- **原因**: 容器/无头环境缺少中文字体库
- **解决方案**:
  ```bash
  sudo apt-get install -y fonts-wqy-zenhei fonts-liberation
  ```

### Windows PowerShell "脚本被禁止执行"
- **原因**: PowerShell ExecutionPolicy 策略限制
- **解决方案**:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```

## 3. Pretty Mermaid 优势总结
使用本技能内置的 `scripts/render.mjs`（基于 `beautiful-mermaid`）可以完全绕过上述第 2 节的 Puppeteer 沙箱、Chromium 下载与字体问题，非常适合 Linux / SSH / CI 等服务器端无头环境直接生成 SVG / PNG。
