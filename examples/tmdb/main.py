from mechanician.ux.cli import run
from mechanician.openai.chat_service_connector import OpenAIChatServiceConnector
from mechanician.openai.assistants_service_connector import OpenAIAssistantServiceConnector
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
connector = OpenAIChatServiceConnector(instructions=instructions, 
                                       tool_schemas=tool_schemas, 
                                       tool_handler=tmdb_handler,
                                       name="TMDB Assistant" )

# connector = OpenAIAssistantServiceConnector(instructions=instructions, 
#                                             tool_schemas=tool_schemas, 
#                                             tool_handler=tmdb_handler,
#                                             name="TMDB Assistant")

# Run the REPL loop
run(connector, name="TMDB Assistant")

