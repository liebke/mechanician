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

def ai_connector():
    # Load environment variables from a .env file
    load_dotenv()

    with open("./instructions.md", 'r') as file:
        instructions = file.read()

    tmdb_handler = TMDbHandler(os.getenv("TMDB_READ_ACCESS_TOKEN"))

    # Initialize the connection to the AI assistant
    ai = OpenAIChatAIConnector(instructions=instructions, 
                            tool_schemas=tool_schemas, 
                            tool_handler=tmdb_handler,
                            assistant_name="TMDB AI" )

    # ai = OpenAIAssistantAIConnector(instructions=instructions, 
    #                                 tool_schemas=tool_schemas, 
    #                                 tool_handler=tmdb_handler,
    #                                 assistant_name="TMDB AI")

    return ai

def main():
    ai = ai_connector()
    run(ai)

