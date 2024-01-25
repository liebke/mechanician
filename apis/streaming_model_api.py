
from abc import abstractmethod
from apis.model_api import ModelAPI


class StreamingModelAPI(ModelAPI):

    @abstractmethod
    def __init__(self) -> 'ModelAPI':
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