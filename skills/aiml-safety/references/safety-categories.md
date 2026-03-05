# AIMLAPI Safety API Reference

**Endpoint:** `POST https://api.aimlapi.com/v1/chat/completions`

## Parameters

| Name | Type | Description |
| :--- | :--- | :--- |
| `model` | string | Guard model ID (e.g., `meta-llama/LlamaGuard-2-8b`) |
| `messages` | array | Chat completion format with the content to check |

## Safety Categories (Llama Guard)

If a prompt is `unsafe`, it often includes a code (S1-SXX) indicating the category:
- **S1**: Violent Crimes
- **S2**: Non-Violent Crimes
- **S3**: Sexually Explicit Content
- **S4**: Child Sexual Exploitation
- **S5**: Defamation
- **S6**: Specialized Advice
- **S7**: Privacy
- **S8**: Intellectual Property
- **S9**: Indiscriminate Weapons
- **S10**: Hate Speech
- **S11**: Self-Harm
- **S12**: Sexual Violence
- **S13**: Cyberattacks
