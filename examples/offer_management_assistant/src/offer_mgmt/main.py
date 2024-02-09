from mechanician.ux.cli import run
from dotenv import load_dotenv
# from mechanician.apis.openai.assistants_service_connector import OpenAIAssistantServiceConnector
from mechanician_openai.chat_ai_connector import OpenAIChatAIConnector

# from offer_mgmt.tools import OfferManagementToolHandler
from offer_mgmt.graphdb_tools import OfferManagementToolHandler
from offer_mgmt.tool_schemas import tool_schemas
import json
import logging

logger = logging.getLogger(__name__)

DELETE_DB_ON_EXIT = False

###############################################################################
## AI Connector
###############################################################################

def ai_connector(database_name):
    # Load environment variables from a .env file
    load_dotenv()

    with open("./instructions.md", 'r') as file:
        instructions = file.read()

    # Initialize the model
    # model = OpenAIAssistant(tool_schemas=tool_schemas, function_handler=call_function)
    return OpenAIChatAIConnector(system_instructions=instructions, 
                                 tool_instructions=tool_schemas, 
                                 tool_handler=OfferManagementToolHandler(database_name))


###############################################################################
## Main program execution
###############################################################################

def main():
    try:
        database_name="offer_mgmt_test_db"
        ai = ai_connector(database_name)
        # ai.tool_handler.load_db("./resources/db1.json")
        run(ai)
        # db = ai.tool_handler.db
        # print(json.dumps(db, indent=4))
    finally:
        if DELETE_DB_ON_EXIT:
            ai.tools.doc_mgr.delete_database(database_name)


if __name__ == '__main__':
    main()
