
from openai import OpenAI
from mechanician.ai_connectors import StreamingAIConnector, AIConnectorFactory
from mechanician.tools import AITools
from mechanician.util import SimpleStreamPrinter
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import pprint

logger = logging.getLogger(__name__)



class OpenAIChatConnector(StreamingAIConnector):
    DEFAULT_MODEL_NAME="gpt-4-1106-preview"
    DEFAULT_ENDPOINT="https://api.openai.com"

    ###############################################################################
    ## INIT_MODEL
    ###############################################################################

    def __init__(self, 
                 model_name=None,
                 api_key=None,
                 base_url=None,
                 stream_printer = SimpleStreamPrinter(),
                 max_thread_workers=None,
                 client=None):
                      
        self.base_url = base_url or self.DEFAULT_ENDPOINT
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            
        if self.api_key is None:
            raise ValueError("OpenAI API Key is required")
    
        self.model_name = model_name or os.getenv("OPENAI_MODEL_NAME")
            
        if self.model_name is None:
            raise ValueError("OpenAI Model Name is required")
        
        self.STREAMING = True
        self.MAX_THREAD_WORKERS = max_thread_workers or int(os.getenv("MAX_THREAD_WORKERS", "10"))
        self.stream_printer = stream_printer
        self.client = client or OpenAI(api_key=api_key)
        self.ai_tool_instructions = None
        self.ai_instructions = None
        self.tools = None
        self.messages = []


    ###############################################################################
    ## INSTRUCT
    ###############################################################################

    def _instruct(self, ai_instructions=None, 
                  ai_tool_instructions=None,
                  tools: 'AITools'=None):
        self.ai_instructions = None
        self.ai_tool_instructions = None
        self.tools = None

        if ai_instructions is not None:
            self.ai_instructions = ai_instructions

        if ai_tool_instructions is not None:
            self.ai_tool_instructions = ai_tool_instructions

        if tools is not None:
            self.tools = tools

        if self.ai_instructions is not None:
            self.messages = [{"role": "system", "content": self.ai_instructions}]
        

    ###############################################################################
    ## SUBMIT_PROMPT
    ###############################################################################
            
    def submit_prompt(self, prompt, role="user"):
        no_content = True
        while no_content:
            stream = self.get_stream(prompt, role=role)
            for content in self.process_stream(stream):
                if content is None:
                    no_content = True
                    break
                else:
                    no_content = False
                    self.stream_printer.print(content, end="", flush=True)
    

    ###############################################################################
    ## GET_PROMPT
    ###############################################################################

    def get_stream(self, prompt, role="user"):
        client = self.client
        # Create a new message with user prompt
        if prompt is not None:
            self.messages.append({"role": role, "content": prompt})
            
        if not self.ai_tool_instructions:
            stream = client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                stream=True,
            )
        else:
            stream = client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                tools=self.ai_tool_instructions,
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
        if tool_calls_chunk.index is not None :
            if(tool_calls_index < tool_calls_chunk.index):
                # get current last tool_call if it exists, and call the function handler using the Thread Pool Executor.
                # This will allow the function handler to run in parallel with the rest of the code.
                if tool_calls_index >= 0:
                    if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
                        tc = tool_calls[-1]
                        with ThreadPoolExecutor(max_workers=self.MAX_THREAD_WORKERS) as executor:
                            futures.append(executor.submit(self.process_tool_call, tc))
                    
                tool_calls_index = tool_calls_chunk.index
                tool_calls.append({"index": tool_calls_index, 
                                   "id": "", 
                                   "type": "", 
                                   "function": {"name": "", 
                                                "arguments": ""}})

        if tool_calls_chunk.id is not None:
            tool_calls[tool_calls_index]["id"] += tool_calls_chunk.id

        if tool_calls_chunk.type is not None :
            tool_calls[tool_calls_index]["type"] += tool_calls_chunk.type

        if tool_calls_chunk.function.name is not None:
            tool_calls[tool_calls_index]["function"]["name"] += tool_calls_chunk.function.name

        if tool_calls_chunk.function.arguments is not None:
            tool_calls[tool_calls_index]["function"]["arguments"] += (tool_calls_chunk.function.arguments)

        return tool_calls, tool_calls_index


    ###############################################################################
    ## PROCESS_TOOL_CALL
    ###############################################################################

    def process_tool_call(self, tc):
        function_resp = json.dumps(self.tools.call_function(tc['function']['name'], 
                                                            call_id=tc['id'], 
                                                            params=tc['function']['arguments']))
        return tc, function_resp

    def process_stream(self, stream):
        response = ""
        tool_calls = []
        tool_calls_index = -1
        futures = []
        for chunk in stream:
            if not chunk.choices:
                continue

            if chunk.choices[0].delta.content is not None:
                # Yield response chunk to include in message history
                response += chunk.choices[0].delta.content
                yield chunk.choices[0].delta.content

            if chunk.choices[0].delta.tool_calls is not None:
                tool_calls, tool_calls_index = self.process_tool_calls_chunk(chunk, tool_calls, tool_calls_index, futures)

        # if the assistant responded with a message, add it to the message history
        if(response != ""):
            self.messages.append({"role": "assistant", "content": response})

        # if the assistant responded with tool calls, call the function handler for each tool_call,
        # and add each response to the message history
        if(tool_calls != []):
            if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
                if (len(tool_calls) > len(futures)):
                    tc = tool_calls[-1]
                    with ThreadPoolExecutor(max_workers=self.MAX_THREAD_WORKERS) as executor:
                        futures.append(executor.submit(self.process_tool_call, tc))
                        yield f"Applying tool: {tc['function']['name']}...\n\n"

                results = [f.result() for f in as_completed(futures)]

            else:
                results = map(self.process_tool_call, tool_calls)

            assistant_message = {"role": "assistant", "tool_calls": []}
            tool_resp_messages = []
            for result in results:
                tc, function_resp = result
                assistant_message['tool_calls'].append(tc)
                tool_resp_message = {"role": "tool", 
                                     "tool_call_id": tc['id'],
                                     "name": tc['function']['name'],
                                     "content": function_resp }
                tool_resp_messages.append(tool_resp_message)
                
            # Append the assistant message with tool_calls to the message history
            self.messages.append(assistant_message)
            # Append the tool response messages to the message history
            for msg in tool_resp_messages:
                self.messages.append(msg)
    
            yield None
        


    ###############################################################################
    ## GET_MESSAGE_HISTORY
    ###############################################################################
    def get_message_history(self):
        return self.messages
    

    ###############################################################################
    ## CLEAN UP
    ###############################################################################

    def clean_up(self):
        pass


###############################################################################
## OpenAIChatConnectorFactory
###############################################################################

class OpenAIChatConnectorFactory(AIConnectorFactory):

    def __init__(self,
                 model_name=None,
                 api_key=None,
                 base_url=None,
                 stream_printer = SimpleStreamPrinter(),
                 max_thread_workers=None,
                 client=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or os.getenv("OPENAI_MODEL_NAME")
        self.base_url = base_url or OpenAIChatConnector.DEFAULT_ENDPOINT
        self.stream_printer = stream_printer
        self.client = client
        self.max_thread_workers = max_thread_workers or int(os.getenv("MAX_THREAD_WORKERS", "10"))


    def create_ai_connector(self, context:dict={}):
        return OpenAIChatConnector(api_key=self.api_key, 
                                   model_name=self.model_name,
                                   base_url=self.base_url,
                                   stream_printer=self.stream_printer,
                                   max_thread_workers=self.max_thread_workers,
                                   client=self.client)
    
