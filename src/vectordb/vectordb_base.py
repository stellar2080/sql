from abc import ABC, abstractmethod


class VectorDB_Base(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def add_key(self, embedding_id: str, key: str, **kwargs) -> str:
        pass

    @abstractmethod
    def add_schema(self, embedding_id:str, schema: str, **kwargs) -> str:
        pass

    @abstractmethod
    def add_doc(self, embedding_id:str, document: str, **kwargs) -> str:
        pass

    @abstractmethod
    def add_memory(self, memory: str, **kwargs) -> str:
        pass

    @abstractmethod
    def remove_data(self, id: str, **kwargs) -> bool:
        pass

    @abstractmethod
    def get_related_schema(self, question: str, **kwargs) -> list:
        pass

    @abstractmethod
    def get_related_doc(self, question: str, **kwargs) -> list:
        pass

    @abstractmethod
    def get_related_key(self, question: str, **kwargs) -> list:
        pass