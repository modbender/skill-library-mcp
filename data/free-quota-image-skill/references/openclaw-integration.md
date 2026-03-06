# OpenClaw Integration

Use this skill in OpenClaw by placing the folder in one of these locations:

* `~/.openclaw/skills/free-quota-image-skill`
* `<workspace>/skills/free-quota-image-skill`

Use OpenClaw `skills.entries` env injection to avoid committing secrets:

```JSON
{
  "skills": {
    "entries": {
      "free-quota-image-skill": {
        "enabled": true,
        "env": {
          "T2I_PEINTURE_HF_TOKENS": "hf_xxx,hf_yyy",
          "T2I_PEINTURE_GITEE_TOKENS": "gitee_xxx",
          "T2I_PEINTURE_MODELSCOPE_TOKENS": "ms_xxx",
          "T2I_PEINTURE_A4F_TOKENS": "",
          "T2I_PEINTURE_OPENAI_COMPATIBLE_URL": "https://api.siliconflow.cn/v1",
          "T2I_PEINTURE_OPENAI_COMPATIBLE_TOKENS": "sk_xxx,sk_yyy"
        }
      }
    }
  }
}
```

Notes:

* Start OpenClaw in a new session after editing skill files or settings.
* Keep `.env` local only; prefer OpenClaw env injection in shared deployments.

