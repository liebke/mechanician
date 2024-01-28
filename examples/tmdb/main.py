from mechanician.ux.cli import run
from mechanician.openai.chat_ai_connector import OpenAIChatAIConnector
from mechanician.openai.assistants_ai_connector import OpenAIAssistantAIConnector
from tmdb_tools import TMDbHandler
from tmdb_tool_schemas import tool_schemas
from dotenv import load_dotenv
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
ai = OpenAIChatAIConnector(instructions=instructions, 
                           tool_schemas=tool_schemas, 
                           tool_handler=tmdb_handler,
                           assistant_name="TMDB AI" )

# ai = OpenAIAssistantAIConnector(instructions=instructions, 
#                                 tool_schemas=tool_schemas, 
#                                 tool_handler=tmdb_handler,
#                                 assistant_name="TMDB AI")

# Run the REPL loop
run(ai)

