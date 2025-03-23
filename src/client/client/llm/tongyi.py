import os

from .llm_base import LLM_Base
from openai import AsyncOpenAI

class Tongyi(LLM_Base):
    def __init__(self, config):
        super().__init__()
        self.model = config['model']
        self.api_key = config.get('api_key')
        self.TEMPERATURE = config.get('TEMPERATURE')
        self.TOP_P = config.get('TOP_P')
        self.MAX_TOKENS = config.get('MAX_TOKENS')
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    async def call(self, messages):
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
            top_p=self.TOP_P
        )
        print(completion)
        return completion