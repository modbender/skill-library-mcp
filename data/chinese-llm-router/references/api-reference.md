# Chinese LLM API Reference

All major Chinese LLM providers support OpenAI-compatible chat/completions API.

## Provider Endpoints (Feb 2026)

### DeepSeek (深度求索)
- Base URL: `https://api.deepseek.com/v1`
- Models: `deepseek-chat` (V3.2), `deepseek-reasoner` (R1)
- Context: 1M tokens (V3.2), 64K (R1)
- Pricing: Input ¥0.5/M, Output ¥2.0/M (cheapest flagship)
- Free tier: ¥10 credits on signup
- Docs: https://api-docs.deepseek.com

### Qwen / 通义千问 (Alibaba)
- Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Models: `qwen3-max`, `qwen3-max-thinking`, `qwen3-coder-plus`, `qwen-turbo-latest`
- Context: 128K (Max), 32K (Turbo)
- Pricing: Input ¥2.0/M, Output ¥6.0/M (Max); ¥0.3/¥0.6 (Turbo)
- Free tier: 1M tokens/month
- Docs: https://help.aliyun.com/zh/model-studio

### GLM (智谱AI)
- Base URL: `https://open.bigmodel.cn/api/paas/v4`
- Models: `glm-5` (NEW! 744B MoE), `glm-4-plus`
- Context: 128K
- Pricing: Input ¥5.0/M, Output ¥5.0/M (GLM-5, may change)
- Note: GLM-5 just launched 2026-02-11, pricing may adjust
- Docs: https://docs.bigmodel.cn

### Kimi (月之暗面/Moonshot AI)
- Base URL: `https://api.moonshot.cn/v1`
- Models: `kimi-k2.5`, `kimi-k2.5-thinking`, `moonshot-v1-128k`
- Context: 128K (K2.5), supports vision
- Pricing: Input ¥2.0/M, Output ¥6.0/M
- Open source: K2.5 weights available on HuggingFace
- Docs: https://platform.moonshot.cn/docs

### Doubao Seed 2.0 (字节豆包)
- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- Models: `doubao-seed-2.0-pro`, `doubao-seed-2.0-lite`, `doubao-seed-2.0-mini`
- Context: 128K (Pro), 32K (Lite/Mini)
- Pricing: Pro ¥0.8/¥2.0, Lite ¥0.3/¥0.6, Mini ¥0.15/¥0.3
- Note: Requires Volcengine endpoint ID, not just model name
- Docs: https://www.volcengine.com/docs/82379

### MiniMax
- Base URL: `https://api.minimax.chat/v1`
- Models: `minimax-m2.5`
- Context: 128K
- Pricing: Input ¥1.0/M, Output ¥3.0/M
- Can run locally (open weights)
- Docs: https://platform.minimaxi.com/document

### Step (阶跃星辰/StepFun)
- Base URL: `https://api.stepfun.com/v1`
- Models: `step-3.5-flash`, `step-2-16k`
- Context: 128K (Flash)
- Pricing: Input ¥0.7/M, Output ¥1.4/M
- Trending #1 on OpenRouter (Feb 2026)
- Docs: https://platform.stepfun.com/docs

### Baichuan (百川)
- Base URL: `https://api.baichuan-ai.com/v1`
- Models: `baichuan4-turbo`
- Context: 128K
- Pricing: Input ¥1.0/M, Output ¥2.0/M
- Docs: https://platform.baichuan-ai.com/docs

### Spark (讯飞星火)
- Base URL: `https://spark-api-open.xf-yun.com/v1`
- Models: `spark-v4.0-ultra`
- Context: 128K
- Pricing: Input ¥2.0/M, Output ¥6.0/M
- Docs: https://www.xfyun.cn/doc/spark

### Hunyuan (腾讯混元)
- Base URL: `https://api.hunyuan.cloud.tencent.com/v1`
- Models: `hunyuan-turbo-s`
- Context: 32K
- Pricing: Input ¥1.5/M, Output ¥5.0/M
- Docs: https://cloud.tencent.com/document/product/1729

## Common API Format

All providers accept:

```bash
curl -X POST <baseUrl>/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <apiKey>" \
  -d '{
    "model": "<model-id>",
    "messages": [{"role": "user", "content": "你好"}],
    "temperature": 0.7,
    "max_tokens": 4096
  }'
```

## Industry Trends (Feb 2026)

- GLM-5 launched 2/11, first Chinese model to rival Opus 4.6 in coding
- Doubao Seed 2.0 launched 2/14, ByteDance's biggest model upgrade
- DeepSeek V3.2 added 1M context window
- Step 3.5 Flash trending globally for speed
- 70%+ of Chinese LLM providers raised API prices (first time since price war)
- Kimi Claw: Moonshot integrated OpenClaw natively into kimi.com
