from openai import OpenAI
from dotenv import load_dotenv
from pprint import pprint
import os
from tools import call_function
from tool_schemas import tool_schemas
import time
from rich.markdown import Markdown
from rich.console import Console


# Load environment variables
load_dotenv()
console = Console()

client = OpenAI()

print('\n\n\n')

with open("./resources/instructions.md", 'r') as file:
                instructions = file.read()
                # print(f"INSTRUCTIONS:\n {instructions}")

assistant = client.beta.assistants.create(
    instructions=instructions,
    model="gpt-4-1106-preview",
    tools=tool_schemas
)

thread = client.beta.threads.create()

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
                # print('')
                # print("------------------")
                # print("SENDING REQUEST TO EXTERNAL PROGRAM...")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    call_id = tool_call.id  # call_id is already a string, no need to index
                    function_name = tool_call.function.name
                    args = tool_call.function.arguments
                    tool_outputs.append(call_function(function_name, call_id, args))
                    # print(f"FUNCTION NAME: {tool_call.function.name}")
                    # print("FUNCTION ARGUMENTS:")
                    # pprint(tool_call.function.arguments)
                    # print(f"CALL_ID: {tool_call.id}")
                    # print("------------------")
                    # print('')

                    # pprint(vars(tool_call))

                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run.status == 'pending':
                print("PENDING...")
                # wait_for_completion(run)
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
        # print(messages_list[0].content[0].text.value)

except KeyboardInterrupt:
    print("Ctrl+C was pressed, exiting...")
except EOFError:
    print("Ctrl+D was pressed, exiting...")
finally:
    print("goodbye")
    client.beta.threads.delete(thread.id)
    client.beta.assistants.delete(assistant.id)
