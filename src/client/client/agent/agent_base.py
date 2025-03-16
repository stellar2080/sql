from abc import abstractmethod, ABC

class Agent_Base(ABC):
    @abstractmethod
    def chat(
        self,
        message: dict
    ):
        pass