
from abc import abstractmethod
from dandyhare.apis.model_api import ModelAPI
from dandyhare.ux.stream_printer import StreamPrinter
from dandyhare.apis.tool_handler import ToolHandler

class StreamingModelAPI(ModelAPI):

    @abstractmethod
    def __init__(self, instructions, tool_schemas, 
                 function_handler : ToolHandler, 
                 stream_printer : 'StreamPrinter') -> 'ModelAPI':
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