from dotenv import load_dotenv
from ux import run_model, run_streaming_model
from apis.openai.assistants import OpenAIAssistant
from apis.openai.chat import OpenAIChat


###############################################################################
## Main program execution
###############################################################################

# Load environment variables from a .env file
load_dotenv()

# Initialize the model
# model = OpenAIAssistant()
model = OpenAIChat()

# Run the REPL loop
# run_model(model)
run_streaming_model(model)

