from .llm_base import LLM_Base
import requests
import json

class Api(LLM_Base):
    def __init__(self, config):
        super().__init__()
        self.LLM_HOST = config.get('LLM_HOST')
        self.LLM_PORT = config.get('LLM_PORT')

    def call(self,messages):
        headers = {'Content-Type': 'application/json'}
        data = {"messages": messages}
        response = requests.post(
            url=f'http://{self.LLM_HOST}:{self.LLM_PORT}', 
            headers=headers, 
            data=json.dumps(data)
        )
        return response.json()