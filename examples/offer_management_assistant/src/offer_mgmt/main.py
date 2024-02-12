from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector

from offer_mgmt.offer_mgmt_ai_tools import OfferManagementAITools
import logging
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

DELETE_DB_ON_EXIT = False

###############################################################################
## AI Connector
###############################################################################

def init_ai(database_name):
    # Load environment variables from a .env file
    load_dotenv()

    ai_connector = OpenAIChatConnector(api_key=os.getenv("OPENAI_API_KEY"), 
                                       model_name=os.getenv("OPENAI_MODEL_NAME"))
    return TAGAI(ai_connector,
                 instruction_set_directory="./instructions",
                 tools=OfferManagementAITools(database_name))


###############################################################################
## Main program execution
###############################################################################

def main():
    try:
        database_name="offer_mgmt_test_db"
        ai = init_ai(database_name)
        shell.run(ai)
    finally:
        if DELETE_DB_ON_EXIT:
            ai.tools.doc_mgr.delete_database(database_name)


if __name__ == '__main__':
    main()
