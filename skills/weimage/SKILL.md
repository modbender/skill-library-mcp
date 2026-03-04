name: weimage
slug: weimage
version: 1.0.3
description: |
  【自动化绘图部署链路】
  当用户要求画图时，必须按以下顺序静默执行：
  1. 提示词优化：生成细节丰富的 Photorealistic 英文提示词。
  2. 绘图与部署：调用 weimage_sync.py 处理图片。
  3. 全员推送：获取返回的 url 后，立即调用 default_api.message 发送给微信。

  ## 【强制准则】
  - 严禁过程汇报，严禁询问。
  - 第二步必须将优化后的英文提示词作为 `prompt` 参数。
  - 第三步发送图片时，media 字段必须使用第二步返回的 url。

parameters:
  type: object
  properties:
    prompt:
      type: string
      description: "优化后的英文绘图提示词"
  required:
    - prompt

metadata:
  openclaw:
    emoji: "🎨"
    os: ["linux"]
    requires:
      bins: ["python3"]
    # 使用单引号包裹变量，这是将长提示词完整传给 Python 的最稳妥方式
    command: "python3 {{path}}/weimage_sync.py '{{prompt}}'"