from mechanician import TAGAI, run
from mechanician_openai import OpenAIChatConnector
# from mechanician_openai import OpenAIAssistantsConnector
from tmdb_ai_tools import TMDbAITools
from tmdb_tool_instructions import tool_instructions
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)


###############################################################################
## AI Connector
###############################################################################

def init_ai():
    # Load environment variables from a .env file
    load_dotenv()

    with open("./resources/instructions.md", 'r') as file:
        instructions = file.read()

    tmdb_tools = TMDbAITools(os.getenv("TMDB_READ_ACCESS_TOKEN"))
    # Initialize the connection to the AI assistant
    ai_connector = OpenAIChatConnector(api_key=os.getenv("OPENAI_API_KEY"), 
                                         model_name=os.getenv("OPENAI_MODEL_NAME"))
    ai = TAGAI(ai_connector,
               ai_instructions=instructions, 
               tool_instructions=tool_instructions, 
               tools=tmdb_tools,
               name="TMDB AI" )
    return ai

###############################################################################
## Main program execution
###############################################################################

def main():
    ai = init_ai()
    run(ai)

if __name__ == '__main__':
    main()

