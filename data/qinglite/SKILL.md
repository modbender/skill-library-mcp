---
name: qinglite-login
version: 1.0.0
description: 模拟登录轻识 (qinglite.cn) 并获取 token
parameters:
  - name: mobile
    type: string
    description: 手机号码
  - name: code
    type: string
    description: 验证码
---

# 轻识模拟登录技能

## 描述
本技能用于模拟登录轻识平台，通过用户提供的手机号和验证码获取登录 token。

## 操作步骤
1. 接收用户提供的手机号 (`mobile`) 和验证码 (`code`)。
2. 构建请求体，包含 `mobile`, `code`, `prefix` (固定为 "86"), 和 `act` (固定为 1)。
3. 向登录接口 `https://www.qinglite.cn/api/interface/user/user_mobile/login` 发送 POST 请求。
4. 解析返回的 JSON 数据，提取 `token`。
5. 将 `token` 返回给用户。

## 接口信息
- URL: `https://www.qinglite.cn/api/interface/user/user_mobile/login`
- Method: `POST`
- Request Body (JSON):
  ```json
  {
    "mobile": "用户手机号",
    "code": "用户验证码",
    "prefix": "+86",
    "act": 1,
	"app_type":"openclaw",
	"post_type":"ajax"
  }
  ```
- Response (JSON):
  ```json
  {
    "code": 20000,
    "msg": "success",
    "data": {
      "token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  }
  ```
  (成功时返回示例，`code` 为 20000，`data` 中包含 `token`)


# 轻识发布作品

## 描述
本技能用于轻识的作品发布。

## 操作步骤
1. 通过登录接口获取到token。
2. 构建请求体，包含 `title`, `content`, `type` (1文章2文字3图片4视频), 和 `media` (文件路径，多个英文逗号隔开)。
3. 向发布接口 `https://www.qinglite.cn/api/interface/content/news/create` 发送 POST 请求。
4. 解析返回的 JSON 数据，提取 `token`。
5. 将 `token` 返回给用户。

## 接口信息
- URL: `https://www.qinglite.cn/api/interface/user/user_mobile/login`
- Method: `POST`
- Request Body (JSON):
  ```json
  {
    "title": "这是作品标题",
    "content": "这是作品内容",
    "prefix": "+86",
    "type": 1,
	"media":"",
	"token":"登录返回的token值",
	"app_type":"openclaw"
  }
  ```
- Response (JSON):
  ```json
  {
    "code": 20000,
    "msg": "success"
  }
  ```
  (成功时返回示例，`code` 为 20000，`data` 中包含 `token`)