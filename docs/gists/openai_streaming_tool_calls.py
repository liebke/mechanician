from openai import OpenAI
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

###########################################################################
## Tool Call Handlers
###########################################################################

def function_handler(function_name, call_id, args):
    pass

def tool_call_handler(tc):
  resp_json_str = json.dumps(function_handler(tc['function']['name'], tc['id'], tc['function']['arguments']))
  return tc, resp_json_str

###########################################################################
## Stream Processing
###########################################################################

def process_stream(stream, messages):
    response = ""
    idx = -1
    tool_calls = []
    futures = []

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            # Collect response to include in message history
            response += chunk.choices[0].delta.content
            # Print the content of the current chunk
            print(chunk.choices[0].delta.content, end="", flush=True)
            
        elif chunk.choices[0].delta.tool_calls is not None:
            tool_calls_chunk = chunk.choices[0].delta.tool_calls[0]
            if tool_calls_chunk.index is not None:
                if(idx < tool_calls_chunk.index):
                    # get current last tool_call if it exists, and call the function handler using the Thread Pool Executor.
                    # This will allow the function handler to run in parallel with the rest of the code.
                    if idx >= 0:
                        if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
                            tc = tool_calls[-1]
                            # Call external function
                            with ThreadPoolExecutor(max_workers=os.getenv("MAX_THREAD_WORKERS")) as executor:
                                futures.append(executor.submit(tool_call_handler, tc))

                    # Since the index has incremented, we need to add a new tool_call to the list
                    tool_calls.append({"index": tool_calls_chunk.index, 
                                       "id": "", 
                                       "type": "", 
                                       "function": {"name": "", 
                                                    "arguments": ""}})

        # Add the tool_call id, type, function name, and arguments to the current tool_call
        if tool_calls_chunk.id is not None :
            tool_calls[idx]["id"] += tool_calls_chunk.id

        if tool_calls_chunk.type is not None:
            tool_calls[idx]["type"] += tool_calls_chunk.type

        if tool_calls_chunk.function.name is not None:
            tool_calls[idx]["function"]["name"] += tool_calls_chunk.function.name

        if tool_calls_chunk.function.arguments is not None:
            tool_calls[idx]["function"]["arguments"] += (tool_calls_chunk.function.arguments)

    # if the assistant responded with a message, add it to the message history
    if(response != ""):
        messages.append({"role": "assistant", "content": response}) 

    # if the assistant responded with tool calls, call the function handler for each tool_call,
    # and add each response to the message history
    elif(tool_calls != []):
        if os.getenv("CALL_TOOLS_IN_PARALLEL") == "True":
            if (len(tool_calls) > len(futures)):
                tc = tool_calls[-1]
                with ThreadPoolExecutor(max_workers=os.getenv("MAX_THREAD_WORKERS")) as executor:
                    futures.append(executor.submit(tool_call_handler, tc))
                    print(f"### Calling external function: {tc['function']['name']}...")

            results = [f.result() for f in as_completed(futures)]

        else:
            results = map(tool_call_handler, tool_calls)

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
        messages.append(assistant_message)
        # Append the tool response messages to the message history
        for msg in tool_resp_messages:
            messages.append(msg)

        # Return N
        response = None

    return response


###########################################################################
## Main Loop
###########################################################################

def main():
    client = OpenAI()
    tool_schemas = {
    "type": "function",
    "function": {
        "name": "get_weather_n_days",
        "description": "Get the weather for the next N days",
        "parameters": { 
        "type": "object",
        "properties": {
            "location": {
            "type": "string",
            "description": "The city and state to get the weather for"
            },
            "number_of_days": {
            "type": "int",
            "description": "The number of days to get the weather for"
            },
        }
        }
    }
    }

    instructions = ""
    messages = []
    # Initialize the conversation with a system message
    messages = [{"role": "system", "content": instructions}]

    # Loop forever, processing user input from the terminal
    while True:
        # Get the user's prompt
        prompt = input("> ")

        # Skip empty prompts
        if prompt == '':
            continue

        messages.append({"role": "user", "content": prompt})

        stream = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            tools=tool_schemas,
            stream=True,
        )
        response = process_stream(stream, messages)
        # if response = None, tool_calls were processed and we need to get a new stream to see the model's response
        while resp == None:
            stream = stream = client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=messages,
                        tools=tool_schemas,
                        stream=True,
                    )
            resp = process_stream(stream)
