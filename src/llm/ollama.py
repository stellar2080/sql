import ollama

from .llm_base import LLM_Base

from ..utils.const import TEMPERATURE, MAX_TOKENS


class Ollama(LLM_Base):
  def __init__(self, config):
    super().__init__()
    self.host = config.get('host', 'localhost')
    self.port = config.get('port', 11434)
    self.model = config['model']
    self.client = ollama.Client(host=f"http://{self.host}:{self.port}")

  def call(self, messages, **kwargs):
      response = self.client.chat(
          model=self.model,
          messages=messages,
          options={
              "temperature": TEMPERATURE,
              "num_predict": MAX_TOKENS,
          }
      )
      print(response)
      return response