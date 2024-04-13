from mechanician_openai import OpenAIChatConnectorProvisioner
from mechanician_studio import AIStudio
from mechanician.ai_tools.notepads import UserNotepadAIToolsProvisioner
from mechanician_arangodb.notepad_store import ArangoNotepadStoreProvisioner
from arango import ArangoClient
from mechanician import AIProvisioner
from mechanician.tools import PromptToolsProvisioner
from mechanician_chroma import ChromaConnectorProvisioner
from studio_demo.tmdb_ai_tools import TMDbAIToolsProvisioner
from studio_demo.crm_connector import CRMConnectorProvisioner
import uvicorn
import os
import logging
from dotenv import load_dotenv
from mechanician_studio.events import EventHandler

from mechanician_chroma.chroma_ai_tools import ChromaAIToolsProvisioner



logger = logging.getLogger(__name__)


class InfoEventHandler(EventHandler):
    async def handle(self, event):
        print(f"RESOURCE UPLOADED HANDLER 1: {event['resource_entry']}")


class InfoEventHandler2(EventHandler):
    async def handle(self, event):
        print(f"RESOURCE UPLOADED HANDLER 2: {event['resource_entry']}")

class ErrorEventHandler(EventHandler):
    async def handle(self, event):
        print(f"ERROR: {event['message']}")


###############################################################################
## Main application initialization
###############################################################################
    
def init_studio():

    # Set up UserNotepad AI Tools Provisioner
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    notepad_store = ArangoNotepadStoreProvisioner(arango_client=arango_client, 
                                                  database_name="test_notepad_db",
                                                  notepad_collection_name="notepads",
                                                  db_username=os.getenv("ARANGO_USERNAME"),
                                                  db_password=os.getenv("ARANGO_PASSWORD"))
    notepad_tools = UserNotepadAIToolsProvisioner(notepad_store_provisioner=notepad_store)

    tmdb_tools = TMDbAIToolsProvisioner(api_key=os.getenv("TMDB_READ_ACCESS_TOKEN"),
                                        instruction_set_directory="./src/instructions",
                                        ai_instructions_file_name="tmdb_ai_instructions.md",
                                        tool_instructions_file_name="tmdb_ai_tool_instructions.json")
    
    contract_tools = ChromaAIToolsProvisioner(collection_name="maritime_contracts",
                                              data_path="./data/chromadb",
                                              instruction_set_directory="./src/instructions",
                                              ai_instructions_file_name="contracts_ai_instructions.md",
                                              tool_instructions_file_name="contracts_ai_tool_instructions.json")

    # Set up the AI provisioner
    ai_connector = OpenAIChatConnectorProvisioner(api_key=os.getenv("OPENAI_API_KEY"), 
                                                  model_name=os.getenv("OPENAI_MODEL_NAME"))
    
    notepad_only_ai = AIProvisioner(ai_connector_provisioner=ai_connector,
                                    name = "Notepad Only AI",
                                    ai_tools_provisioners = [notepad_tools])
    
    tmdb_ai = AIProvisioner(ai_connector_provisioner=ai_connector,
                            name = "TMDB AI",
                            ai_tools_provisioners = [notepad_tools,
                                                     tmdb_tools])
    
    contract_ai = AIProvisioner(ai_connector_provisioner=ai_connector,
                                name = "Contracts Copilot AI",
                                ai_tools_provisioners = [contract_tools])
    
    # Set up the Prompt Tools provisioners
    crm_connector = CRMConnectorProvisioner(crm_data_directory="./data")
    crm_tools = PromptToolsProvisioner(resource_connector_provisioner = crm_connector,
                                       prompt_template_directory="./templates",
                                       prompt_instructions_directory="./src/instructions",
                                       prompt_tool_instructions_file_name="crm_prompt_tool_instructions.json") 
     
    chroma_connector = ChromaConnectorProvisioner(collection_name="maritime_contracts",)
    chroma_tools = PromptToolsProvisioner(resource_connector_provisioner = chroma_connector,
                                          prompt_template_directory="./templates",
                                          prompt_instructions_directory="./src/instructions",
                                          prompt_tool_instructions_file_name="rag_prompt_tool_instructions.json") 
    
    event_handlers = {"resource_uploaded": [InfoEventHandler(), InfoEventHandler2()], 
                      "error": [ErrorEventHandler()]}
    # Set up the Mechanician AI Studio
    return AIStudio(ai_provisioners=[notepad_only_ai, tmdb_ai, contract_ai],
                    prompt_tools_provisioners=[crm_tools, chroma_tools],
                    event_handlers=event_handlers)


def run_studio():
    load_dotenv()
    uvicorn.run(init_studio(), 
                host="0.0.0.0", 
                port=8000,
                ssl_keyfile=os.getenv("SSL_KEYFILE"),
                ssl_certfile=os.getenv("SSL_CERTFILE"))


if __name__ == '__main__':
    run_studio()





