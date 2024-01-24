
from abc import ABC, abstractmethod
from models.llm_model import LLMModel


class LLMStreamingModel(LLMModel):

    @abstractmethod
    def __init__(self) -> 'LLMModel':
        pass

    @abstractmethod
    def get_stream(self, prompt):
        pass

    @abstractmethod
    def process_stream(self, stream):
        pass

    @abstractmethod
    def clean_up(self) -> None:
        pass

    def submit_prompt(self, prompt):
        return self.process_stream(self.get_stream(prompt))