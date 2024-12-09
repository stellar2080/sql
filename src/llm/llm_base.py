from abc import ABC, abstractmethod

class LLM_Base(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def system_message(self, message: str) -> any:
        pass

    @abstractmethod
    def user_message(self, message: str) -> any:
        pass

    @abstractmethod
    def assistant_message(self, message: str) -> any:
        pass

    @abstractmethod
    def submit_message(self, message, **kwargs) -> str:
        pass


