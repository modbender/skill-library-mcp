---
name: nano-banana-image-t8
description: 用户要求验证 nano-banana-2（或兼容模型）是否可用，并需要文生图和图生图的真实调用结果。
---


# Nano Banana 生图联调

## 触发条件

用户要求验证 `nano-banana-2`（或兼容模型）是否可用，并需要文生图和图生图的真实调用结果。

## 指令

使用技能自带脚本执行联调（优先）：

- `~/.whaleclaw/workspace/skills/nano-banana-image-t8/scripts/test_nano_banana_2.py`
- 若当前在 WhaleClaw 仓库内，也可用仓库脚本 `scripts/test_nano_banana_2.py`

1. WebChat 场景必须使用“对话参数驱动”，禁止依赖脚本后台交互输入（`input/getpass`）。
2. 必须只使用本技能脚本执行，不允许临时 `file_write` 生成 Python 脚本，不允许手写 `curl` 直连接口。
3. API 基地址固定为 `https://ai.t8star.cn`，禁止改为其它域名（如 `api.nanobanana.ai`）。
4. API Key 来自用户对话消息，执行时通过 `--api-key` 或环境变量传入；脚本会落盘到 `~/.whaleclaw/credentials/nano_banana_api_key.txt`（权限 600）。
5. 下次若用户未提供 Key，可直接使用已保存 Key；若用户提供新 Key，覆盖保存。
6. 模式来自用户对话：`文生图` / `图生图` / `都测试`。
7. 文生图只取用户提示词（`--prompt`）。
8. 图生图取用户提示词 + 用户上传图片路径（`--input-image` 可重复）；按接收顺序编号：第一张=图1，第二张=图2。
9. 输出文件目录默认 `~/.whaleclaw/workspace/nano_banana_test/`（固定用户目录，不依赖当前项目 cwd）。
10. 用户若写了尺寸/比例（例如“4:3”“16:9”“1024x1024”），直接透传到脚本参数，不再重复追问。
11. 当用户只说“我要做文生图/图生图”时，只追问缺失的必要参数，不要给与 ComfyUI、本地部署、OpenAI 方案选择题。
12. 文生图最小必填：提示词（其余如尺寸/模型可用默认值）；图生图最小必填：提示词 + 至少1张图片。
13. 回答风格简短直接，优先执行，不写长篇计划。
14. 当用户要求“先查有没有 API Key”时，只允许检查以下来源：
   - 环境变量 `NANO_BANANA_API_KEY`
   - 保存文件 `~/.whaleclaw/credentials/nano_banana_api_key.txt`
15. Key 检查必须优先调用脚本：`test_nano_banana_2.py --check-key`；禁止扫描其它项目目录或 `.env` 文件。
16. 仅在以下任一条件满足时，才允许提取并保存 `sk-` 开头 Key：
   - 用户显式发送 `/use nano-banana-image-t8`
   - 同一条消息明确包含 `nanobanana`/`nano-banana` 且语义是文生图/图生图
17. 非本技能场景（如用户在处理其它任务时提到 API Key）禁止捕获、禁止保存该 Key。
18. 在不确定是否属于本技能场景时，先追问一句“是否用于 Nano Banana 生图技能？”再决定是否保存。

图生图提示词示例：

- `让图1的女孩站在图2的背景中`

执行命令（优先）：

```bash
NANO_BANANA_API_KEY='<你的key>' ./python/bin/python3.12 scripts/test_nano_banana_2.py --model 'nano-banana-2' --edit-model 'nano-banana-2'
```

强制文生图模板（WebChat）：

```bash
./python/bin/python3.12 ~/.whaleclaw/workspace/skills/nano-banana-image-t8/scripts/test_nano_banana_2.py \
  --mode text \
  --api-key '<从用户消息提取的key或留空走已保存key>' \
  --prompt '<用户提示词>' \
  --aspect-ratio '<用户比例，如4:3；未提供则auto>' \
  --out-dir '~/.whaleclaw/workspace/nano_banana_test'
```

技能目录脚本示例（跨机器仅装 SKILL 也可用）：

```bash
NANO_BANANA_API_KEY='<你的key>' ./python/bin/python3.12 ~/.whaleclaw/workspace/skills/nano-banana-image-t8/scripts/test_nano_banana_2.py --model 'nano-banana-2' --edit-model 'nano-banana-2'
```

图生图多图示例：

```bash
NANO_BANANA_API_KEY='<你的key>' ./python/bin/python3.12 scripts/test_nano_banana_2.py \
  --mode edit \
  --edit-model 'nano-banana-2-2k' \
  --prompt '让图1的女孩站在图2的背景中' \
  --input-image '/path/girl.png' \
  --input-image '/path/scene.png' \
  --aspect-ratio 'auto'
```

可选参数：

- `--base-url`：默认 `https://ai.t8star.cn`
- `--size`：直接指定像素，如 `1024x1024`
- `--aspect-ratio`：比例模式，如 `auto`、`4:3`、`16:9`（当 `--size` 为空时生效）
- `--mode`：`text` / `edit` / `both`
- `--prompt`：提示词（WebChat 必传，来自对话框）
- `--input-image`：图生图输入图，可重复传多次
- `--out-dir`：默认 `~/.whaleclaw/workspace/nano_banana_test`

关于 2K：优先通过模型名控制，例如 `nano-banana-2-2k`，比例参数不一定自动映射到 2K 像素。

若失败，优先返回结构化错误：HTTP 状态码、请求 URL、响应体。
若缺少 Key/提示词/图片，不要执行脚本后台交互，直接在对话里向用户要参数后重试。

## 工具

- bash
- file_read

## 示例

用户：帮我测一下 nano-banana-2 的文生图和图生图。
助手：执行测试脚本并返回两张输出图片路径与接口响应结果。
