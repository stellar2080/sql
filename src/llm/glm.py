from zhipuai import ZhipuAI
from .llm_base import LLM_Base

class Glm(LLM_Base):
    def __init__(self, config):
        super().__init__(config)
        self.model = config['model']
        self.api_key = config['api_key']

    def system_message(self, message: str):
        return {'role': 'system', 'content': message}

    def user_message(self, message: str):
        return {'role': 'user', 'content': message}

    def assistant_message(self, message: str):
        return {'role': 'assistant', 'content': message}

    def submit_message(self, message, **kwargs):
        client = ZhipuAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=message,
            temperature=0.2
        )
        # print(response)
        answer = response.choices[0].message.content
        return answer