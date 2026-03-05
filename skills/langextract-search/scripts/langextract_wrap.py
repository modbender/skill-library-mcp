"""
LangExtract OpenAI 兼容模型 Provider 封装

支持所有 OpenAI 兼容 API，配置在 conf.json 中指定
"""

import os

try:
    import langextract as lx
    HAS_LANGEXTRACT = True
except ImportError:
    HAS_LANGEXTRACT = False
    lx = None

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


if HAS_LANGEXTRACT and lx:
    @lx.providers.registry.register(
        r'^glm', r'^zhipu', r'^doubao', r'^volcengine', r'^kimi', r'^gpt', r'^claude',
        priority=10
    )
    class OpenAICompatibleModel(lx.inference.BaseLanguageModel):
        """通用 OpenAI 兼容模型"""
        
        def __init__(self, model_id: str, api_key: str = None, base_url: str = None, **kwargs):
            super().__init__()
            
            self.model_id = model_id
            self.api_key = api_key
            self.base_url = base_url
            
            if not self.model_id:
                raise ValueError("model_id is required")
            if not self.api_key:
                raise ValueError("api_key is required")
            
            if not HAS_OPENAI:
                raise ImportError("openai package is required")
            
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

        def infer(self, batch_prompts, **kwargs):
            api_kwargs = kwargs.copy()
            
            for prompt in batch_prompts:
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[{"role": "user", "content": prompt}],
                    **api_kwargs
                )
                output = response.choices[0].message.content
                yield [lx.inference.ScoredOutput(score=1.0, output=output)]
