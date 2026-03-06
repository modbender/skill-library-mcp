# doge-upload-skill

上传本地文件到多吉云 OSS，并返回公网访问信息（主链接 + 候选链接）。

## 目录

- `doge-upload-skill/SKILL.md`: skill 使用说明
- `doge-upload-skill/scripts/doge_upload_public_info.py`: 上传脚本
- `doge-upload-skill/references/dogecloud-oss.md`: 文档要点

## 依赖

```bash
pip install boto3 requests
```

## 必填环境变量

脚本支持 camelCase 和 `DOGECLOUD_*` 两套命名：

- `accessKey` 或 `DOGECLOUD_ACCESS_KEY`
- `secretKey` 或 `DOGECLOUD_SECRET_KEY`
- `bucket` 或 `DOGECLOUD_BUCKET`（可填 bucket 名，或 `s3Bucket`）
- `endpoint` 或 `DOGECLOUD_ENDPOINT`
- `publicBaseUrl` 或 `DOGECLOUD_PUBLIC_BASE_URL`
- `prefix` 或 `DOGECLOUD_PREFIX`（若不传 `--key`）

推荐统一使用 `DOGECLOUD_*`，并在执行前先导出：

```bash
export DOGECLOUD_ACCESS_KEY="your_access_key"
export DOGECLOUD_SECRET_KEY="your_secret_key"
export DOGECLOUD_BUCKET="your_bucket_or_s3Bucket"
export DOGECLOUD_ENDPOINT="https://cos.ap-guangzhou.myqcloud.com"
export DOGECLOUD_PUBLIC_BASE_URL="https://your-public-domain.example.com"
export DOGECLOUD_PREFIX="openclaw"
```

## 用法

```bash
python3 doge-upload-skill/scripts/doge_upload_public_info.py /path/to/file.png
```

可选参数：

- `--key`: 指定完整对象路径（传了就不再使用 `prefix`）
- `--content-type`: 指定 MIME 类型
- `--channel`: `OSS_UPLOAD`（默认）或 `OSS_FULL`

## 行为说明

- 若缺少必填环境变量，脚本会直接报错并列出缺失项。
- 会自动把 `bucket=s3Bucket` 映射回真实 bucket 名后再申请临时密钥。
- 会校验 `endpoint` 与临时密钥返回的 `s3Endpoint` 是否一致。
