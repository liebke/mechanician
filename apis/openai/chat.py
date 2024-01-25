
from openai import OpenAI
from rich.console import Console
from apis.streaming_model_api import StreamingModelAPI
from apis.openai.tools import call_function
from apis.openai.tool_schemas import tool_schemas
from util import print_markdown
import json
import os

from concurrent.futures import ThreadPoolExecutor, as_completed



class OpenAIChat(StreamingModelAPI):

    ###############################################################################
    ## INIT_MODEL
    ###############################################################################

    def __init__(self):
        self.model = {}
        self.model["MODEL_NAME"] = os.getenv("MODEL_NAME") # "gpt-4-1106-preview"
        self.client = OpenAI()
        self.model["client"] = self.client

        with open("./resources/instructions.md", 'r') as file:
            instructions = file.read()

        # Initialize the conversation with a system message
        self.messages = [{"role": "system", "content": instructions}]

        self.console = Console()

        print_markdown(self.console, f"* MODEL_NAME: {self.model['MODEL_NAME']}")


    ###############################################################################
    ## SUBMIT_PROMPT
    ###############################################################################

    def get_stream(self, prompt):
        client = self.model["client"]
        # Create a new message with user input
        self.messages.append({"role": "user", "content": prompt})

        stream = client.chat.completions.create(
            model=self.model["MODEL_NAME"],
            messages=self.messages,
            tools=tool_schemas,
            stream=True,
        )
        return stream
    


    ###############################################################################
    ## PROCESS_TOOL_CALLS_CHUNK
    ###############################################################################

    def process_tool_calls_chunk(self, chunk, tool_calls, tool_calls_index, futures):
        # copy tool_calls so that we don't modify the original
        tool_calls = tool_calls.copy()
        tool_calls_chunk = chunk.choices[0].delta.tool_calls[0]
        if(tool_calls_chunk.index != None):
            if(tool_calls_index < tool_calls_chunk.index):
                # get current last tool_call if it exists, and call the function handler using the Thread Pool Executor.
                # This will allow the function handler to run in parallel with the rest of the code.
                if tool_calls_index >= 0:
                    if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
                        tc = tool_calls[-1]
                        print_markdown(self.console, f"### Calling external function: {tc['function_name']}...")
                        with ThreadPoolExecutor() as executor:
                            futures.append(executor.submit(self.process_tool_call, tc))
                    
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

        return tool_calls, tool_calls_index


    ###############################################################################
    ## PROCESS_TOOL_CALL
    ###############################################################################

    def process_tool_call(self, tc):
        # convert args from list to string
        tc["args"] = ''.join(tc["args"])

        msg1 = {"role": "assistant",
                "tool_calls": [{
                                "id": tc['id'],
                                "function": {"name": tc['function_name'],
                                "arguments": tc['args']
                                },
                          "type": tc['type']
                        }]}

        function_resp = json.dumps(call_function(tc['function_name'], tc['id'], tc['args']))
        msg2 = {"role": "tool", 
                "tool_call_id": tc['id'],
                "name": tc['function_name'],
                "content": function_resp}
        
        return msg1, msg2

    
    ###############################################################################
    ## PROCESS_STREAM
    ###############################################################################

    def process_stream(self, stream):
        
        response = []
        tool_calls = []
        tool_calls_index = -1
        futures = []
        print("\n")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                # Collect response to include in message history
                response.append(chunk.choices[0].delta.content)
                print(chunk.choices[0].delta.content, end="", flush=True)

            elif chunk.choices[0].delta.tool_calls is not None:
                tool_calls, tool_calls_index = self.process_tool_calls_chunk(chunk, tool_calls, tool_calls_index, futures)

        # if the assistant responded with a message, add it to the message history
        if(response != []):
            self.messages.append({"role": "assistant", "content": ''.join(response)})

        # if the assistant responded with tool calls, call the function handler for each tool_call,
        # and add each response to the message history
        elif(tool_calls != []):
            if tool_calls:
                if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
                    if (len(tool_calls) > len(futures)):
                        tc = tool_calls[-1]
                        with ThreadPoolExecutor() as executor:
                            futures.append(executor.submit(self.process_tool_call, tc))
                            print_markdown(self.console, f"### Calling external function: {tc['function_name']}...")

                    results = [f.result() for f in as_completed(futures)]

                else:
                    results = map(self.process_tool_call, tool_calls)

                for result in results:
                    msg1, msg2 = result
                    self.messages.append(msg1)
                    self.messages.append(msg2)

            for tc in tool_calls: 
                # convert args from list to string
                tc["args"] = ''.join(tc["args"])
                # print_markdown(self.console, f"* Function Name: {tc['function_name']}")
                # print_markdown(self.console, f"* ID: {tc['id']}")
                # print_markdown(self.console, f"* Index: {tc['index']}")
                # print_markdown(self.console, f"* Arguments:")
                # print_markdown(self.console, f"```json \n{tc['args']}\n ```")

                response = None

        print("\n")
        
        return response


    ###############################################################################
    ## CLEAN UP
    ###############################################################################

    def clean_up(self):
        pass