from abc import ABC

class VectorDB_Base(ABC):
    def __init__(self, config):
        self.config = config