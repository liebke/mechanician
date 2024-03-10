from abc import ABC
from typing import List
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)



###############################################################################
## PROMPT TOOLS
###############################################################################
        
class PromptTools(ABC):

    def call_function(self, function_name:str, args:List[str]):
        try:
            if hasattr(self, function_name):
                meth = getattr(self, function_name)
                
                if meth:
                    if args is None:
                        resp = meth()
                        if resp is not None:
                            return resp
                    else:
                        resp = meth(args)
                        if resp is not None:
                            return resp
            else:
                logger.info(f"Unknown Function: {function_name}")
                return f"Unknown Function: {function_name}"
            
        except Exception as e:
            logger.error(f"Error calling function {function_name}: {e}")
            traceback.print_exc()
            return f"Error calling function {function_name}: {e}"
        


class PromptToolKit(PromptTools):

    def __init__(self, tools: List[PromptTools]):
        self.tools = tools

    def call_function(self, function_name:str, args:List[str]):
        # iterate over all tools and find the tool with the function
        for tool in self.tools:
            if hasattr(tool, function_name):
                return tool.call_function(function_name, args)
