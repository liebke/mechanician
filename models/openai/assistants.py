
from openai import OpenAI
from dotenv import load_dotenv

# Import Markdown and Console from rich library for pretty terminal outputs
# from rich.markdown import Markdown
from rich.console import Console

from models.openai.tools import call_function
from models.openai.tool_schemas import tool_schemas
from util import print_markdown
import time
import os


load_dotenv()
console = Console()


###############################################################################
## INIT_MODEL
###############################################################################

def init_model():
    model = {}
    model["ASSISTANT_ID"] = os.getenv("ASSISTANT_ID")
    model["CREATE_NEW_ASSISTANT"] = os.getenv("CREATE_NEW_ASSISTANT") # False
    model["DELETE_ASSISTANT_ON_EXIT"] = os.getenv("DELETE_ASSISTANT_ON_EXIT") # False
    model["MODEL_NAME"] = os.getenv("MODEL_NAME") # "gpt-4-1106-preview"
    client = OpenAI()
    model["client"] = client


    print_markdown(console, f"* ASSISTANT_ID: {model['ASSISTANT_ID']}")
    print_markdown(console, f"* CREATE_NEW_ASSISTANT: {model['CREATE_NEW_ASSISTANT']}")
    print_markdown(console, f"* DELETE_ASSISTANT_ON_EXIT: {model['DELETE_ASSISTANT_ON_EXIT']}")
    print_markdown(console, f"* MODEL_NAME: {model['MODEL_NAME']}")

    if model["CREATE_NEW_ASSISTANT"] == "True":
        # Open and read the instructions file
        with open("./resources/instructions.md", 'r') as file:
            instructions = file.read()
            # print(f"INSTRUCTIONS:\n {instructions}")

        # Create an assistant with the OpenAI client
        print_markdown(console, "## Creating a new assistant...")
        model["assistant"] = client.beta.assistants.create(
            instructions=instructions,
            model=model["MODEL_NAME"],
            tools=tool_schemas
            )
    else:
        print_markdown(console, "## Retrieving existing assistant...")
        model["assistant"] = client.beta.assistants.retrieve(model["ASSISTANT_ID"])

    model["thread"] = client.beta.threads.create()
    return model


###############################################################################
## SUBMIT_PROMPT
###############################################################################

def submit_prompt(model, prompt):
    client = model["client"]
    assistant = model["assistant"]
    thread = model["thread"]
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
        # instructions="Ask to confirm before calling out to a function tool by showing the parameters of the call before proceeding."
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
            # print("REQUIRES ACTION...")
            # The following block of code is responsible for sending requests to an external program
            # and submitting the outputs of the tools used in the program.

            # Get the list of tool calls required by the current run
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            # Initialize an empty list to store the outputs of the tools
            tool_outputs = []
            # call_ids = []

            # Iterate over each tool call
            for tool_call in tool_calls:
                # print(f"tool_call: {tool_call}")
                call_id = tool_call.id 
                function_name = tool_call.function.name
                args = tool_call.function.arguments

                # Call the function with the extracted name, ID, and arguments,
                # and append the output to the tool_outputs list
                # call_ids.append(call_id)
                tool_outputs.append(call_function(function_name, call_id, args))

            # Submit the outputs of the tools to the current run
            # print(f"tool_outputs: {tool_outputs}")
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        elif run.status == 'pending':
            print("PENDING...")
            time.sleep(0.5)  # wait for 1 seconds before the next check

        elif run.status == 'failed':
            print_markdown(console, "# RUN FAILED")
            print_markdown(console, f"* Code: {run.last_error.code}")
            print_markdown(console, f"* Message: {run.last_error.message}")
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

def clean_up(model):
    client = model["client"]
    client.beta.threads.delete(model["thread"].id)
    if model["DELETE_ASSISTANT_ON_EXIT"] == "True":
        client.beta.assistants.delete(model["assistant"].id)