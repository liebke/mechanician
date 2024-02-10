
from abc import ABC, abstractmethod
from mechanician.util import StreamPrinter
from mechanician.ai_tools import AITools
import logging

logger = logging.getLogger(__name__)

class AIConnector(ABC):

    messages = []
    instructions = None
    tool_schemas = None

    @abstractmethod
    def __init__(self, instructions, tool_schemas, 
                 function_handler : 'AITools', name):
        pass

    @abstractmethod
    def submit_prompt(self, prompt) -> str:
        pass

    @abstractmethod
    def clean_up(self) -> None:
        pass

    def get_messages(self):
        return self.messages



class StreamingAIConnector(AIConnector):

    @abstractmethod
    def __init__(self, instructions, tool_schemas, 
                 function_handler : 'AITools', 
                 stream_printer : 'StreamPrinter',
                 name: str):
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