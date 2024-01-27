
from openai import OpenAI
from rich.console import Console
from dandyhare.apis.model_api import ModelAPI
from dandyhare.apis.tool_handler import ToolHandler
from dandyhare.util import print_markdown
import time
import os


class OpenAIAssistant(ModelAPI):

    ###############################################################################
    ## INIT_MODEL
    ###############################################################################

    def __init__(self, instructions, tool_schemas, tool_handler: 'ToolHandler'):
        self.model = {}
        self.model["ASSISTANT_ID"] = os.getenv("ASSISTANT_ID")
        self.model["CREATE_NEW_ASSISTANT"] = os.getenv("CREATE_NEW_ASSISTANT") # False
        self.model["DELETE_ASSISTANT_ON_EXIT"] = os.getenv("DELETE_ASSISTANT_ON_EXIT") # False
        self.model["MODEL_NAME"] = os.getenv("MODEL_NAME") # "gpt-4-1106-preview"
        self.model["tool_schemas"] = tool_schemas
        self.tool_handler = tool_handler
        self.client = OpenAI()
        self.model["client"] = self.client
        self.model["instructions"] = instructions

        self.console = Console()

        print_markdown(self.console, f"* ASSISTANT_ID: {self.model['ASSISTANT_ID']}")
        print_markdown(self.console, f"* CREATE_NEW_ASSISTANT: {self.model['CREATE_NEW_ASSISTANT']}")
        print_markdown(self.console, f"* DELETE_ASSISTANT_ON_EXIT: {self.model['DELETE_ASSISTANT_ON_EXIT']}")
        print_markdown(self.console, f"* MODEL_NAME: {self.model['MODEL_NAME']}")

        if self.model["CREATE_NEW_ASSISTANT"] == "True":
            # Create an assistant with the OpenAI client
            print_markdown(self.console, "## Creating a new assistant...")
            self.model["assistant"] = self.client.beta.assistants.create(
                instructions=self.model["instructions"],
                model=self.model["MODEL_NAME"],
                tools=self.model["tool_schemas"]
                )
        else:
            print_markdown(self.console, "## Retrieving existing assistant...")
            self.model["assistant"] = self.client.beta.assistants.retrieve(self.model["ASSISTANT_ID"])

        self.model["thread"] = self.client.beta.threads.create()


    ###############################################################################
    ## SUBMIT_PROMPT
    ###############################################################################

    def submit_prompt(self, prompt):
        client = self.model["client"]
        assistant = self.model["assistant"]
        thread = self.model["thread"]
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
                    tool_outputs.append(self.tool_handler.call_function(function_name, call_id, args))

                # Submit the outputs of the tools to the current run
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run.status == 'pending':
                print("PENDING...")
                time.sleep(0.5)  # wait for 1 seconds before the next check

            elif run.status == 'failed':
                print_markdown(self.console, "# RUN FAILED")
                print_markdown(self.console, f"* Code: {run.last_error.code}")
                print_markdown(self.console, f"* Message: {run.last_error.message}")
                break

        # Retrieve and print the last message
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        # Convert messages to a list
        messages_list = list(messages)
        return messages_list[0].content[0].text.value


    ###############################################################################
    ## CLEAN UP
    ###############################################################################

    def clean_up(self):
        client = self.model["client"]
        client.beta.threads.delete(self.model["thread"].id)
        if self.model["DELETE_ASSISTANT_ON_EXIT"] == "True":
            client.beta.assistants.delete(self.model["assistant"].id)