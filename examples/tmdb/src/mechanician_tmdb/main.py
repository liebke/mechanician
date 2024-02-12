from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector
# from mechanician_openai import OpenAIAssistantsConnector
from tmdb_ai_tools import TMDbAITools
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)


###############################################################################
## AI Connector
###############################################################################

def init_ai():
    tmdb_tools = TMDbAITools(os.getenv("TMDB_READ_ACCESS_TOKEN"))
    # Initialize the connection to the AI assistant
    ai_connector = OpenAIChatConnector(api_key=os.getenv("OPENAI_API_KEY"), 
                                         model_name=os.getenv("OPENAI_MODEL_NAME"))
    ai = TAGAI(ai_connector,
               instruction_set_directory="./instructions",
               tools=tmdb_tools,
               name="TMDB AI" )
    return ai

###############################################################################
## Main program execution
###############################################################################

def main():
    # Load environment variables from a .env file
    load_dotenv()

    ai = init_ai()
    shell.run(ai)

if __name__ == '__main__':
    main()

