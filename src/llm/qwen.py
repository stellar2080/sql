import random

from .llm_base import LLM_Base
from dashscope import Generation

class Qwen(LLM_Base):
  def __init__(self, config):
    super().__init__(config)
    self.model=config['model']
    self.api_key=config['api_key']

  def system_message(self, message: str):
    return {'role':'system','content':message}

  def user_message(self, message: str):
    return {'role':'user','content':message}

  def assistant_message(self, message: str):
    return {'role':'assistant','content':message}

  def submit_message(self, message, **kwargs):
    response = Generation.call(
      model=self.model,
      api_key=self.api_key,
      messages=message,
      temperature=0.7,
      top_p=0.8,
      seed=random.randint(1,10000),
      result_format='message',
      max_tokens=8192
    )
    print(response)
    answer=response.output.choices[0].message.content
    return answer