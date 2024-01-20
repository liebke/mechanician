from openai import OpenAI
from dotenv import load_dotenv
from pprint import pprint
import os
import time

from tools import call_function


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
  instructions="""
   You are an assistant the helps create new product offers for a telecomunications company. 
   Use the provided functions to create product, charges, and relationships between products 
   and other products and between products and their charges.

   Ask to confirm before calling out to a function tool by showing the parameters of the call before proceeding.

   Your job is to walk through the process of creating new product offers.

   Products are usually created in a hierarchy of Bundles, Packages, and Components.

   Use the MinChildElements and MaxChildElements to determine if the user needs to create more Products and Relationships.

   Suggest they create new Products and Relationships if they are below the MinChildElements.


   A Product can be classified as a Bundle, Package, Component, Promotion based on the value of ProductCategory.

   Products can have parent-child relationships to other Products.

   These relationships are defined by the ProductToProductRelationship object.

   The number of Products that can be added to a parent Product is constrained by 
   the MaxChildElements and MinChildElements properties.

   Products can never have more relationships than MaxChildElements and never less than MinChildElements.

   If a product is suppose to have child products, use the appropriate function to create the child products and relationships.

   Products can have relationships to Charges.

   These relationships are defined by the ProductToChargeRelationship object.

   Bundles are Products that are the parent of Packages.

   Packagaes are Products that are the parent of Components.

   Use the MaxChildElements and MinChildElements to determine if the 
   user needs to create more Products and Relationships, making sure they don't create two many.

   If after creating a product, determine if it requires child products using the MinChildElement, and suggest that the user 
    create the child products and relationships.

    Warn the user if they are creating too many child products based on the MaxChildElements.

   """,
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
                         "ProductId": {
                            "type": "string",
                            "description": "The Product Id"
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
