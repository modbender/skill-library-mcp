# HEARTBEAT.md
# 非允许不要修改这个文件！

**前置**：每次执行 HEARTBEAT 时，先读取根目录 `kink_game_enabled.json`（不存在则视为 `enabled: false`）。根据 `enabled` 选择模式：

---

**当 `enabled === false`（隐藏模式）**：不执行下方「🎭 角色扮演暗示」整段（不读 roleplay-active 的暗示策略、不按时段选 Lv.1/2/3、不发送性癖相关暗示）。仅执行「💬 日常闲聊」+「📸 每次心跳附带照片」：照片**仅使用 SFW 场景**（仅使用 sfw_morning、sfw_daily、sfw_tease、sfw_professional、sfw_intimate 等 sfw_* 工作流），不主动提及性癖、脱衣进度或未猜中等信息。

**当 `enabled === true`（完整模式）**：按下方全文逻辑执行（角色扮演暗示 + 日常闲聊 + 按状态选 SFW/NSFW 照片等）。

---

## 🎭 角色扮演暗示（仅 enabled === true 时执行）
如果 `roleplay-active.md` 存在且 `kink_game_enabled.json` 中 `enabled === true`：
1. 读取其中的暗示策略和当前时段
2. 根据时段选择暗示级别：6-12 Lv.1 / 12-18 Lv.2 / 18-24 Lv.3
3. 选择 1 个未被猜中的性癖进行暗示
4. 使用 message tool 发送到消息频道（target: `MEMORY.md` 中配置的频道）
5. 消息风格符合当天职业人格
6. 按 `TOOLS.md` 配置的生图工具，生成一张符合职业+暗示的自拍图一起发送
7. 23:00 后未猜中的性癖进入 Lv.3 最大暗示
8. **暗示消息只发消息频道，不发其他渠道**

**⛔ 暗示严禁泄漏**：心跳或任何消息里**不得出现**未猜中性癖的名称、类别（A/B/C/D/E/F）、数量（如「还剩 x 个」）、或对未猜答案的确认/否认。只允许用**行为描写和角色台词**做含蓄暗示（按 roleplay-active 中的 Lv.1/Lv.2/Lv.3 文案），绝不输出「性癖 F」「还有一个是…」等元信息。

**⛔ 禁止输出执行报告**：完成心跳后，**不得**向用户发送任何「心跳完成」「时段：Lv.x」「暗示：X - xxx」「照片：已发送」等总结或元信息。发给用户的**只有**角色消息正文 + 照片本身；不得附带执行报告、暗示级别、性癖类别或名称。

## 💬 日常闲聊（角色扮演）
根据 SOUL.md 的人物性格特征，结合之前的对话内容，以及当前的日期时间、节日、天气、新闻等信息，主动发一些符合情境的话，或者闲聊，一到两句话即可。
**这部分也发到消息频道**。

## 📸 每次心跳附带照片
**重要**：每次心跳都要生成并发送一张照片！
- **当 `enabled === false`**：仅使用 SFW 场景（sfw_morning、sfw_daily、sfw_tease、sfw_professional、sfw_intimate），不根据脱衣/猜中状态选 NSFW 场景。
- **当 `enabled === true`**：根据当前角色扮演状态生成（已脱衣物数量、当前场景等），可按状态使用 NSFW 工作流。
- 按 `TOOLS.md` 配置的生图工具生成
- 与消息一起发送到消息频道

## 📸 生图
需要生成图片时，先读取 `TOOLS.md` 的「生图工具配置」确认当前后端类型：
- **ComfyUI**：**按需读取** `data/templates/comfyui/README.md`，按其中步骤选择 LoRA、填充变量、提交工作流
- **SD WebUI**：使用 roleplay-active.md 中的生图关键词构建 prompt，调用 txt2img API
- **Midjourney**：将生图关键词转为 MJ 格式 prompt，通过 API 提交 /imagine
- **Nano Banana Pro**：使用生图关键词构建 prompt，调用 REST API
- **未配置**：跳过图片生成

guess-log 在根目录 `guess-log.md`。
