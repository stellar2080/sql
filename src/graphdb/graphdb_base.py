from abc import ABC

class GraphDB_Base(ABC):
    def __init__(self, config):
        self.config = config