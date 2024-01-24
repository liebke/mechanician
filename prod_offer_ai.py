from openai import OpenAI
import json
from dotenv import load_dotenv
from util import print_markdown
from rich.console import Console
from pprint import pprint

# Import custom function call_function from tools module
from models.openai.tools import call_function
from models.openai.tool_schemas import tool_schemas

# Load environment variables from a .env file
load_dotenv()

# Create a Console object for pretty terminal outputs
console = Console()

with open("./resources/instructions.md", 'r') as file:
    instructions = file.read()
    # print(f"INSTRUCTIONS:\n {instructions}")


# Initialize the conversation with a system message
messages = [
    {"role": "system", "content": instructions},
]

client = OpenAI()

try:
    while True:
        # Get user input
        user_input = input("> ")

        if user_input == '':
            continue

        if user_input.startswith('/file'):
            filename = user_input.replace('/file ', '', 1)

            with open(filename, 'r') as file:
                user_input = file.read()
                print('')
                print_markdown(console, "------------------")
                print_markdown(console, "## INPUT FILE")
                print_markdown(console, f"``` \n{user_input}\n ```")
                print_markdown(console, "------------------")
                print('')


        messages.append({"role": "user", "content": user_input})

        stream = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            tools=tool_schemas,
            stream=True,
        )
        response = []
        tool_calls_response = []
        tool_calls = []
        tool_calls_index = -1
        tool_call = None
        print("\n")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response.append(chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="")

            elif chunk.choices[0].delta.tool_calls is not None:
                tool_calls_chunk = chunk.choices[0].delta.tool_calls[0]
                if(tool_calls_chunk.index != None):
                    if(tool_calls_index < 0):
                        tool_calls_index = tool_calls_chunk.index
                        tool_calls.append({"args": []})
                    tool_calls[tool_calls_index]["index"] = tool_calls_chunk.index

                if(tool_calls_chunk.id != None):
                    tool_calls[tool_calls_index]["id"] = tool_calls_chunk.id

                if(tool_calls_chunk.type != None):
                    tool_calls[tool_calls_index]["type"] = tool_calls_chunk.type

                if(tool_calls_chunk.function.name != None):
                    tool_calls[tool_calls_index]["function_name"] = tool_calls_chunk.function.name

                if(tool_calls_chunk.function.arguments != None):
                    tool_calls[tool_calls_index]["args"] += (tool_calls_chunk.function.arguments)
                # pprint(vars(chunk))

        # DEBUG: print the response
        if(response != []):
            messages.append({"role": "assistant", "content": ''.join(response)})
            # print(''.join(response))
        elif(tool_calls != []):
            for tc in tool_calls: 
                tc["args"] = json.dumps(json.loads(''.join(tc["args"])))
                print_markdown(console, f"* Function Name: {tc['function_name']}")
                print_markdown(console, f"* ID: {tc['id']}")
                print_markdown(console, f"* Index: {tc['index']}")
                print_markdown(console, f"* Arguments:")
                print_markdown(console, f"```json \n{tc['args']}\n ```")

                msg_tool_calls = {"id": tc['id'],
                                  "function": {"name": tc['function_name'],
                                               "arguments": tc['args']
                                              },
                                  "type": tc['type']
                                }
                msg1 = {"role": "assistant",
                        "tool_calls": [msg_tool_calls]}
                msg2 = {"role": "tool", 
                        "tool_call_id": tc['id'],
                        "name": tc['function_name'],
                        "content": json.dumps(call_function(tc['function_name'], tc['id'], tc['args']))}
                messages.append(msg1)
                messages.append(msg2)
                
                print(msg1)
                print("----------------------------------")
                print(msg2)
        print("\n")
        





except KeyboardInterrupt:
    print("Ctrl+C was pressed, exiting...")

