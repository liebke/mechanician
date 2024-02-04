from mechanician.ux.cli import run
from dotenv import load_dotenv
from mechanician_openai.chat_ai_connector import OpenAIChatAIConnector
from mechanician_arangodb.doc_mgr_instructions import instructions

from mechanician_arangodb.document_tool_handler import DocumentManagerToolHandler
from mechanician_arangodb.doc_mgr_tool_schema import tool_schemas

from arango import ArangoClient

import os


instructions = f"""
You are an Document Manager Assistant with access to tools that can help you manage JSON documents.

You can create 
* JSON Document Databases, 
* and within those databases you can create Collections that will contain JSON Documents.
* You can create JSON Documents.
* You can create special collections containing Links which are used to link documents together.
* You can Link Documents together, using links that you create in the special Link Collections.
"""

###############################################################################
## AI Connector
###############################################################################

def ai_connector(tool_handler):

    # with open("./instructions.md", 'r') as file:
    #     instructions = file.read()

   
    return OpenAIChatAIConnector(instructions=instructions, 
                                 tool_schemas=tool_schemas, 
                                 tool_handler=tool_handler)


###############################################################################
## Main program execution
###############################################################################

def main():
    try: 
        load_dotenv()
        # Initialize the ArangoDB client
        arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
        # Initialize the model
        doc_tool_handler = DocumentManagerToolHandler(arango_client, 
                                                    database_name="test_db")
        ai = ai_connector(doc_tool_handler)
        run(ai)
        
    finally:
        doc_tool_handler.doc_mgr.delete_database("test_db")

if __name__ == '__main__':
    main()
