from abc import ABC
from typing import List
import logging
import traceback
import shlex

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)



###############################################################################
## PROMPT TOOLS
###############################################################################
        
class PromptTools(ABC):

    def parse_command_line(self, command_line):
        tokens = shlex.split(command_line)
        if len(tokens) < 2 or tokens[0] != '/call':
            return {"error": f"Invalid /call command: {command_line}"}

        command_name = tokens[1]
        args = tokens[2:]

        # Parse arguments into a dictionary if they are in the form arg=value
        arg_dict = {}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                arg_dict[key] = value
            else:
                arg_dict[arg] = None

        return {"function_name": command_name, "params": arg_dict}


    def call_function(self, function_name:str, params:dict):
        try:            
            if hasattr(self, function_name):
                meth = getattr(self, function_name)
                
                if meth:
                    if params is None:
                        resp = meth()
                        if resp is not None:
                            return resp
                    else:
                        resp = meth(params)
                        if resp is not None:
                            return resp
            else:
                logger.info(f"Unknown Function: {function_name}")
                return f"Unknown Function: {function_name}"
            
        except Exception as e:
            logger.error(f"Error calling function {function_name}: {e}")
            # Return empty prompt so that it's skipped
            prompt = ''
            return prompt
        


class PromptToolKit(PromptTools):

    def __init__(self, tools: List[PromptTools]):
        self.tools = tools

    def call_function(self, function_name:str, args:str):
        # iterate over all tools and find the tool with the function
        for tool in self.tools:
            if hasattr(tool, function_name):
                return tool.call_function(function_name, args)
