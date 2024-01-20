from openai import OpenAI
from dotenv import load_dotenv
from pprint import pprint
import os
import time


# Load environment variables
load_dotenv()

client = OpenAI()

# assistant = client.beta.assistants.create(
#     name="Math Tutor",
#     instructions="You are a personal math tutor. Write and run code to answer math questions.",
#     tools=[{"type": "code_interpreter"}],
#     model="gpt-4-1106-preview"
# )

assistant = client.beta.assistants.create(
  instructions="You are a weather bot. Use the provided functions to answer questions.",
  model="gpt-4-1106-preview",
  tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather_forecast",
            "description": "Get an N-day weather forecast",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast",
                    }
                },
                "required": ["location", "format", "num_days"]
            },
        }
    },
    {
    "type": "function",
    "function": {
      "name": "getNickname",
      "description": "Get the nickname of a city",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", 
                       "description": "The city and state e.g. San Francisco, CA"},
        },
        "required": ["location"]
      }
    } 
  }
]
)

thread = client.beta.threads.create()

try:
    while True:
        user_input = input("> ")

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
            instructions="Please address the user as Jane Doe. The user has a premium account."
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
                print("ACTION REQUIRED...")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    pprint(vars(tool_call))  
                    call_id = tool_call.id  # call_id is already a string, no need to index
                    function_name = tool_call.function.name
                    args = tool_call.function.arguments
                    if function_name == "get_current_weather":
                        tool_outputs.append({
                            "tool_call_id": call_id,  # use call_id directly
                            "output": "22C",
                        })
                    elif function_name == "get_n_day_weather_forecast":
                        tool_outputs.append({
                            "tool_call_id": call_id,  # use call_id directly
                            "output": "20C",
                        })
                    elif function_name == "getNickname":
                        tool_outputs.append({
                            "tool_call_id": call_id,  # use call_id directly
                            "output": "LA",
                        })

                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run.status == 'pending':
                print("PENDING...")

            time.sleep(1)  # wait for 5 seconds before the next check

        # Retrieve and print the last message
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        # Convert messages to a list
        messages_list = list(messages)
        print(messages_list[0].content[0].text.value)

except KeyboardInterrupt:
    print("Ctrl+C was pressed, exiting...")
except EOFError:
    print("Ctrl+D was pressed, exiting...")
finally:
    print("This block is executed no matter what")
    client.beta.threads.delete(thread.id)
    client.beta.assistants.delete(assistant.id)
