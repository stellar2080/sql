import os
import random

from .llm_base import LLM_Base
from dashscope import Generation

from ..utils.const import TEMPERATURE, MAX_TOKENS


class Qwen(LLM_Base):
  def __init__(self, config):
    super().__init__()
    self.model = config['model']
    self.api_key = os.environ.get('DASHSCOPE_API_KEY')

  def call(self, messages, **kwargs):
    response = Generation.call(
      model=self.model,
      api_key=self.api_key,
      messages=messages,
      temperature=TEMPERATURE,
      result_format='message',
      max_tokens=MAX_TOKENS,
    )
    print(response)
    return response