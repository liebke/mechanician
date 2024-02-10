from abc import ABC, abstractmethod
from rich.markdown import Markdown
from rich.console import Console 
import logging

logger = logging.getLogger(__name__)

###############################################################################
## STREAM PRINTER
###############################################################################
        

class StreamPrinter(ABC):

    @abstractmethod
    def print(self, text):
        pass



class SimpleStreamPrinter(StreamPrinter):
    
    def print(self, text, end='\n', flush=True):
        print(text, end=end, flush=flush)
        return
  

def print_markdown(console, text):
    console.print(Markdown(text))
    return