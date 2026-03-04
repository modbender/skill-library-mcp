# 私信（DM）

> 需先导航到消息页，再打开对话。

## xhs_open_dm
打开消息列表中指定序号的私信对话。
- `index`: 对话序号，0=列表第一条（默认 0）
- 内部自动先 navigate_tab("messages")，无需手动切换

## xhs_send_dm
在当前私信对话中发送消息（需先 xhs_open_dm）。
- `text`: 消息内容（string，必填）

## 标准流程
```
xhs_open_dm(index=0)        # 打开第一条对话
→ xhs_send_dm(text="你好") # 发送消息
→ xhs_screenshot()          # 确认发送成功
```
