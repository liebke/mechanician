
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from mechanician.ai_connectors import StreamingAIConnector
from mechanician.tools import AITools
from mechanician.util import SimpleStreamPrinter
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import pprint
import traceback

logger = logging.getLogger(__name__)



class MistralAIConnector(StreamingAIConnector):
    DEFAULT_MODEL_NAME="mistral-large-latest"

    ###############################################################################
    ## INIT_MODEL
    ###############################################################################

    def __init__(self, 
                 model_name=None,
                 api_key=None,
                 stream_printer = SimpleStreamPrinter(),
                 max_thread_workers=None,
                 client=None):
                      
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
            
        if self.api_key is None:
            raise ValueError("Mistral API Key is required")
    
        self.model_name = model_name or os.getenv("MISTRAL_MODEL_NAME")
            
        if self.model_name is None:
            raise ValueError("Mistral Model Name is required")
        
        self.STREAMING = True
        self.MAX_THREAD_WORKERS = max_thread_workers or int(os.getenv("MAX_THREAD_WORKERS", "10"))
        self.stream_printer = stream_printer
        self.client = client or MistralClient(api_key=api_key)
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
        self.ai_instructions = None
        self.tool_instructions = None
        self.tools = None

        if ai_instructions is not None:
            self.ai_instructions = ai_instructions

        if tool_instructions is not None:
            self.tool_instructions = tool_instructions

        if tools is not None:
            self.tools = tools

        if self.ai_instructions is not None:
            self.messages = [{"role": "system", "content": self.ai_instructions}]
        

    ###############################################################################
    ## SUBMIT_PROMPT
    ###############################################################################

    def submit_prompt(self, prompt, role="user"):
        return self.process_stream(self.get_stream(prompt, role=role))
    
    ###############################################################################
    ## GET_PROMPT
    ###############################################################################

    def get_stream(self, prompt, role="user"):
        client = self.client
        # Create a new message with user prompt
        if prompt is not None:
            self.messages.append({"role": role, "content": prompt})
            
        if not self.tool_instructions:
            stream = client.chat_stream(
                model=self.model_name,
                messages=self.messages,
            )
        else:
            stream = client.chat_stream(
                model=self.model_name,
                messages=self.messages,
                tools=self.tool_instructions,
                # tool_choice="any",
                tool_choice="auto"
            )
            
        return stream
    


    ###############################################################################
    ## PROCESS_TOOL_CALLS_CHUNK
    ###############################################################################

    def process_tool_calls_chunk(self, chunk, tool_calls, tool_calls_index, futures):
        # copy tool_calls so that we don't modify the original
        tool_calls = tool_calls.copy()
        tool_calls_chunk = chunk.choices[0].delta.tool_calls
        for tc in tool_calls_chunk:
            # get current last tool_call if it exists, and call the function handler using the Thread Pool Executor.
            # This will allow the function handler to run in parallel with the rest of the code.
            if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
                self.stream_printer.print(f"Applying tool: {tc.function.name}...")
                with ThreadPoolExecutor(max_workers=self.MAX_THREAD_WORKERS) as executor:
                    futures.append(executor.submit(self.process_tool_call, tc))
                
            tool_calls.append({"id": "", 
                                "type": "", 
                                "function": {"name": "", 
                                            "arguments": ""}})

            if tc.id is not None:
                tool_calls[tool_calls_index]["id"] += tc.id

            if tc.type is not None :
                tool_calls[tool_calls_index]["type"] += tc.type

            if tc.function.name is not None:
                tool_calls[tool_calls_index]["function"]["name"] += tc.function.name

            if tc.function.arguments is not None:
                tool_calls[tool_calls_index]["function"]["arguments"] += (tc.function.arguments)

        return tool_calls, tool_calls_index


    ###############################################################################
    ## PROCESS_TOOL_CALL
    ###############################################################################

    def process_tool_call(self, tc):
        tc_resp = self.tools.call_function(tc.function.name, 
                                           call_id=tc.id, 
                                           params=tc.function.arguments)
        # print("TC RESP:")
        tc_resp = {"response": tc_resp}
        # pprint.pprint(tc_resp)
        function_resp = json.dumps(tc_resp)
        return tc, function_resp

    
    ###############################################################################
    ## PROCESS_STREAM
    ###############################################################################

    def process_stream(self, stream):
        try:
            response = ""
            tool_calls = []
            tool_calls_index = -1
            futures = []
            for chunk in stream:
                if not chunk.choices:
                    continue
                # print("Chunk: ", chunk)
                if chunk.choices[0].delta.content is not None:
                    # Collect response to include in message history
                    response += chunk.choices[0].delta.content
                    self.stream_printer.print(chunk.choices[0].delta.content, end="", flush=True)

                elif chunk.choices[0].delta.tool_calls[0] is not None:
                    # print("Tool Calls CHUNK: ", chunk.choices[0].delta.tool_calls[0])
                    tool_calls, tool_calls_index = self.process_tool_calls_chunk(chunk, tool_calls, tool_calls_index, futures)
                    print("TOOL CALLS: ", tool_calls)

            # if the assistant responded with a message, add it to the message history
            if(response != ""):
                self.messages.append({"role": "assistant", "content": response})
                # print("ASSISTANT: ", response)

            # if the assistant responded with tool calls, call the function handler for each tool_call,
            # and add each response to the message history
            elif(tool_calls != []):
                if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
                    if (len(tool_calls) > len(futures)):
                        tc = tool_calls[-1]
                        print("1. CALLING PROCESS TOOL CALL: TC: ")
                        pprint.pprint(tc)
                        with ThreadPoolExecutor(max_workers=self.MAX_THREAD_WORKERS) as executor:
                            futures.append(executor.submit(self.process_tool_call, tc))
                            self.stream_printer.print(f"Applying tool: {tc.function.name}...")

                    results = [f.result() for f in as_completed(futures)]

                else:
                    print("2. CALLING PROCESS TOOL CALL: TC: ")
                    pprint.pprint(tool_calls)
                    results = map(self.process_tool_call, tool_calls)

                assistant_message = {"role": "assistant", "tool_calls": []}
                tool_resp_messages = []
                for result in results:
                    tc, function_resp = result
                    tc_json = {"id": tc.id,
                                "type": tc.type,
                                "function": {"name": tc.function.name,
                                            "arguments": tc.function.arguments}}
                    # print("TC JSON: ")
                    # pprint.pprint(tc_json)
                    # print("TC RESULTS: ")
                    # pprint.pprint(result)
                    assistant_message['tool_calls'].append(tc_json)
                    tool_resp_message = {"role": "tool", 
                                         "name": tc.function.name,
                                         "content": function_resp}
                    # print("TOOL RESP MESSAGE:")
                    pprint.pprint(tool_resp_message)
                    tool_resp_messages.append(tool_resp_message)
                    
                # Append the assistant message with tool_calls to the message history
                self.messages.append(assistant_message)
                # Append the tool response messages to the message history
                for msg in tool_resp_messages:
                    self.messages.append(msg)

                response = None

            return response
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            return None


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