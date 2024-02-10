from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector, OpenAIAssistantsConnector
from mechanician_arangodb import DocumentManagerAITools, tool_instructions
from revised_instructions import ai_instructions
from arango import ArangoClient
import os
import logging
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

###############################################################################
## AI Connector
###############################################################################

def init_ai(database_name="test_db"):
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    doc_tools = DocumentManagerAITools(arango_client, database_name=database_name)
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")

    if os.getenv("USE_OPENAI_ASSISTANTS_API", "False") == "True":
        ai_connector = OpenAIAssistantsConnector(api_key=api_key, model_name=model_name)
    else:
        ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)

    ai = TAGAI(ai_connector=ai_connector, 
               ai_instructions=ai_instructions, 
               tool_instructions=tool_instructions,
               tools=doc_tools,
               name="Movie Document Manager AI")
    return ai


###############################################################################
## Main program execution
###############################################################################

def main():
    try: 
        load_dotenv()
        database_name = "test_db"
        ai = init_ai(database_name)
        shell.run(ai)
        
    finally:
        ai.tools.doc_mgr.delete_database(database_name)

if __name__ == '__main__':
    main()
