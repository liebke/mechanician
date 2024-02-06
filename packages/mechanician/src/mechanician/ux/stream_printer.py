from abc import ABC, abstractmethod
import logging

logger = logging.getLogger('mechanician.ux.stream_printer')
logger.setLevel(level=logging.INFO)

class StreamPrinter(ABC):

    @abstractmethod
    def print(self, text):
        pass



class SimpleStreamPrinter(StreamPrinter):
    
    def print(self, text, end='\n', flush=True):
        print(text, end=end, flush=flush)
        return
  