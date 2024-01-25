from dotenv import load_dotenv
from dandyhare.ux import run_model, run_streaming_model
from dandyhare.apis.openai.assistants import OpenAIAssistant
from dandyhare.apis.openai.chat import OpenAIChat

from dandyhare.apis.openai.tools import call_function
from dandyhare.apis.openai.tool_schemas import tool_schemas



###############################################################################
## Main program execution
###############################################################################

# Load environment variables from a .env file
load_dotenv()

# Initialize the model
# model = OpenAIAssistant(tool_schemas=tool_schemas, function_handler=call_function)
model = OpenAIChat(tool_schemas=tool_schemas, function_handler=call_function)

# Run the REPL loop
# run_model(model)
run_streaming_model(model)

