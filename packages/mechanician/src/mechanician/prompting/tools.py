from abc import ABC
from typing import List
import logging
import shlex
import os
import json

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)



###############################################################################
## PROMPT TOOLS
###############################################################################
        
class PromptTools(ABC):

    def get_tool_instructions(self):
        if hasattr(self, "tool_instructions"):
            return self.tool_instructions
        
        if hasattr(self, "instruction_set_directory"):
            instruction_set_directory = self.instruction_set_directory
        else:
            directory_name = 'src/instructions'
            instruction_set_directory = os.path.join(os.getcwd(), directory_name)


        if hasattr(self, "tool_instruction_file_name"):
            tool_instruction_path = os.path.join(instruction_set_directory, self.tool_instruction_file_name)
        else:
            tool_instruction_path = os.path.join(instruction_set_directory, "prompt_tool_instructions.json")
        
        print(f"tool_instruction_path: {tool_instruction_path}")
        if os.path.exists(tool_instruction_path):
            print(f"Loading Tool Instructions from {tool_instruction_path}")
            with open(tool_instruction_path, 'r') as file:
                logger.info(f"Loading Tool Instructions from {tool_instruction_path}")
                tool_instructions = json.loads(file.read())
            return tool_instructions
        else:
            return []
        

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
                        prompt = meth()
                        if prompt is not None:
                            return {"status": "success", "prompt": prompt}
                    else:
                        prompt = meth(params)
                        if prompt is not None:
                            return {"status": "success", "prompt": prompt}
            else:
                error_msg = f"Unknown function: {function_name}"
                logger.info(error_msg)
                return {"status": "success", "prompt": error_msg}
            
        except Exception as e:
            error_msg = f"Error calling function {function_name}: {e}"
            logger.error(error_msg)
            # Return empty prompt so that it's skipped
            return {"status": "error", "prompt": error_msg}
        


class PromptToolKit(PromptTools):

    def __init__(self, tools: List[PromptTools]):
        self.tools = tools

    def call_function(self, function_name:str, args:str):
        # iterate over all tools and find the tool with the function
        resp = {"status": "error", "prompt": f"Unknown function: {function_name}"}
        for tool in self.tools:
            if hasattr(tool, function_name):
                resp = tool.call_function(function_name, args)
                return resp
            
        return resp