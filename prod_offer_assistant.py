# Import necessary libraries
from openai import OpenAI
from dotenv import load_dotenv
from pprint import pprint
import os

# Import custom function call_function from tools module
from tools import call_function

# Import tool_schemas from tool_schemas module
from tool_schemas import tool_schemas
import time

# Import Markdown and Console from rich library for pretty terminal outputs
from rich.markdown import Markdown
from rich.console import Console

# Load environment variables from a .env file
load_dotenv()
# Create a Console object for pretty terminal outputs
console = Console()

# Create an OpenAI client
client = OpenAI()

print('\n\n\n')
markdown = Markdown("""# Product Offer Assistant Proof of Concept""")
console.print(markdown)
markdown = Markdown("""Hello! I'm your virtual assistant designed to help you create new product offers. With my assistance, you can efficiently build product hierarchies, define pricing entities, and establish relationships between products and associated charges or other products. Whether you are crafting bundles, packages, promotions, or any other product-related entities within Hansen Catalog Manager, I'm here to guide you through the process and provide support wherever needed. If you have any tasks in mind, please let me know, and we can get started on creating a new product offer together! 
                     \n\n""")
console.print(markdown)
print('\n\n\n')

# Open and read the instructions file
with open("./resources/instructions.md", 'r') as file:
    instructions = file.read()
    # print(f"INSTRUCTIONS:\n {instructions}")

# Create an assistant with the OpenAI client
assistant = client.beta.assistants.create(
    instructions=instructions,
    model="gpt-4-1106-preview",
    tools=tool_schemas
)

thread = client.beta.threads.create()

# Loop forever, processing user input from the terminal
try:
    while True:
        user_input = input("> ")

        if user_input == '':
            continue

        if user_input.startswith('/slurp'):
            filename = user_input.replace('/slurp ', '', 1)

            # print(f"slurping file: {filename}")
            with open(filename, 'r') as file:
                user_input = file.read()
                print('')
                print("------------------")
                print("SLURPED FILE")
                pprint(user_input)
                print("------------------")
                print('')


        # Create a new message with user input
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=user_input
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
                    tool_outputs.append(call_function(function_name, call_id, args))

                # Submit the outputs of the tools to the current run
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run.status == 'pending':
                print("PENDING...")
                time.sleep(1)  # wait for 1 seconds before the next check

        # Retrieve and print the last message
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        # Convert messages to a list
        messages_list = list(messages)
        print('')
        markdown = Markdown(messages_list[0].content[0].text.value)
        console.print(markdown)
        print('')

except KeyboardInterrupt:
    print("Ctrl+C was pressed, exiting...")
except EOFError:
    print("Ctrl+D was pressed, exiting...")
finally:
    print("goodbye")
    client.beta.threads.delete(thread.id)
    client.beta.assistants.delete(assistant.id)
