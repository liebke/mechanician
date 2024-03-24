from abc import ABC, abstractmethod
import os
import json
import logging
from typing import Any, List
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

###############################################################################
## RESOURCE CONNECTOR TOOLS
###############################################################################
        
class ResourceConnector(ABC):

    def get_instructions(self):
        if hasattr(self, "resource_instructions"):
            return self.instructions
        
        if hasattr(self, "instruction_set_directory"):
            resource_set_directory = self.instruction_set_directory
        else:
            directory_name = 'src/instructions'
            resource_set_directory = os.path.join(os.getcwd(), directory_name)

        if hasattr(self, "resource_instruction_file_name"):
            resource_instruction_path = os.path.join(resource_set_directory, self.resource_instruction_file_name)
        else:
            resource_instruction_path = os.path.join(resource_set_directory, "resource_instructions.json")
        
        print(f"resource_instruction_path: {resource_instruction_path}")
        if os.path.exists(resource_instruction_path):
            print(f"Loading Resource Instructions from {resource_instruction_path}")
            with open(resource_instruction_path, 'r') as file:
                logger.info(f"Loading Resource Instructions from {resource_instruction_path}")
                ai_tool_instructions = json.loads(file.read())
            return ai_tool_instructions
        else:
            return []
    

    @abstractmethod
    def list_resources(self):
        pass
    

    @abstractmethod
    def get_resource(self, params:dict=None):
        pass


    @abstractmethod
    def list_resources(self, params:dict=None):
        pass



###############################################################################
## RESOURCES
###############################################################################

class PromptResource:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data

    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
        else:
            raise AttributeError(f"'PromptResource' object has no attribute '{attr}'")
