from openai import OpenAI
import json
# import openai
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored

# Import custom function call_function from tools module
from tools import call_function

# Import tool_schemas from tool_schemas module
from tool_schemas import tool_schemas
import time


GPT_MODEL = "gpt-4-1106-preview"

from dotenv import load_dotenv

# Import Markdown and Console from rich library for pretty terminal outputs
from rich.markdown import Markdown
from rich.console import Console


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai.api_key,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


# Load environment variables from a .env file
load_dotenv()

# Create a Console object for pretty terminal outputs
console = Console()

with open("./resources/instructions.md", 'r') as file:
    instructions = file.read()
    # print(f"INSTRUCTIONS:\n {instructions}")

# openai.api_key = 'your-api-key'

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
                console.print(Markdown("------------------"))
                console.print(Markdown("## INPUT FILE"))
                console.print(Markdown(f"``` \n{user_input}\n ```"))
                console.print(Markdown("------------------"))
                print('')


        #########################
        # messages = []
        # messages.append({"role": "system", "content": instructions})
        # messages.append({"role": "user", "content": user_input})
        # chat_response = chat_completion_request(
        #     messages, tools=tool_schemas, model=GPT_MODEL
        # )
        # assistant_message = chat_response.json()["choices"][0]["message"]
        # messages.append(assistant_message)
        # assistant_message
        #########################
                

        messages.append({"role": "user", "content": user_input})


        stream = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            tools=tool_schemas,
            stream=True,
        )
        response = []
        print("\n")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response.append(chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="")

        print("\n")


        # Add AI response to the messages
        # Add AI response to the messages
        messages.append({"role": "assistant", "content": ''.join(response)})





except KeyboardInterrupt:
    print("Ctrl+C was pressed, exiting...")

