from openai import OpenAI
from dotenv import load_dotenv
from pprint import pprint
import os
import time

from tools import call_function


# Load environment variables
load_dotenv()

client = OpenAI()

# with open("./resources/create_entities_activity_diagram.plantuml", 'r') as file:
#                 activity_diagram = file.read()
#                 # print(f"ACTIVITY DIAGRAM:\n {activity_diagram}")

with open("./resources/instructions2.md", 'r') as file:
                instructions = file.read()
                print(f"INSTRUCTIONS 2:\n {instructions}")

assistant = client.beta.assistants.create(
  instructions=instructions,
  model="gpt-4-1106-preview",
  tools = [
        {
            "type": "function",
            "function": {
                "name": "createProduct",
                "description": "Creates a new Product object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ProductCategory": {
                            "type": "string",
                            "description": "The Product Category, must be one of the following: Bundle, Package, Component, Promotion, ComponentGroup"
                        },
                         "BusinessId": {
                            "type": "string",
                            "description": """An automatically generated, business-readable ID that labels the entity with a suitable ID that can be used to reference the entity so that longer, internal system identifiers are not needed. Along with Name, you can use this identifier to search for entities, in addition to the other search options."""
                        },
                        "MaxChildElements": {
                            "type": "integer",
                            "description": "Maximum customer portfolio instances"
                        },
                        "MinMinChildElements": {
                            "type": "integer",
                            "description": "Minimum customer portfolio instances"
                        },
                        "AvailableEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity is no longer available to customers, which must fall within the effective date range."""
                        },
                        "AvailableStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity becomes available to customers, which must fall within the effective date range. This value is required by default."""
                        },
                        "BusinessID": {
                            "type": "string",
                            "description": "The business identifier"
                        },
                        "CategoryID": {
                            "type": "string",
                            "description": "The category identifier"
                        },
                        "Description": {
                            "type": "string",
                            "description": "A description of the entity."
                        },
                        "EffectiveEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity should become inactive in your organization. This value is optional to allow for no expiry date."""
                        },
                        "EffectiveStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": """The date on which the entity should become effective and active in your organization. This value is required by default."""
                        },
                        "ElementGuid": {
                            "type": "string",
                            "description": "The element GUID"
                        },
                        "ElementTypeGuid": {
                            "type": "string",
                            "description": "The element type GUID"
                        },
                        "Name": {
                            "type": "string",
                            "description": """Name: A descriptive name for the entity that must be unique in the category of the product catalog where the entity resides. For example, two components may not share the same name unless they sit in different categories of the catalog. This value is required."""
                        }
                    },
                    "required": ["Name", "ProductCategory", "ProductId"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createProductToProductRelationship",
                "description": "Creates a new Relationship object between two Products",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "SourceProduct": {
                            "type": "string",
                            "description": "The ID of the source product"
                        },
                        "TargetProduct": {
                            "type": "string",
                            "description": "The ID of the target product"
                        },
                        
                    },
                    "required": ["SourceProduct", "TargetProduct"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createProductToChargeRelationship",
                "description": "Creates a new Relationship object between a Product and a Charge object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ProductId": {
                            "type": "string",
                            "description": "The ID of the Product"
                        },
                        "ChargeId": {
                            "type": "string",
                            "description": "The ID of the Charge"
                        },
                        
                    },
                    "required": ["ProductId", "ChargeId"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createCharge",
                "description": "Creates a new Product object",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "AvailableEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The available end date"
                        },
                        "AvailableStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The available start date"
                        },
                        "BusinessID": {
                            "type": "string",
                            "description": "The business identifier"
                        },
                        "CategoryID": {
                            "type": "string",
                            "description": "The category identifier"
                        },
                        "Description": {
                            "type": "string",
                            "description": "The description of the launch entity"
                        },
                        "EffectiveEndDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The effective end date"
                        },
                        "EffectiveStartDate": {
                            "type": "string",
                            "format": "date",
                            "description": "The effective start date"
                        },
                        "ElementGuid": {
                            "type": "string",
                            "description": "The element GUID"
                        },
                        "ElementTypeGuid": {
                            "type": "string",
                            "description": "The element type GUID"
                        },
                        "Name": {
                            "type": "string",
                            "description": "The name of the launch entity"
                        },
                        "ChargeId": {
                            "type": "string",
                            "description": "The ID of the Charge"
                        }
                    },
                    "required": ["Name", "ChargeId"]
                }
            }
        }
    ]
)

thread = client.beta.threads.create()

try:
    while True:
        user_input = input("> ")

        if user_input == '':
            # print("user_input is empty, skipping...")
            continue

        if user_input.startswith('/slurp'):
            filename = user_input.replace('/slurp ', '', 1)

            print(f"slurping file: {filename}")
            with open(filename, 'r') as file:
                user_input = file.read()
                print(f"Updated user_input: {user_input}")

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
                print("ACTION REQUIRED...")
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    pprint(vars(tool_call))  
                    call_id = tool_call.id  # call_id is already a string, no need to index
                    function_name = tool_call.function.name
                    args = tool_call.function.arguments
                    tool_outputs.append(call_function(function_name, call_id, args))

                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

            elif run.status == 'pending':
                print("PENDING...")

            time.sleep(2)  # wait for 0.25 seconds before the next check

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
    print("goodbye")
    client.beta.threads.delete(thread.id)
    client.beta.assistants.delete(assistant.id)
