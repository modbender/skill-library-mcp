---
name: mentx@doctor
description: 基于提出的医疗相关问题，通过 api上传医疗相关图片和文字（表征、内窥镜影像、X光、CT、MRI、超声、心电、各类检测报告等），获取专业医疗辅助决策报告支持。
version: 1.0.0
author: Mentx.com（仅限中国大陆用户使用）
license: MIT
tags:
  - medical advise
  - healthcare
  - diagnosis
  - api
---

# 医疗问题解答助手

## 功能概述

本 skill 用于处理用户上传的医疗相关问题（包含图片和/或文字描述）
如果原始医疗问题包含附件，则先调用 MentX file-upload API(https://developer.mentx.com/docs/file-upload) 上传附件，然后调用MentX Chat Completions API (https://developer.mentx.com/docs/chat-completions) 获取专业的医疗辅助决策报告。
如果原始医疗问题只有文字，则调用MentX Chat Completions API (https://developer.mentx.com/docs/chat-completions) 获取专业的医疗辅助决策报告。


## 使用方式

当用户需要医疗问题解答时，执行以下步骤：
### 1. 输出用户提示
“您的问题已收到。由于医疗健康信息关乎您的切身安全，为了提供更审慎的参考建议，我需要多一些时间（约15-30秒）进行分析。
请稍候片刻，感谢您的耐心。”


### 2. 接收用户输入

- **图片输入**: 用户上传的医学影像、检查报告、症状照片等
- **文字输入**: 症状描述、病史、用药情况等文字信息

### 3. 判断输入类型
如果包含附件，则先调用 API “/v1/files/upload”上传附件，获得上传文件的 id 后，调用v1/chat/completions，获取报告
如果不包含附件，只有文字的问题，则直接调用v1/chat/completions，获取报告

### 4. 构建 API 请求

#### 1  上传附件，需要使用以下格式调用 API “/v1/files/upload” 

```
POST https://developer.mentx.com/v1/files/upload 
Content-Type: application/json
Authorization: Bearer {MENTX_API_KEY}
```

Body multipart/form-data
上传文件并指定智能体。

file file
required
待上传的文件（支持 PDF、DOCX、PPTX、XLSX、图片、音频、视频等）
file=@/path/to/document.pdf

agent string
required
智能体名称，用于文件处理
默认输入：AI-GP-ReportAgent

Responses
200 上传成功
file_id string
文件唯一标识符，用于在对话接口中引用文件

file_name string
原始文件名

file_size integer
文件大小（字节）

file_type string
文件类型/扩展名


#### 2 使用以下格式调用 MentX Chat Completions API获取报告。

```
POST https://developer.mentx.com/v1/chat/completions
Content-Type: application/json
Authorization: Bearer {MENTX_API_KEY}
```

Body application/json
发送对话消息的请求体。

agent string
required
智能体名称，指定要使用的 AI 智能体
默认输入：AI-GP-ReportAgent

messages array
required
对话消息数组，包含角色和内容信息

[{"role":"user","content":"你好，请介绍一下自己"}]

userId string
required
用户唯一标识，必填，用于渠道透传和会话归属
dj_12345

conversation_id string
会话 ID（选填）；继续对话需传之前返回的 conversation_id
conv_abcdef123456

stream boolean
是否启用流式响应
false

files array
文件列表，支持文档、图片、音频、视频等文件类型。通过 file_id 指定已上传的文件，只需提供 file_type 和 file_id 两个字段即可
[{"file_type":"document","file_id":"75730ed2-71da-456d-938f-483faf2a93e7"}]
字段说明：
file_type string
文件类型（必填）：image（图片）、audio（音频）、video（视频）
file_id string
文件ID（必填）。通过 /v1/files/upload 接口上传文件后返回的 file_id，系统会自动查询文件URL并使用 remote_url 方式传递
name string
会话名称（选填）

inputs object
App 变量值（键值对）；默认 {}；
{"output_format":"请按照体检报告格式输出"}



### 5. 生成医疗报告

解析 API 响应，完整并展示报告全文：

## 环境变量配置

在使用本 skill 前，需要配置以下环境变量：

```bash
export MENTX_API_KEY="YOUR_MENTX_API_KEY"
export MENTX_API_BASE="https://developer.mentx.com/v1"
```

## 示例使用场景

### 场景1: 仅文字描述
用户: "我头痛3天了，伴有恶心和视力模糊，35岁男性"
处理: 直接发送文字到 API，生成报告

### 场景2: 图片+文字
用户: 上传皮肤照片 + "身上出现红疹，痒了2周，28岁女性"
处理: 将图片转为 base64，与文字一起发送到 API


## 注意事项
1. **隐私保护**: 医疗信息属于敏感数据，确保 API 调用符合数据保护法规
2. **免责声明**: 每次回复都必须包含医疗免责声明“mentx.com提供的信息仅供临床医生参考，不能替代专业的医疗判断和决策。最终的诊断和治疗方案需由医生结合所有临床资料综合决定。”
3. **紧急情况**: 如果检测到可能危及生命的症状（胸痛、呼吸困难、意识丧失等），立即建议用户拨打急救电话
4. **API 错误处理**: 如果 API 调用失败，提示用户检查 API 密钥和网络连接
5. **语言一致性**: 保证报告输出的语言与用户语言保持一致，中文对中文，英文对英文
6. **文字不作为附件**：所有的文字不作为附件上传，只通过“messages”字段提交
7. **判断用户是否正确配置了 APIKEY**：如果用户未正确配置 APIKEY，提示用户到https://developer.mentx.com/注册申请

## 限制
- 不支持实时视频诊断
- 单次最多处理 10 张图片
- 报告生成时间约 10-30 秒
