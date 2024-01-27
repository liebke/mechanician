from dandyhare.ux.cli import run_model, run_streaming_model
from dotenv import load_dotenv
# from dandyhare.apis.openai.assistants import OpenAIAssistant
from dandyhare.openai.chat import OpenAIChat

from tmdb_tools import TMDbHandler
from tmdb_tool_schemas import tool_schemas
import os



###############################################################################
## Main program execution
###############################################################################

# Load environment variables from a .env file
load_dotenv()

with open("./examples/tmdb/instructions.md", 'r') as file:
    instructions = file.read()

tmdb_handler = TMDbHandler(os.getenv("TMDB_READ_ACCESS_TOKEN"))

# Initialize the model
model = OpenAIChat(instructions=instructions, tool_schemas=tool_schemas, tool_handler=tmdb_handler)

# Run the REPL loop
run_streaming_model(model, name="TMDB Assistant")

