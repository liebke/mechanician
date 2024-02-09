from mechanician.ux.cli import run
from dotenv import load_dotenv
from mechanician.tag_ai import TAGAI
from mechanician_openai.chat_ai_connector import OpenAIChatAIConnector
from revised_instructions import system_instructions
from mechanician_arangodb.document_ai_tools import DocumentManagerAITools
from mechanician_arangodb.doc_mgr_tool_instructions import tool_instructions
from arango import ArangoClient
import os
import logging
# FOR TESTING
from mechanician_openai.assistants_ai_connector import OpenAIAssistantAIConnector


logger = logging.getLogger(__name__)

###############################################################################
## AI Connector
###############################################################################

def init_ai(database_name="test_db"):
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    doc_tools = DocumentManagerAITools(arango_client, 
                                       database_name=database_name)
    
    if os.getenv("USE_ASSISTANT_API", "False") == "True":
        ai_connector = OpenAIAssistantAIConnector()
    else:
        ai_connector = OpenAIChatAIConnector()

    ai = TAGAI(ai_connector=ai_connector, 
               system_instructions=system_instructions, 
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
        run(ai)
        
    finally:
        ai.tools.doc_mgr.delete_database(database_name)

if __name__ == '__main__':
    main()
