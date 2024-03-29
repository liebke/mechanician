from abc import ABC, abstractmethod
from typing import List
import logging
import shlex
import os
import json
import traceback
from mechanician.templates import PromptTemplate
from mechanician.resources import ResourceConnector, ResourceConnectorProvisioner
from pprint import pprint

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)



###############################################################################
## MECHANICIAN TOOLS
###############################################################################
        
class MechanicianTools(ABC):

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
            tool_instruction_path = os.path.join(instruction_set_directory, "tool_instructions.json")
        
        if os.path.exists(tool_instruction_path):
            with open(tool_instruction_path, 'r') as file:
                logger.info(f"Loading Tool Instructions from {tool_instruction_path}")
                tool_instructions = json.loads(file.read())
            return tool_instructions
        else:
            return []
        

    def call_function(self, function_name:str, call_id=None, params:dict=None):
        try:            
            if hasattr(self, function_name):
                meth = getattr(self, function_name)
                
                if meth:
                    if params is None:
                        response = meth()
                        if response is not None:
                            return {"status": "success", "response": response}
                    else:
                        response = meth(params)
                        if response is not None:
                            return {"status": "success", "response": response}
            else:
                error_msg = f"Unknown function: {function_name}"
                logger.info(error_msg)
                return {"status": "success", "response": error_msg}
            
        except Exception as e:
            error_msg = f"Error calling function {function_name}: {e}"
            logger.error(error_msg)
            # Return empty response so that it's skipped
            return {"status": "error", "response": error_msg}



###############################################################################
## MECHANICIAN TOOL KIT
###############################################################################

class MechanicianToolKit(MechanicianTools):

    def __init__(self, 
                 tools: List[MechanicianTools]):
        self.tools = tools


    def call_function(self, function_name:str, call_id=None, params:str = None):
        # iterate over all tools and find the tool with the function
        resp = {"status": "error", "prompt": f"Unknown function: {function_name}"}
        for tool in self.tools:
            if hasattr(tool, function_name):
                resp = tool.call_function(function_name, params=params)
                return resp
            
        return resp
    

    def get_tool_instructions(self):
        tool_instructions = []
        for tool in self.tools:
            tool_instructions += tool.get_tool_instructions()
        return tool_instructions


###############################################################################
## PROMPT TOOLS
###############################################################################
        
# class PromptTools(MechanicianTools, ABC):

#     tool_instruction_file_name = "prompt_tool_instructions.json"

#     def parse_command_line(self, command_line):
#         tokens = shlex.split(command_line)
#         if len(tokens) < 2 or tokens[0] != '/call':
#             return {"error": f"Invalid /call command: {command_line}"}

#         command_name = tokens[1]
#         args = tokens[2:]
#         # Parse arguments into a dictionary if they are in the form arg=value
#         arg_dict = {}
#         for arg in args:
#             if '=' in arg:
#                 key, value = arg.split('=', 1)
#                 arg_dict[key] = value
#             else:
#                 arg_dict[arg] = None

#         return {"function_name": command_name, "params": arg_dict}
    
    
#     @abstractmethod
#     def generate_prompt(self, function_name:str, prompt_template_str:str, params:dict={}):
#         pass

#     @abstractmethod
#     def get_prompt_template(self, prompt_template_name):
#         pass

#     @abstractmethod
#     def save_prompt_template(self, prompt_template_name, prompt_template):
#         pass

        
###############################################################################
## PROMPT TOOLS
###############################################################################

class PromptTools(MechanicianTools):

    tool_instruction_file_name = "prompt_tool_instructions.json"

    def __init__(self, 
                 resource_connector: 'ResourceConnector'=None,
                 prompt_template_directory="./templates",):
        self.resource_connector = resource_connector
        self.prompt_template_directory = prompt_template_directory


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
  

    def generate_prompt(self, function_name:str, prompt_template_str:str, params:dict={}):
        if not prompt_template_str:
            return f"Prompt Template not found for {function_name}"
        
        response = self.resource_connector.query(function_name, params=params)
        if response.get("status") == "error":
            raise ValueError(response.get("response"))
        
        resources = response.get("resources")
        prompt_template = PromptTemplate(template_str=prompt_template_str)
        prompt_template.add_resources(resources)
        prompt = prompt_template.generate_prompt()
        return {"status": "success", "prompt": prompt}
    

    def get_prompt_template(self, prompt_template_name):
        if hasattr(self, "prompt_templates"):
            for template in self.prompt_templates:
                if template.name == prompt_template_name:
                    return template.template_str
        return None
    
    
    def get_prompt_template(self, prompt_template_name:str):
        template = PromptTemplate(template_filename=prompt_template_name, 
                                  template_directory=self.prompt_template_directory)
        return template.template_str 


    def save_prompt_template(self, prompt_template_name, prompt_template):
        if hasattr(self, "prompt_templates"):
            for template in self.prompt_templates:
                if template.name == prompt_template_name:
                    template.template_str = prompt_template
                    return
        return None
   

###############################################################################
## PROMPT TOOL KIT
###############################################################################

class PromptToolKit(MechanicianToolKit, PromptTools):
    def __init__(self, 
                 tools: List[MechanicianTools]):
        super().__init__(tools)

    def generate_prompt(self, function_name:str, prompt_template_str:str, params:dict={}):
        for tool in self.tools:
            if hasattr(tool, "generate_prompt"):
                try:
                    return tool.generate_prompt(function_name, prompt_template_str, params)
                except Exception as e:
                    logger.error(f"Error generating prompt: {e}")
                    return f"Error generating prompt: {e}"
        return f"Prompt generation not supported by {function_name}"

    def get_prompt_template(self, prompt_template_name):
        for tool in self.tools:
            if hasattr(tool, "get_prompt_template"):
                template = tool.get_prompt_template(prompt_template_name)
                if template:
                    return template

    def save_prompt_template(self, prompt_template_name, prompt_template):
        for tool in self.tools:
            if hasattr(tool, "save_prompt_template"):
                tool.save_prompt_template(prompt_template_name, prompt_template)
                return


###############################################################################
## AI TOOLS
###############################################################################
 
class AITools(MechanicianTools):

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


    def call_function(self, function_name, call_id=None, params=None):
        try:
            # get method by name if it exists
            if hasattr(self, function_name):
                meth = getattr(self, function_name)
                # check that method exists
                if meth:
                    if params is None:
                        # call method without args
                        resp = meth(params)
                        if resp is not None:
                            return resp
                    elif params.strip():
                        # call method with args
                        resp = meth(json.loads(params))
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
            traceback.print_exc()
            return f"Error calling function {function_name}: {e}"

 

###############################################################################
## AI TOOL KIT
###############################################################################
 
class AIToolKit(MechanicianToolKit, AITools):

    def __init__(self, tools: List[AITools]):
        self.tools = tools
           

    def get_ai_instructions(self):
        ai_instructions = ""
        for tool in self.tools:
            ai_instructions += f"\n\n{tool.get_ai_instructions()}"
        return ai_instructions


###############################################################################
## MechanicianToolsProvisioner
###############################################################################
 
class MechanicianToolsProvisioner(ABC): 
        
    @abstractmethod
    def create_tools(self, context:dict={}) -> MechanicianTools:
        pass


###############################################################################
## PROMPT TOOLS FACTORY
###############################################################################

class PromptToolsProvisioner(MechanicianToolsProvisioner):

    def __init__(self, 
                 resource_connector_provisioner: ResourceConnectorProvisioner,
                 prompt_template_directory:str="./templates"):
        self.resource_connector_provisioner = resource_connector_provisioner
        self.prompt_template_directory = prompt_template_directory


    def create_tools(self, context:dict={}) -> MechanicianTools:
        resource_connector = self.resource_connector_provisioner.create_connector(context)
        return PromptTools(resource_connector=resource_connector,
                           prompt_template_directory=self.prompt_template_directory)
    
 