from mechanician.ux.cli import run
from dotenv import load_dotenv
# from mechanician.apis.openai.assistants_service_connector import OpenAIAssistantServiceConnector
from mechanician.openai.chat_ai_connector import OpenAIChatAIConnector

from tools import OfferManagementToolHandler
from tool_schemas import tool_schemas

import json


###############################################################################
## AI Connector
###############################################################################

def ai_connector():
    # Load environment variables from a .env file
    load_dotenv()

    with open("./instructions.md", 'r') as file:
        instructions = file.read()

    # Initialize the model
    # model = OpenAIAssistant(tool_schemas=tool_schemas, function_handler=call_function)
    return OpenAIChatAIConnector(instructions=instructions, 
                                 tool_schemas=tool_schemas, 
                                 tool_handler=OfferManagementToolHandler())


###############################################################################
## Main program execution
###############################################################################

def main():
    ai = ai_connector()
    ai.tool_handler.load_db("./resources/db1.json")
    run(ai)
    db = ai.tool_handler.db
    print(json.dumps(db, indent=4))


if __name__ == '__main__':
    main()
