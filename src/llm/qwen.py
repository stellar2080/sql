import random

from langchain_core.prompts import ChatPromptTemplate

from .llm_base import LLM_Base
from langchain_community.chat_models.tongyi import ChatTongyi

class Qwen(LLM_Base):
  def __init__(self, config):
    super().__init__()
    self.model = ChatTongyi(model = config['model'])

  def system_message(self, message: str):
    return 'system', message

  def user_message(self, message: str):
    return 'user', message

  def assistant_message(self, message: str):
    return 'assistant', message

  def submit_message(self, message: list, **kwargs):
    response = self.model.invoke(message)
    print(response)
    answer=response.content
    return answer