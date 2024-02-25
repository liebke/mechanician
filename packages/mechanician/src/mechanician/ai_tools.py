from abc import ABC, abstractmethod
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

class AITools(ABC):

    def get_tool_instructions(self):
        return []

    def get_ai_instructions(self):
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