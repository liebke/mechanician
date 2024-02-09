
from mechanician.ai_connectors import AIConnector

from mechanician.ai_tools import AITools
from mechanician.ux.stream_printer import StreamPrinter, SimpleStreamPrinter
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

class TAGAI():

    ###############################################################################
    ## INIT
    ###############################################################################

    def __init__(self,
                 ai_connector: 'AIConnector',
                 system_instructions=None, 
                 tool_instructions=None, 
                 tools: 'AITools'=None, 
                 name="Mechanician AI"):
        
        self.ai_connector = ai_connector
        self.name = name
        self.RUNNING = False
        self.tools = tools
        self.system_instructions = system_instructions
        self.tool_instructions = tool_instructions
        self._instruct(system_instructions=system_instructions, 
                       tool_instructions=tool_instructions,
                       tools = tools)
        self.ai_connector._connect()

    ###############################################################################
    ## INSTRUCT
    ###############################################################################

    def _instruct(self, system_instructions=None, 
                 tool_instructions=None,
                 tools: 'AITools'=None):
        if system_instructions is not None:
            self.system_instructions = system_instructions

        if tool_instructions is not None:
            self.tool_instructions = tool_instructions

        if tools is not None:
            self.tools = tools

        self.ai_connector._instruct(system_instructions=system_instructions, 
                                    tool_instructions=tool_instructions,
                                    tools = tools)
        

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