
from abc import ABC, abstractmethod


class ModelAPI(ABC):

    @abstractmethod
    def __init__(self, instructions, tool_schemas, function_handler) -> 'ModelAPI':
        pass

    @abstractmethod
    def submit_prompt(self, prompt) -> str:
        pass

    @abstractmethod
    def clean_up(self) -> None:
        pass