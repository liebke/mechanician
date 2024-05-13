from mechanician_openai import OpenAIChatConnectorProvisioner
from mechanician_studio import AIStudio
from mechanician.ai_tools.notepads import UserNotepadAIToolsProvisioner
from mechanician_arangodb.notepad_store import ArangoNotepadStoreProvisioner
from arango import ArangoClient
from mechanician import AIProvisioner
from mechanician.tools import PromptToolsProvisioner, PromptPreprocessorProvisioner
from mechanician_chroma import UserAIChromaConnectorProvisioner
from studio_demo.tmdb_ai_tools import TMDbAIToolsProvisioner
from studio_demo.crm_connector import CRMConnectorProvisioner
import uvicorn
import os
import logging
from dotenv import load_dotenv
from mechanician_chroma.chroma_ai_tools import ChromaAIToolsProvisioner
from mechanician_chroma.chroma_resource_handlers import PDFResourceUploadedEventHandler, ChromaPDFResourceUploadedEventHandler
from mechanician_studio.resource_handlers import TextResourceUploadedEventHandler

from studio_demo.product_catalog import ProductCatalogConnectorProvisioner, CatalogAIToolsProvisioner

from .web_form_analyzer import WebFormAnalyzerConnectorProvisioner

from pprint import pprint
import traceback

logger = logging.getLogger(__name__)





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
     
    # chroma_connector = ChromaConnectorProvisioner(collection_name="maritime_contracts",)
    chroma_connector = UserAIChromaConnectorProvisioner()
    chroma_tools = PromptToolsProvisioner(resource_connector_provisioner = chroma_connector,
                                          prompt_template_directory="./templates",
                                          prompt_instructions_directory="./src/instructions",
                                          prompt_tool_instructions_file_name="rag_prompt_tool_instructions.json") 
    
    preprocessors = {"Contracts Copilot AI": PromptPreprocessorProvisioner(resource_connector_provisioner = chroma_connector,
                                                                           prompt_template_directory="./templates",
                                                                           prompt_template_name="chroma_query.md")} 
    
    # event_handlers = {"resource_uploaded": [PDFResourceUploadedEventHandler(), TextResourceUploadedEventHandler()]}
    event_handlers = {"resource_uploaded": [ChromaPDFResourceUploadedEventHandler(), TextResourceUploadedEventHandler()]}
    

    ## PRODUCT CATALOG
    catalog_connector = ProductCatalogConnectorProvisioner(data_directory="./data",
                                                               product_catalog_filename="product_catalog.csv")

    catalog_tools = PromptToolsProvisioner(resource_connector_provisioner = catalog_connector,
                                           prompt_template_directory="./templates",
                                           prompt_instructions_directory="./src/instructions",
                                           prompt_tool_instructions_file_name="catalog_prompt_tool_instructions.json")
    
    catalog_ai_tools = CatalogAIToolsProvisioner(catalog_connector_provisioner=catalog_connector,
                                                 tool_instructions_file_name="catalog_ai_tool_instructions.json",
                                                 ai_instructions_file_name="catalog_ai_instructions.md",
                                                 instruction_set_directory="./src/instructions")

    catalog_ai = AIProvisioner(ai_connector_provisioner=ai_connector,
                               name = "Offer Managment Copilot",
                               ai_tools_provisioners = [catalog_ai_tools])
    
    ## END PRODUCT CATALOG

    ## WEB FORM ANALYZER

    web_form_analyzer_connector = WebFormAnalyzerConnectorProvisioner()
    web_form_analyzer_tools = PromptToolsProvisioner(resource_connector_provisioner = web_form_analyzer_connector,
                                                     prompt_template_directory="./templates",
                                                     prompt_instructions_directory="./src/instructions",
                                                     prompt_tool_instructions_file_name="web_form_analyzer_instructions.json")

    ## END WEB FORM ANALYZER

    # Set up the Mechanician AI Studio
    return AIStudio(ai_provisioners=[notepad_only_ai, tmdb_ai, contract_ai, catalog_ai],
                    prompt_tools_provisioners=[crm_tools, chroma_tools, catalog_tools, web_form_analyzer_tools],
                    event_handlers=event_handlers,
                    prompt_preprocessor_provisioners=preprocessors)


def run_studio():
    load_dotenv()
    uvicorn.run(init_studio(), 
                host="0.0.0.0", 
                port=8000,
                ssl_keyfile=os.getenv("SSL_KEYFILE"),
                ssl_certfile=os.getenv("SSL_CERTFILE"))


def test_catalog_connector():
    try:
        catalog_connector = ProductCatalogConnectorProvisioner(data_directory="./data",
                                                               product_catalog_filename="product_catalog.csv")
        connector = catalog_connector.create_connector()
        pprint(connector.list_products_by_brand({"brand": "alditalk"}))

        catalog_tools = PromptToolsProvisioner(resource_connector_provisioner = catalog_connector,
                                               prompt_template_directory="./templates",
                                               prompt_instructions_directory="./src/instructions",
                                               prompt_tool_instructions_file_name="catalog_prompt_tool_instructions.json") 

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error: {e}")



if __name__ == '__main__':
    run_studio()
    # test_catalog_connector()





