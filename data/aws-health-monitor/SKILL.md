---
name: aws-health-monitor
description: Monitor AWS Health Dashboard for active incidents and notify via configurable channels (Feishu, Telegram, Slack, Discord, etc.). Activate when user wants to watch AWS service health, set up alerts for AWS outages, or check current AWS regional incidents. Covers global, eu-central-1, ap-northeast-1, and me-central-1 (UAE) regions. Supports HTTP proxy for restricted network environments.
---

# AWS Health Monitor

监控 AWS Health Dashboard 活跃故障，变更时推送通知（支持飞书、Telegram、Slack、Discord 等）。

## 部署路径

- 脚本：`scripts/aws-health-monitor.py`（部署到 workspace/scripts/）
- 忽略配置：`references/aws-health-ignore.example.json`（部署为 workspace/scripts/aws-health-ignore.json）
- 状态文件（运行时自动生成）：`workspace/scripts/.aws-health-state.json`
- 日志：`workspace/logs/aws-health-monitor.log`

## 关键配置（环境变量）

脚本所有关键参数通过环境变量注入，不硬编码：

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `HTTPS_PROXY` / `HTTP_PROXY` | 出口代理 | 不使用代理 |
| `AWS_HEALTH_NOTIFY_CHANNEL` | 通知渠道（feishu/telegram/slack/discord 等） | `feishu` |
| `AWS_HEALTH_NOTIFY_TARGET` | 通知目标（open_id / chat_id / @username 等） | 必填 |
| `AWS_HEALTH_WATCH_REGIONS` | 监控的 region 白名单，逗号分隔 | 空（监控全部） |
| `AWS_HEALTH_WATCH_SERVICES` | 监控的服务名白名单，逗号分隔 | 空（监控全部） |

**示例：只监控法兰克福和东京的 EC2、RDS**
```bash
export AWS_HEALTH_WATCH_REGIONS=eu-central-1,ap-northeast-1
export AWS_HEALTH_WATCH_SERVICES="Amazon EC2,Amazon RDS"
```

## 挂 Cron

```bash
*/5 * * * * export http_proxy=http://<proxy>:<port> https_proxy=http://<proxy>:<port> AWS_HEALTH_NOTIFY_CHANNEL=<channel> AWS_HEALTH_NOTIFY_TARGET=<target>; cd /path/to/workspace && /usr/bin/python3 scripts/aws-health-monitor.py >> logs/aws-health-monitor.log 2>&1
```

## 忽略配置（aws-health-ignore.json）

参考 `references/aws-health-ignore.example.json`，支持两种忽略方式：

```json
{
  "arns": ["arn:aws:health:me-central-1::event/..."],  // 精确忽略单个 issue
  "services": ["Amazon WorkSpaces", "AWS IoT Core"]    // 按服务名模糊忽略
}
```

修改后保存即生效，下次轮询自动跳过。

## 通知触发条件

- 新 issue 出现
- 已知 issue 有最新更新（message 变化）
- issue 从 Dashboard 消失（视为已解决）

## 通知格式示例

```
[新故障] | AWS Health Dashboard

Region：UAE
服务：Multiple services
状态：调查中（Increased Error Rates）
首发：2026-03-01 20:51 CST
更新：2026-03-02 13:59 CST

根因：电源故障、数据中心火灾/物理损坏
We are investigating issues with AWS services in the ME-CENTRAL-1 Region

最新进展：
We are investigating additional connectivity issues and error rates...

https://health.aws.amazon.com/health/status
```

## 根因提炼逻辑

脚本通过正则匹配 event_log 所有消息文本，识别以下根因类型：
电源故障、数据中心物理损坏、网络故障、连通性问题、硬件故障、软件 Bug、配置变更/错误、变更发布问题、容量/资源耗尽、DNS 问题、证书/TLS 问题、存储故障、内存问题、流量异常/DDoS、上游/第三方问题。

匹配到多个时用顿号拼接；未匹配则显示"暂无明确根因"。

## 数据来源

`GET https://health.aws.amazon.com/public/currentevents`（UTF-16 编码 JSON）

旧接口 `https://status.aws.amazon.com/data.json` 已 301 重定向至此。
