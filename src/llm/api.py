from .llm_base import LLM_Base
from src.utils.const import LLM_HOST,LLM_PORT
import requests
import json

class Api(LLM_Base):
    def __init__(self, config):
        super().__init__()

    def call(self,messages):
        headers = {'Content-Type': 'application/json'}
        data = {"prompt": messages}
        response = requests.post(url=f'http://{LLM_HOST}:{LLM_PORT}', headers=headers, data=json.dumps(data))
        return response.json()['response']