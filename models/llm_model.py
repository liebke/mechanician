
from abc import ABC, abstractmethod


class LLMModel(ABC):

    @abstractmethod
    def __init__(self) -> 'LLMModel':
        pass

    @abstractmethod
    def submit_prompt(self, prompt) -> str:
        pass

    @abstractmethod
    def clean_up(self) -> None:
        pass