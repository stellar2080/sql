class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class AgentTypeException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class LLMTypeException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class DbConnException(Exception):
    def __init__(self, *args, **kwargs):
        pass

class ArgsException(Exception):
    def __init__(self, *args, **kwargs):
        pass