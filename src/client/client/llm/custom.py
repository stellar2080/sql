from .llm_base import LLM_Base
import requests
import json

class Custom(LLM_Base):
    def __init__(self, config):
        super().__init__()
        self.LLM_HOST = config.get('LLM_HOST')
        self.LLM_PORT = config.get('LLM_PORT')
        self.DO_SAMPLE = config.get('DO_SAMPLE')
        self.TEMPERATURE = config.get('TEMPERATURE')
        self.TOP_P = config.get('TOP_P')
        self.MAX_TOKENS = config.get('MAX_TOKENS')

    async def call(self,messages):
        headers = {'Content-Type': 'application/json'}
        data = {
            "messages": messages,
            'DO_SAMPLE': self.DO_SAMPLE,
            'TEMPERATURE': self.TEMPERATURE,
            'TOP_P': self.TOP_P,
            'MAX_TOKENS': self.MAX_TOKENS,
        }
        response = await requests.post(
            url=f'http://{self.LLM_HOST}:{self.LLM_PORT}', 
            headers=headers, 
            data=json.dumps(data)
        )
        return response.json()