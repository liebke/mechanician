
from openai import OpenAI
from rich.console import Console
from mechanician.ai_connectors import AIConnector
from mechanician.ai_tools import AITools
import time
import os
import json
import logging

logger = logging.getLogger(__name__)

class OpenAIAssistantsConnector(AIConnector):

    DEFAULT_MODEL_NAME="gpt-4-1106-preview"

    ###############################################################################
    ## INIT_MODEL
    ###############################################################################

    def __init__(self, 
                 model_name=None,
                 api_key=None,
                 assistant_id=None,
                 create_new_assistant=None,
                 delete_assistant_on_exit=None):

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OpenAI API Key is required")
        
        self.model_name = model_name or os.getenv("OPENAI_MODEL_NAME") or self.DEFAULT_MODEL_NAME
        if self.model_name is None:
            raise ValueError("OpenAI Model Name is required")
        
        self.assistant_id = assistant_id or os.getenv("ASSISTANT_ID")
        self.CREATE_NEW_ASSISTANT = create_new_assistant or os.getenv("CREATE_NEW_ASSISTANT", "False") # False
        if self.CREATE_NEW_ASSISTANT == "False" and self.assistant_id is not None:
            raise ValueError("ASSISTANT_ID is required if CREATE_NEW_ASSISTANT is False")
        
        self.STREAMING = False
        self.assistant = None
        self.thread = None
        self.DELETE_ASSISTANT_ON_EXIT = delete_assistant_on_exit or os.getenv("DELETE_ASSISTANT_ON_EXIT", "False") # False
        self.client = OpenAI(api_key=api_key)
        self.tool_instructions = None
        self.ai_instructions = None
        self.tools = None
        self.messages = []


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

        
    ###############################################################################
    ## CONNECT
    ###############################################################################

    def _connect(self):

        self.console = Console()
        logger.info(f"* ASSISTANT_ID: {self.assistant_id}")
        logger.info(f"* CREATE_NEW_ASSISTANT: {self.CREATE_NEW_ASSISTANT}")
        logger.info(f"* DELETE_ASSISTANT_ON_EXIT: {self.DELETE_ASSISTANT_ON_EXIT}")
        logger.info(f"* MODEL_NAME: {self.model_name}")

        if self.CREATE_NEW_ASSISTANT == "True":
            # Create an assistant with the OpenAI client
            logger.info("## Creating a new assistant...")
            self.assistant = self.client.beta.assistants.create(
                name="Mechanician Assistant",
                instructions=self.ai_instructions,
                model=self.model_name,
                tools=self.tool_instructions
                )
        else:
            logger.info("## Retrieving existing assistant...")
            self.assistant = self.client.beta.assistants.retrieve(self.assistant_id)

        self.thread = self.client.beta.threads.create()
        return self.assistant


    ###############################################################################
    ## SUBMIT_PROMPT
    ###############################################################################

    def submit_prompt(self, prompt):
        client = self.client
        assistant = self.assistant
        if assistant is None:
            assistant = self._connect()
            
        thread = self.thread
        # Create a new message with user input
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=prompt
        )

        # Create a new run
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        # Wait for the run status to be 'completed'
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            if run.status == 'completed':
                break

            elif run.status == 'requires_action':
                # The following block of code is responsible for sending requests to an external program
                # and submitting the outputs of the tools used in the program.

                # Get the list of tool calls required by the current run
                tool_calls = run.required_action.submit_tool_outputs.tool_calls

                # Initialize an empty list to store the outputs of the tools
                tool_outputs = []

                # Iterate over each tool call
                for tool_call in tool_calls:
                    call_id = tool_call.id 
                    function_name = tool_call.function.name
                    args = tool_call.function.arguments

                    # Call the function with the extracted name, ID, and arguments,
                    # and append the output to the tool_outputs list
                    logger.info(f"Applying tool: {function_name}...")
                    resp = self.tools.call_function(function_name, call_id, args)
                    if resp is not None:
                        resp_str = json.dumps(resp)
                    else:
                        resp_str = ""
                    
                    tool_outputs.append({"tool_call_id": call_id,
                                            "output": resp_str})
                    
                # Submit the outputs of the tools to the current run
                if tool_outputs:
                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

            elif run.status == 'pending':
                logger.info("PENDING...")
                time.sleep(0.5)  # wait for 1 seconds before the next check

            elif run.status == 'failed':
                logger.error("# RUN FAILED")
                logger.error(f"* Code: {run.last_error.code}")
                logger.error(f"* Message: {run.last_error.message}")
                break

        # Retrieve and print the last message
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Convert messages to a list
        messages_list = list(messages)
        return messages_list[0].content[0].text.value


    ###############################################################################
    ## GET_MESSAGE_HISTORY
    ###############################################################################
    def get_message_history(self):
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        messages_list = list(messages)
        return messages_list


    ###############################################################################
    ## CLEAN UP
    ###############################################################################

    def clean_up(self):
        client = self.client
        client.beta.threads.delete(self.thread.id)
        if self.DELETE_ASSISTANT_ON_EXIT == "True":
            client.beta.assistants.delete(self.assistant.id)