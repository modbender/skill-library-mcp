# feishu-app-setup — 飞书开放平台应用自动化配置

> 用 agent-browser 自动完成飞书企业自建应用的创建、权限配置、事件订阅、改名和版本发布。

在飞书开放平台上配置一个 OpenClaw bot 应用需要大量重复的点击操作。这个技能把整个流程自动化了：创建应用、添加机器人能力、批量导入权限、配置事件订阅、修改应用名称、发布版本——全部通过 `agent-browser` 在浏览器中自动完成。

## 前置条件

- 已安装 `agent-browser` 技能
- 已登录飞书开放平台（https://open.feishu.cn）
- OpenClaw Gateway 正在运行（事件订阅需要活跃的 WebSocket 连接）

## 连接浏览器

### 方式一：连接已有浏览器（推荐）

OpenClaw Gateway 运行时通常已启动 Chrome debug 实例。直接连接已登录的浏览器，无需重新登录：

```bash
# 连接到已有 Chrome 实例（已有飞书 session）
agent-browser --cdp-endpoint http://localhost:9223 open "https://open.feishu.cn/app"
```

**优势**：无需扫码登录，直接可用。适合批量操作。

### 方式二：启动新浏览器

```bash
agent-browser --headed open "https://open.feishu.cn/app"
# 用户扫码登录后，后续操作均可自动化
```

## 完整配置流程

```
创建应用 → 添加机器人能力 → 权限导入 → 事件订阅 → 改名（可选）→ 版本发布 → OpenClaw 配置 → 配对审批
```

---

## Step 1: 创建应用

```bash
agent-browser find role button click --name "创建企业自建应用"
sleep 2
```

### 填写表单（React 受控组件）

飞书开放平台使用 React。`agent-browser fill @ref` 通常可以正常工作，但在 fill 失败时需要回退到原生 setter：

```javascript
// React 受控 input 的可靠填写方式
const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
s.call(inputElement, '目标值');
inputElement.dispatchEvent(new Event('input', {bubbles: true}));
```

### 提取凭证

```javascript
// App ID
const m = document.body.innerText.match(/cli_[a-f0-9]+/);
// App Secret — 先点眼睛图标显示
const eyeBtn = document.querySelectorAll('[data-icon="VisibleOutlined"]');
```

**注意**: App Secret 旁边有 3 个图标按钮：复制(CopyOutlined)、显示(VisibleOutlined)、重置(RefreshOutlined)。**千万别点重置**。

## Step 2: 添加机器人能力

```bash
agent-browser find text "添加应用能力" click
sleep 2
agent-browser eval "
  const btns = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === '+ 添加' || b.textContent.trim() === '添加');
  if (btns[0]) btns[0].click();
"
```

## Step 3: 权限批量导入

### 推荐权限集（OpenClaw 所需最小权限）

```json
{
  "scopes": {
    "tenant": [
      "im:message",
      "im:message:send_as_bot",
      "im:message:readonly",
      "im:message.p2p_msg:readonly",
      "im:message.group_at_msg:readonly",
      "im:resource",
      "im:chat.members:bot_access",
      "im:chat.access_event.bot_p2p_chat:read",
      "contact:user.employee_id:readonly",
      "contact:contact.base:readonly",
      "application:application:self_manage",
      "application:application.app_message_stats.overview:readonly",
      "application:bot.menu:write",
      "event:ip_list",
      "aily:file:read",
      "aily:file:write",
      "corehr:file:download"
    ],
    "user": [
      "aily:file:read",
      "aily:file:write",
      "im:chat.access_event.bot_p2p_chat:read"
    ]
  }
}
```

**重要**: `contact:contact.base:readonly` 必须包含，否则 agent 无法读取用户信息。

### 操作步骤

```bash
# 点击"批量导入/导出权限"
agent-browser snapshot -i | grep '批量'
agent-browser click @eXX
sleep 2

# Monaco 编辑器填写：全选 → 粘贴
agent-browser eval "document.querySelector('.monaco-editor textarea').focus()"
agent-browser press Meta+a
sleep 0.3

# 用 ClipboardEvent 粘贴（Monaco 不支持普通 fill）
agent-browser eval "
  const json = JSON.stringify(PERM_JSON, null, 2);
  const ta = document.querySelector('.monaco-editor textarea');
  const dt = new DataTransfer();
  dt.setData('text/plain', json);
  ta.dispatchEvent(new ClipboardEvent('paste', {clipboardData: dt, bubbles: true, cancelable: true}));
"
sleep 1

# 点击"下一步，确认新增权限" → "申请开通"
```

部分权限（如通讯录相关）会弹出"数据范围"确认对话框，需要额外点击"确认"。

## Step 4: 事件订阅（长连接 WebSocket）

### 先决条件：Gateway 必须先连接

飞书有个鸡生蛋的问题：保存长连接订阅方式时，飞书会检查是否已有活跃的 WebSocket 连接。**正确顺序**：

1. 先在 `openclaw.json` 配置应用凭证
2. 重启 Gateway，让它建立 WebSocket 连接
3. 然后再到飞书控制台保存订阅方式

否则会报错：`code: 10068, msg: "应用未建立长连接"`

### 配置订阅方式

```bash
agent-browser open "https://open.feishu.cn/app/$APP_ID/event"
sleep 4
agent-browser eval "document.querySelector('.app-layout__main').scrollTo(0, 500)"
sleep 1

# 点编辑按钮
agent-browser snapshot -i | grep '订阅方式'
agent-browser click @eXX
sleep 1

# 长连接默认选中，直接保存
agent-browser find role button click --name "保存"
sleep 3
```

### 添加事件

```bash
agent-browser snapshot -i | grep '添加事件'
agent-browser click @eXX
sleep 2

# 用搜索框精确查找（避免在分类列表中翻找选错）
agent-browser snapshot -i | grep 'textbox.*nth=1'
agent-browser fill @eXX "im.message.receive_v1"
sleep 2

# 勾选搜索结果
agent-browser snapshot -i | grep 'checkbox'
agent-browser click @eXX
sleep 1

# 确认添加
agent-browser snapshot -i | grep '确认添加'
agent-browser click @eXX
```

## Step 5: 应用改名

应用名称在 **基础信息 → 国际化配置** 中修改：

```bash
agent-browser open "https://open.feishu.cn/app/$APP_ID/baseinfo"
sleep 3

# 滚动到"国际化配置"区域
agent-browser eval "document.querySelector('.app-layout__main').scrollTo(0, 1000)"
sleep 1

# 点击编辑铅笔图标
agent-browser snapshot -i | grep 'EditOutlined\|编辑'
agent-browser click @eXX
sleep 2

# 清除旧名称并填写新名称
agent-browser snapshot -i | grep 'textbox'
agent-browser fill @eXX "新名称"
sleep 1

# 保存
agent-browser find role button click --name "保存"
sleep 2
```

**注意**：改名后必须创建新版本并发布，新名字才会在飞书聊天中生效。

### 批量改名

```bash
APP_IDS=("cli_xxx1" "cli_xxx2" "cli_xxx3")
NAMES=("名字1" "名字2" "名字3")

for i in "${!APP_IDS[@]}"; do
  agent-browser open "https://open.feishu.cn/app/${APP_IDS[$i]}/baseinfo"
  sleep 3
  # 编辑国际化配置 → 填写新名称 → 保存
done
```

## Step 6: 版本发布

```bash
# 点"创建版本"
agent-browser find role button click --name "创建版本"
sleep 3

# 填写更新说明（版本号自动递增）
agent-browser snapshot -i | grep 'textbox'
agent-browser fill @eXX "更新应用配置"

# 保存版本
agent-browser find role button click --name "保存"
sleep 3

# 申请发布
agent-browser find role button click --name "申请线上发布"
sleep 2

# 确认发布
agent-browser eval "
  const btn = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === '确定');
  if (btn) btn.click();
"
sleep 2
```

### 发布注意事项

- 企业自建应用通常**免审核**，提交即上线
- 发布前可能需要确认**数据权限范围**（如"飞书人事"相关权限需设为"全部"）
- 发布成功后状态显示 **"已发布"** + **"当前修改均已发布"**
- 改名 + 发布通常配合进行，流程：**改名 → 保存 → 创建版本 → 发布**

## Step 7: OpenClaw 多账号配置

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "accounts": {
        "main": { "appId": "cli_xxx", "appSecret": "xxx", "name": "主助手" },
        "agent2": { "appId": "cli_yyy", "appSecret": "yyy", "name": "助手2" }
      }
    }
  },
  "bindings": [
    { "agentId": "main", "match": { "channel": "feishu", "accountId": "main" } },
    { "agentId": "agent2", "match": { "channel": "feishu", "accountId": "agent2" } }
  ]
}
```

重启 Gateway 使配置生效：

```bash
launchctl stop ai.openclaw.gateway && sleep 3 && launchctl start ai.openclaw.gateway
```

## Step 8: 配对审批

用户首次给 bot 发消息时，OpenClaw 返回配对请求。每个用户对每个 bot 需要单独配对一次。

```bash
openclaw pairing approve feishu <配对码>
```

## 操作模式：snapshot + ref

所有操作的核心模式：用 `agent-browser snapshot -i` 获取页面元素 ref，用 `grep` 提取，再用 ref 操作。比 JS 选择器更可靠。

```bash
REF=$(agent-browser snapshot -i 2>&1 | grep 'button "保存"' | head -1 | grep -o 'ref=e[0-9]*' | sed 's/ref=//')
if [ -n "$REF" ]; then
  agent-browser click @$REF
fi
```

## 踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| 保存订阅方式报 10068 | Gateway 未连接 | 先配 openclaw.json → 重启 → 再保存 |
| 添加事件选错 | 分类列表太长 | 用搜索框精确搜索 `im.message.receive_v1` |
| React input fill 无效 | 受控组件问题 | 用原生 setter + dispatchEvent |
| Monaco 编辑器无法 fill | 非标准 input | 用 ClipboardEvent paste |
| 权限不足报错 | 缺 `contact:contact.base:readonly` | 加到权限 JSON 中 |
| 权限变更后仍报错 | 需要新版本 | 权限变更后必须发布新版本 |
| 点错 App Secret 重置 | 3 个图标难区分 | 用 `data-icon` 属性区分 |
| snapshot ref 失效 | daemon busy | `sleep 2` 后重试 |
| 新浏览器打不开飞书 | 需要扫码登录 | 用 `--cdp-endpoint` 连接已登录浏览器 |
| 改名后不生效 | 未发布版本 | 改名 → 保存 → 创建版本 → 发布 |
| 发布要求确认数据范围 | 部分权限需选范围 | 如"飞书人事"权限选"全部" |
| agent-browser launch 失败 | 需要 raw mode | 用 `--cdp-endpoint` 连接已有浏览器 |

## 依赖

- `agent-browser` 技能（用于浏览器自动化）
- 飞书企业管理员权限（创建自建应用）
- OpenClaw Gateway（事件订阅需要活跃连接）
