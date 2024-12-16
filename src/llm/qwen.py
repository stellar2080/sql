import os
import random

from .llm_base import LLM_Base
from dashscope import Generation

from ..utils.const import TEMPERATURE, MAX_TOKENS
from ..utils.utils import info


class Qwen(LLM_Base):
  def __init__(self, config):
    super().__init__()
    self.model = config['model']
    self.api_key = os.environ.get('DASHSCOPE_API_KEY')

  def call(self, messages, tools=None, **kwargs):
    response = Generation.call(
      model=self.model,
      api_key=self.api_key,
      messages=messages,
      temperature=TEMPERATURE,
      seed=random.randint(1,10000),
      result_format='message',
      max_tokens=MAX_TOKENS,
      tools=tools,
    )
    return response