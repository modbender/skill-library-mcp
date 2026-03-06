---
name: alicloud-storage-oss-ossutil
description: Alibaba Cloud OSS CLI (ossutil 2.0) skill. Install, configure, and operate OSS from the command line based on the official ossutil overview.
---

Category: tool

# OSS（ossutil 2.0）命令行技能

## 目标

- 使用 ossutil 2.0 管理 OSS：上传、下载、同步与资源管理。
- 统一安装、配置、凭证与 Region/Endpoint 的 CLI 流程。

## 快速接入流程

1. 安装 ossutil 2.0。
2. 配置 AK/SK 与默认 Region（`ossutil config` 或配置文件）。
3. 先 `ossutil ls` 列 bucket，再按 bucket 所在 region 列 object。
4. 执行上传/下载/同步或 API 级命令。

## 安装 ossutil 2.0

- 按平台安装步骤见 `references/install.md`。

## 配置 ossutil

- 交互式配置：

```bash
ossutil config
```

- 默认配置文件路径：
  - Linux/macOS：`~/.ossutilconfig`
  - Windows：`C:\Users\issuser\.ossutilconfig`

配置项主要包括：
- `AccessKey ID`
- `AccessKey Secret`
- `Region`（示例默认 `cn-hangzhou`；未确定最合理 Region 时需询问）
- `Endpoint`（可选；未指定时按 Region 自动推导）

## AccessKey 配置提示

建议使用 RAM 用户/角色并遵循最小权限原则，避免在命令行中明文传入 AK。

推荐方式（环境变量）：

```bash
export ALICLOUD_ACCESS_KEY_ID="你的AK"
export ALICLOUD_ACCESS_KEY_SECRET="你的SK"
export ALICLOUD_REGION_ID="cn-beijing"
```

`ALICLOUD_REGION_ID` 可作为默认 Region；未设置时可选择最合理 Region，无法判断则询问用户。

或使用标准共享凭证文件：

`~/.alibabacloud/credentials`

```ini
[default]
type = access_key
access_key_id = 你的AK
access_key_secret = 你的SK
```


## 命令结构（2.0）

- 高级命令示例：`ossutil config`
- API 级命令示例：`ossutil api put-bucket-acl`

## 常用命令示例

```bash
ossutil ls
ossutil ls oss://your-bucket -r --short-format --region cn-shanghai -e https://oss-cn-shanghai.aliyuncs.com
ossutil cp ./local.txt oss://your-bucket/path/local.txt
ossutil cp oss://your-bucket/path/remote.txt ./remote.txt
ossutil sync ./local-dir oss://your-bucket/path/ --delete
```

## 推荐执行流程（先列 bucket，再列对象）

1) 列出所有 bucket

```bash
ossutil ls
```

2) 从输出中拿到目标 bucket 的 region（例如 `oss-cn-shanghai`），转换成 `--region` 所需格式（`cn-shanghai`）

3) 列对象时显式指定 `--region` 与 `-e`（避免跨地域签名/endpoint 错误）

```bash
ossutil ls oss://your-bucket \
  -r --short-format \
  --region cn-shanghai \
  -e https://oss-cn-shanghai.aliyuncs.com
```

4) 对超大 bucket，优先限制输出规模

```bash
ossutil ls oss://your-bucket --limited-num 100
ossutil ls oss://your-bucket/some-prefix/ -r --short-format --region cn-shanghai -e https://oss-cn-shanghai.aliyuncs.com
```

## 常见报错与处理

- `Error: region must be set in sign version 4.`
  - 原因：缺少 region 配置。
  - 处理：在配置文件补充 `region`，或命令行加 `--region cn-xxx`。

- `The bucket you are attempting to access must be addressed using the specified endpoint`
  - 原因：请求 endpoint 与 bucket 实际地域不一致。
  - 处理：改用 bucket 所在地域 endpoint，如 `-e https://oss-cn-hongkong.aliyuncs.com`。

- `Invalid signing region in Authorization header`
  - 原因：签名 region 与 bucket 地域不一致。
  - 处理：同时修正 `--region` 与 `-e`，两者必须与 bucket 所在地域一致。

## 凭证与安全建议

- 优先使用 RAM 用户的 AK 进行访问控制。
- 命令行选项可覆盖配置文件，但直接在命令行传入密钥存在泄露风险。
- 生产环境建议使用配置文件或环境变量方式管理密钥。

## 选择问题（不确定时提问）

1. 你的操作对象是 Bucket 还是 Object？
2. 需要上传/下载/同步，还是权限/生命周期/跨域等管理操作？
3. 目标 Region 与 Endpoint 是什么？
4. 是否在同地域 ECS 上访问 OSS（可考虑内网 Endpoint）？

## 参考

- OSSUTIL 2.0 概述与安装/配置：
  - https://help.aliyun.com/zh/oss/developer-reference/ossutil-overview

- 官方文档来源清单：`references/sources.md`
