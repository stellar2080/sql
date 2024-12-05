from abc import ABC, abstractmethod


class VectorDB_Base(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def add_question_sql(self, question: str, sql: str, **kwargs) -> str:
        pass

    @abstractmethod
    def add_schema(self, embedding_id:str, schema: str, **kwargs) -> str:
        pass

    @abstractmethod
    def add_doc(self, embedding_id:str, document: str, **kwargs) -> str:
        pass

    @abstractmethod
    def remove_training_data(self, id: str, **kwargs) -> bool:
        pass

    @abstractmethod
    def get_related_schema(self, question: str, **kwargs) -> list:
        pass

    @abstractmethod
    def get_related_doc(self, question: str, **kwargs) -> list:
        pass

    @abstractmethod
    def get_related_sql(self, question: str, **kwargs) -> list:
        pass