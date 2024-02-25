from abc import ABC, abstractmethod
import json
import logging
from typing import List
import os

logger = logging.getLogger(__name__)

class AITools(ABC):

    def get_tool_instructions(self):
        if hasattr(self, "tool_instructions"):
            return self.tool_instructions
        
        if hasattr(self, "instruction_set_directory"):
            instruction_set_directory = self.instruction_set_directory
        else:
            directory_name = 'instructions'
            instruction_set_directory = os.path.join(os.getcwd(), directory_name)


        if hasattr(self, "tool_instruction_file_name"):
            tool_instruction_path = os.path.join(instruction_set_directory, self.tool_instruction_file_name)
        else:
            tool_instruction_path = os.path.join(instruction_set_directory, "tool_instructions.json")
        
        if os.path.exists(tool_instruction_path):
            with open(tool_instruction_path, 'r') as file:
                logger.info(f"Loading Tool Instructions from {tool_instruction_path}")
                tool_instructions = json.loads(file.read())
            return tool_instructions
        else:
            return []


    def get_ai_instructions(self):
        if hasattr(self, "ai_instructions"):
            return self.ai_instructions
        
        if hasattr(self, "instruction_set_directory"):
            instruction_set_directory = self.instruction_set_directory
        else:
            directory_name = 'instructions'
            instruction_set_directory = os.path.join(os.getcwd(), directory_name)

        if hasattr(self, "ai_instruction_file_name"):
            ai_instruction_path = os.path.join(instruction_set_directory, self.ai_instruction_file_name)
        else:
            ai_instruction_path = os.path.join(instruction_set_directory, "ai_instructions.md")

        if os.path.exists(ai_instruction_path):
            with open(ai_instruction_path, 'r') as file:
                logger.info(f"Loading AI Instructions from {ai_instruction_path}")
                ai_instructions = file.read()
            return ai_instructions
        else:
            return ""


    def call_function(self, function_name, call_id, args):
        # get method by name if it exists
        if hasattr(self, function_name):
            meth = getattr(self, function_name)
            # check that method exists
            if meth:
                if args is None:
                    # call method without args
                    resp = meth(args)
                    if resp is not None:
                        return resp
                elif args.strip():
                    # call method with args
                    resp = meth(json.loads(args))
                    if resp is not None:
                        return resp
                else:
                    resp = meth(args)
                    if resp is not None:
                        return resp
        else:
            logger.info(f"Unknown Function: {function_name}")
            return f"Unknown Function: {function_name}"
            

class AIToolKit(AITools):

    def __init__(self, tools: List[AITools]):
        self.tools = tools

    def call_function(self, function_name, call_id, args):
        # iterate over all tools and find the tool with the function
        for tool in self.tools:
            if hasattr(tool, function_name):
                return tool.call_function(function_name, call_id, args)
            

    def get_ai_instructions(self):
        ai_instructions = ""
        for tool in self.tools:
            ai_instructions += f"\n\n{tool.get_ai_instructions()}"
        return ai_instructions
    

    def get_tool_instructions(self):
        tool_instructions = []
        for tool in self.tools:
            tool_instructions += tool.get_tool_instructions()
        return tool_instructions