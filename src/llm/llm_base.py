from abc import ABC, abstractmethod

class LLM_Base(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def call(self, messages, tools=None, **kwargs):
        pass


