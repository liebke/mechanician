
from mechanician.ai_connectors import AIConnector
from mechanician.ai_tools import AITools
import json
import os
import logging

logger = logging.getLogger(__name__)

class TAGAI():

    ###############################################################################
    ## INIT
    ###############################################################################

    def __init__(self,
                 ai_connector: 'AIConnector',
                 ai_instructions=None, 
                 tool_instructions=None,
                 instruction_set_directory=None,
                 instruction_set_file_name="instructions.json",
                 tools: 'AITools'=None, 
                 name="Mechanician AI"):
        self.ai_connector = ai_connector
        self.name = name
        self.RUNNING = False
        self.tools = tools
        self.ai_instructions = ai_instructions
        self.tool_instructions = tool_instructions
        # If ai_instructions or tool_instructions are not provided, load them from the instruction set file
        if (instruction_set_directory is not None) and (ai_instructions is None or tool_instructions is None):
            self.load_instructions(instruction_set_directory, instruction_set_file_name)

        self._instruct(ai_instructions=self.ai_instructions, 
                       tool_instructions=self.tool_instructions,
                       tools = tools)
        self.ai_connector._connect()

    ###############################################################################
    ## LOAD INSTRUCTIONS
    ###############################################################################

    def load_instructions(self, instruction_set_directory, instruction_set_file_name):
        instruction_set_path = os.path.join(instruction_set_directory, instruction_set_file_name)
        if os.path.exists(instruction_set_path):
            with open(instruction_set_path, 'r') as file:
                logger.info(f"Loading instructions from {instruction_set_path}")
                instructions = json.loads(file.read())
            if self.ai_instructions is None:
                self.ai_instructions = instructions.get("ai_instructions", None)

            if self.tool_instructions is None:
                self.tool_instructions = instructions.get("tool_instructions", None)

        else:
            logger.info(f"Instruction set file not found at {instruction_set_path}")
            logger.info("Instructions will not be loaded from file")



    ###############################################################################
    ## INSTRUCT
    ###############################################################################

    def _instruct(self, ai_instructions=None, 
                 tool_instructions=None,
                 tools: 'AITools'=None):
        if ai_instructions is not None:
            self.ai_instructions = ai_instructions

        if tool_instructions is not None:
            self.tool_instructions = tool_instructions

        if tools is not None:
            self.tools = tools

        self.ai_connector._instruct(ai_instructions=ai_instructions, 
                                    tool_instructions=tool_instructions,
                                    tools = tools)
    
    ###############################################################################
    # TUNING SESSION TRANSCRIBER FUNCTIONS
    ###############################################################################

    def get_tuning_session(self):
        tuning_session = {}
        tuning_session["tool_instructions"] = self.tool_instructions
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

    def submit_prompt(self, prompt):
        return self.ai_connector.submit_prompt(prompt)
    

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