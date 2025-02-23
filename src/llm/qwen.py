import os
import random

from .llm_base import LLM_Base
from dashscope import Generation

from ..utils.const import TEMPERATURE, MAX_LENGTH, TOP_K, TOP_P


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
      result_format='message',
      max_tokens=MAX_LENGTH,
      temperature=TEMPERATURE,
      top_k=TOP_K,
      top_p=TOP_P
    )
    print(response)
    return response