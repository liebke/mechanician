
from mechanician.ai_connectors import AIConnector, AIConnectorProvisioner
from mechanician.tools import AITools, AIToolKit, MechanicianTools, MechanicianToolsProvisioner
import json
import os
import logging
import pprint
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class TAGAI():

    ###############################################################################
    ## INIT
    ###############################################################################

    def __init__(self,
                 ai_connector: 'AIConnector',
                 ai_instructions=None, 
                 ai_tool_instructions=None,
                 instruction_set_directory=None,
                 tool_instruction_file_name="ai_tool_instructions.json",
                 ai_instruction_file_name="ai_instructions.md",
                 ai_tools=None, 
                 name="Mechanician AI"):
        self.ai_connector = ai_connector
        self.name = name
        self.RUNNING = False
        self.ai_tools = []
        self.ai_instructions = None
        self.ai_tool_instructions = None
        
        if ai_instructions is not None:
            self.ai_instructions = ai_instructions

        # if tool instructions is a JSON string, then convert to it to list of dictionaries
        if isinstance(ai_tool_instructions, str):
            self.ai_tool_instructions = json.loads(ai_tool_instructions)
        elif isinstance(ai_tool_instructions, list):
            self.ai_tool_instructions = ai_tool_instructions
        else:
            logger.debug(f"ai_tool_instructions is not a string or list: {ai_tool_instructions}")

        if (instruction_set_directory is not None) and (ai_instructions is None):
            self.instruction_set_directory = instruction_set_directory
            self.ai_instruction_file_name = ai_instruction_file_name
            self.load_ai_instructions(instruction_set_directory, ai_instruction_file_name)

        if (instruction_set_directory is not None) and (ai_tool_instructions is None):
            self.instruction_set_directory = instruction_set_directory
            self.tool_instruction_file_name = tool_instruction_file_name
            self.load_ai_tool_instructions(instruction_set_directory, tool_instruction_file_name)

        if ai_tools is not None:
            if isinstance(ai_tools, AITools):
                self.ai_tools = ai_tools
            elif isinstance(ai_tools, list):
                if not ai_tools:
                    self.ai_tools = None
                else:
                    self.ai_tools = AIToolKit(tools=ai_tools)
            else:
                raise ValueError(f"tools must be an instance of AITools or a list of AITools. Received: {ai_tools}")
                    
        self._equip_tools()

    ###############################################################################
    ## LOAD INSTRUCTIONS
    ###############################################################################

    def load_ai_instructions(self, instruction_set_directory, ai_instruction_file_name):
        ai_instruction_path = os.path.join(instruction_set_directory, ai_instruction_file_name)
        if os.path.exists(ai_instruction_path):
            with open(ai_instruction_path, 'r') as file:
                logger.info(f"Loading AI Instructions from {ai_instruction_path}")
                ai_instructions = file.read()
            if self.ai_instructions is None:
                self.ai_instructions = ai_instructions
        else:
            logger.info(f"AI Instruction file not found at {ai_instruction_path}")
            logger.info("AI Instructions will not be loaded from file")


    def load_ai_tool_instructions(self, instruction_set_directory, tool_instruction_file_name):
        tool_instruction_path = os.path.join(instruction_set_directory, tool_instruction_file_name)
        if os.path.exists(tool_instruction_path):
            with open(tool_instruction_path, 'r') as file:
                logger.info(f"Loading Tool Instructions from {tool_instruction_path}")
                ai_tool_instructions = json.loads(file.read())

            if self.ai_tool_instructions is None:
                self.ai_tool_instructions = ai_tool_instructions

        else:
            logger.info(f"Tool Instruction file not found at {tool_instruction_path}")
            logger.info("Tool Instructions will not be loaded from file")


    ###############################################################################
    ## EQUIP TOOLS
    ###############################################################################

    def _equip_tools(self):
        if isinstance(self.ai_tools, AITools):
            if self.ai_instructions is None:
                self.ai_instructions = self.ai_tools.get_ai_instructions()
            else:
                # If ai_instructios has already been set by the user, then append the self-explanatory tool's ai_instructions.
                self.ai_instructions += f"""\n\n{self.ai_tools.get_ai_instructions()}"""

        if isinstance(self.ai_tools, MechanicianTools):
            if self.ai_tool_instructions is None:
                self.ai_tool_instructions = self.ai_tools.get_tool_instructions()
            else:
                # If specific tool_instructios has already been set by the user, then append the self-explanatory tool's ai_tool_instructions.
                self.ai_tool_instructions = self.ai_tool_instructions + self.ai_tools.get_tool_instructions()

        self.ai_connector._instruct(ai_instructions=self.ai_instructions, 
                                    ai_tool_instructions=self.ai_tool_instructions,
                                    tools = self.ai_tools)
        

    ###############################################################################
    # TUNING SESSION TRANSCRIBER FUNCTIONS
    ###############################################################################

    def get_tuning_session(self):
        tuning_session = {}
        tuning_session["ai_tool_instructions"] = self.ai_tool_instructions
        tuning_session["ai_instructions"] = self.ai_instructions
        tuning_session["transcript"] = self.get_message_history()
        tuning_session["test_results"] = None
        return json.dumps(tuning_session, indent=2)


    def save_tuning_session(self, 
                            tuning_session_dir="./tuning_sessions", 
                            file_name="tuning_session.json"):
        if tuning_session_dir is not None:
                os.makedirs(tuning_session_dir, exist_ok=True)
        with open(os.path.join(tuning_session_dir, file_name), 'w') as f:
            json.dump(self.get_tuning_session(), f, indent=2)



    ###############################################################################
    ## SUBMIT_PROMPT
    ###############################################################################

    def submit_prompt(self, prompt, role="user"):
        return self.ai_connector.submit_prompt(prompt, role=role)
    

    ###############################################################################
    ## GET_MESSAGE_HISTORY
    ###############################################################################
    def get_message_history(self):
        return self.ai_connector.get_message_history()
    

    ###############################################################################
    ## STREAMING
    ###############################################################################
    def streaming_connector(self):
        return self.ai_connector.STREAMING


    ###############################################################################
    ## CLEAN UP
    ###############################################################################

    def clean_up(self):
        return self.ai_connector.clean_up()
    

    ###############################################################################
    ## APPEND AI INSTRUCTIONS
    ###############################################################################

    def append_ai_instructions(self, ai_instructions):
        return self.submit_prompt(ai_instructions, role="system")
    



###############################################################################
## TAGAIProvisioner
###############################################################################
 
class TAGAIProvisioner(ABC):
    def __init__(self,
                 ai_connector_provisioner: 'AIConnectorProvisioner',
                 ai_instructions=None, 
                 ai_tool_instructions=None,
                 instruction_set_directory=None,
                 tool_instruction_file_name="ai_tool_instructions.json",
                 ai_instruction_file_name="ai_instructions.md",
                 ai_tools_provisioner=None, 
                 name="Daring Mechanician AI"):
        
        # TAGAI parameters
        self.ai_connector_provisioner = ai_connector_provisioner
        self.name = name
        self.ai_tools_provisioner = ai_tools_provisioner
        self.ai_instructions = ai_instructions
        self.ai_tool_instructions = ai_tool_instructions
        self.instruction_set_directory = instruction_set_directory
        self.tool_instruction_file_name = tool_instruction_file_name
        self.ai_instruction_file_name = ai_instruction_file_name
        
        
    def create_ai_instance(self, context={}) -> TAGAI:
        ai_connector = self.ai_connector_provisioner.create_ai_connector(context=context)
        if self.ai_tools_provisioner is not None:
            if isinstance(self.ai_tools_provisioner, AITools):
                ai_tools = ai_tools
            elif isinstance(self.ai_tools_provisioner, MechanicianToolsProvisioner):
                ai_tools = ai_tools.create_tools(context=context)
            elif isinstance(self.ai_tools_provisioner, list):
                ai_tools_instances = []
                for at in self.ai_tools_provisioner:
                    if isinstance(at, MechanicianToolsProvisioner):
                        ai_tools_instances.append(at.create_tools(context=context))
                    elif isinstance(at, MechanicianTools):
                        ai_tools_instances.append(at)
                    else:
                        raise ValueError(f"tools must be an instance or list of instances of MechanicianTools or MechanicianToolsProvisioner. Received: {ai_tools}")
                    
                ai_tools = AIToolKit(tools=ai_tools_instances)
            else:
                raise ValueError(f"tools must be an instance of AITools or a list of AITools. Received: {ai_tools}")

        ai = TAGAI(ai_connector=ai_connector, 
                   name = self.name,
                   ai_tools = ai_tools,
                   ai_instructions = self.ai_instructions,
                   ai_tool_instructions = self.ai_tool_instructions,
                   instruction_set_directory = self.instruction_set_directory,
                   tool_instruction_file_name = self.tool_instruction_file_name,
                   ai_instruction_file_name = self.ai_instruction_file_name )
        return ai

