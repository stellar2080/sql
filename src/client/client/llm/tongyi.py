import os

from .llm_base import LLM_Base
from dashscope import Generation

class Tongyi(LLM_Base):
    def __init__(self, config):
        super().__init__()
        self.model = config['model']
        self.api_key = os.environ.get('DASHSCOPE_API_KEY')
        self.TEMPERATURE = config.get('TEMPERATURE')
        self.TOP_K = config.get('TOP_K')
        self.TOP_P = config.get('TOP_P')
        self.MAX_TOKENS = config.get('MAX_TOKENS')

    def call(self, messages):
        response = Generation.call(
            model=self.model,
            api_key=self.api_key,
            messages=messages,
            result_format='message',
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
            top_k=self.TOP_K,
            top_p=self.TOP_P
        )
        print(response)
        return response