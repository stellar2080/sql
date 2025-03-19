from .llm_base import LLM_Base
import requests
import json

class Api(LLM_Base):
    def __init__(self, config):
        super().__init__()
        self.LLM_HOST = config.get('LLM_HOST')
        self.LLM_PORT = config.get('LLM_PORT')
        self.DO_SAMPLE = config.get('DO_SAMPLE')
        self.TEMPERATURE = config.get('TEMPERATURE')
        self.TOP_K = config.get('TOP_K')
        self.TOP_P = config.get('TOP_P')
        self.MAX_LENGTH = config.get('MAX_LENGTH')

    def call(self,messages):
        headers = {'Content-Type': 'application/json'}
        data = {
            "messages": messages,
            'DO_SAMPLE': self.DO_SAMPLE,
            'TEMPERATURE': self.TEMPERATURE,
            'TOP_K': self.TOP_K,
            'TOP_P': self.TOP_P,
            'MAX_LENGTH': self.MAX_LENGTH,
        }
        response = requests.post(
            url=f'http://{self.LLM_HOST}:{self.LLM_PORT}', 
            headers=headers, 
            data=json.dumps(data)
        )
        return response.json()