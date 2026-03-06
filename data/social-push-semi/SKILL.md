---
name: social-push-semi
description: 小红书半自动发布脚手架：自动生成文案、自动抽封面图、产出发布包；最后由人工确认发布。
---

# social-push-semi

## 安装后首句指引（强制）
- 当用户发送：`开始小红书流程`
- 必须先回复完整提问模板（最终定稿版），再进入执行。

## 能力
- 输入视频/主题/关键词
- 自动生成 3 版文案（稳妥/干货/故事）
- 自动从视频抽取封面图
- 生成 `publish-pack`（标题、正文、话题、封面、素材路径）
- **不会自动点击发布**（半自动）

## 快速使用
### Step1 生成发布包
```bash
bash ~/.openclaw/workspace/skills/social-push-semi/scripts/run.sh \
  --video /绝对路径/xxx.mp4 \
  --topic "你的主题" \
  --keywords "关键词1,关键词2" \
  --out ~/.openclaw/workspace/output/social-push
```

### Step2 接上 CDP，自动填充到待发布页
```bash
bash ~/.openclaw/workspace/skills/social-push-semi/scripts/fill_preview_cdp.sh \
  --pack ~/.openclaw/workspace/output/social-push/publish-pack.json
```

### One-shot（一条命令跑完，视频）
```bash
bash ~/.openclaw/workspace/skills/social-push-semi/scripts/one_shot.sh \
  --video /绝对路径/xxx.mp4 \
  --topic "你的主题" \
  --keywords "自动化,AI效率,内容创作"
```

### One-shot（主题自动生图文，豆包API）
```bash
bash ~/.openclaw/workspace/skills/social-push-semi/scripts/topic_auto_api.sh \
  --topic "openclaw自动发文" \
  --tone A \
  --audience "学生" \
  --count 3 \
  --realistic 不要 \
  --image-desc "自习室+笔记本电脑，科技感蓝色霓虹，右侧留标题空白"
```

生成结果：
- `draft.md`：3版文案草稿
- `cover.jpg`：封面
- `publish-pack.json`：发布参数
- `checklist.md`：发布前人工检查单

## 为什么是半自动
流程会停在“待发布”前，发布按钮需人工确认点击，降低风控与误发风险。

## 依赖
- 先执行：`bash ~/.openclaw/workspace/skills/social-push-semi/scripts/setup_vendor_xhs.sh`
- CDP Chrome 已启动（默认 `127.0.0.1:9222`）
- 小红书账号已登录

## 交互提问模板（强制）
当用户说“发小红书/跑小红书流程”时，必须先问一次以下模板（无论视频还是图文）：

```text
发布类型（必填）：视频 / 图文 / 主题自动生成图文

如果是【视频】：
- 视频路径（必填）：
- 主题（必填）：
- 关键词（可选，逗号分隔）：

如果是【图文】：
- 图片路径列表（必填，1~9张，逗号分隔）：
- 主题（必填）：
- 关键词（可选，逗号分隔）：

如果是【主题自动生成图文】：
- 主题（必填）：
- 调性（A干货/B种草/C故事，默认A）：
- 目标人群（必填）：
- 图片数量（默认3）：
- 真人风（要/不要，默认不要）：
- 图片描述（可选）：
  - 填写引导：
    - 场景：你希望画面出现什么（如：宿舍书桌、教室、自习室）
    - 构图：近景/中景/远景，是否要留文案空白区
    - 风格：科技感/极简/扁平插画/海报风
    - 配色：主色（如深蓝+青色）
    - 禁止项：不想出现的元素（如真人脸、Logo、水印）

通用：
- 文案风格（A稳妥/B干货/C故事，默认A）：
- 账号（可空）：
- CDP端口（默认9222）：
- 自动预填到待发布页（要/不要，默认要）：
```

> 说明：该模板是对外可复用的 Skill 入口协议，避免遗漏参数。
