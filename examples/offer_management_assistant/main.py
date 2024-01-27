from dandyhare.ux.cli import run_model, run_streaming_model
from dotenv import load_dotenv
# from dandyhare.apis.openai.assistants_service_connector import OpenAIAssistantServiceConnector
from dandyhare.openai.chat_service_connector import OpenAIChatServiceConnector

from examples.offer_management_assistant.tools import call_function
from examples.offer_management_assistant.tool_schemas import tool_schemas



###############################################################################
## Main program execution
###############################################################################

# Load environment variables from a .env file
load_dotenv()

with open("./examples/offer_management_assistant/instructions.md", 'r') as file:
    instructions = file.read()

# Initialize the model
# model = OpenAIAssistant(tool_schemas=tool_schemas, function_handler=call_function)
model = OpenAIChat(instructions=instructions, tool_schemas=tool_schemas, tool_handler=call_function)

# Run the REPL loop
# run_model(model, name="Product Offer AI Assistant (Proof of Concept)"
run_streaming_model(model, name="Product Offer AI Assistant (Proof of Concept)")

