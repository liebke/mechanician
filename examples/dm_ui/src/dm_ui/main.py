from mechanician_openai import OpenAIChatConnectorProvisioner
import os
import logging
from dotenv import load_dotenv
from mechanician.resources import ResourceConnector, ResourceConnectorProvisioner
from mechanician.tools import PromptToolsProvisioner
from mechanician_ui import MechanicianWebApp
import uvicorn
from mechanician.ai_tools.notepads import UserNotepadAIToolsProvisioner
from mechanician_arangodb.notepad_store import ArangoNotepadStoreProvisioner
from arango import ArangoClient
from .middle_earth_crm import MiddleEarthCRM
from pprint import pprint
from mechanician.ai import AIProvisioner

import chromadb
from chromadb.utils import embedding_functions

from dm_ui.tmdb_ai_tools import TMDbAIToolsProvisioner


logger = logging.getLogger(__name__)

###############################################################################
## MiddleEarthCRMConnectorProvisioner
###############################################################################
    
class CRMConnectorProvisioner(ResourceConnectorProvisioner):
        
        def __init__(self, crm_data_directory="./data"):
            self.crm_data_directory = crm_data_directory
    

        def create_connector(self, context: dict={}):
            # Use the context to control access to resources provided by the connector.
            # ...
            return CRMConnector(crm_data_directory=self.crm_data_directory)


###############################################################################
## MiddleEarthCRMConnector
###############################################################################

class CRMConnector(ResourceConnector):

    def __init__(self, crm_data_directory="./data"):
        self.crm = MiddleEarthCRM(crm_data_directory=crm_data_directory)


    def event_invite(self, params):
        event_title = params.get("event")
        contact_name = params.get("contact")
        contact = self.crm.lookup_contact_by_name(contact_name)
        if contact is None:
            return f"Contact not found: {contact_name}"
        
        event = self.crm.lookup_event_by_title(event_title)
        if event is None:
            return f"Event not found: {event_title}"
        
        return [{"name": "contact", "data": contact}, 
                {"name": "event", "data": event}]


    def sales_email(self, params):
        sender_name = params.get("sender")
        sender = self.crm.lookup_contact_by_name(sender_name)
        if sender is None:
            return f"Sender not found: {sender_name}"
        
        sender["company"] = "Middle Earth Merchantile Co."
        contact_name = params.get("contact")
        contact = self.crm.lookup_contact_by_name(contact_name)
        if contact is None:
            return f"Contact not found: {contact_name}"
        
        products = self.crm.list_products()
        customer_inventory = self.crm.list_customer_inventory(contact_name)
        return [{"name": "contact", "data": contact}, 
                {"name": "sender", "data": sender}, 
                {"name": "products", "data": products}, 
                {"name": "customer_inventory", "data": customer_inventory}]


    def customer_service_message(self, params):
        care_agent_name = params.get("care_agent")
        care_agent = self.crm.lookup_contact_by_name(care_agent_name)
        if care_agent is None:
            return f"care_agent not found: {care_agent}"
        
        care_agent["company"] = "Barad-dûr Jewelery Supply"
        case_id = params.get("case_id")
        case = self.crm.lookup_customer_case(case_id)
        if case is None:
            return f"Contact not found: {case_id}"
        
        return [{"name": "customer_care_agent", "data": care_agent}, 
                {"name": "customer_case", "data": case}]
    

    def product_newsletter(self, params):
        company_name = params.get("company")
        company = {"name": company_name}
        products = self.crm.list_products()
        return [{"name": "company", "data": company}, 
                {"name": "products", "data": products}]
        

    def customer_summarization(self, params):
        customer_name = params.get("customer")
        customer = self.crm.lookup_contact_by_name(customer_name)
        if customer is None:
            return f"Contact not found: {customer_name}"
        
        customer_inventory = self.crm.list_customer_inventory(customer_name)
        cases = self.crm.lookup_customer_cases_by_name(customer_name)
        return [{"name": "customer", "data": customer}, 
                {"name": "cases", "data": cases}, 
                {"name": "customer_inventory", "data": customer_inventory}]


###############################################################################
## ChromaConnectorProvisioner
###############################################################################
    
class ChromaConnectorProvisioner(ResourceConnectorProvisioner):
        
        def __init__(self, collection_name="wikipedia_collection"):
            self.collection_name = collection_name
    

        def create_connector(self, context: dict={}):
            # Use the context to control access to resources provided by the connector.
            # ...
            return ChromaConnector(collection_name=self.collection_name)


###############################################################################
## ChromaConnector
###############################################################################

# docker run -p 8080:8000 chromadb/chroma
class ChromaConnector(ResourceConnector):
    def __init__(self, collection_name, data_path="./data/chromadb"):
        self.collection_name = collection_name
        self.data_path = data_path
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        

    def get_collection(self):
        # chroma_client = chromadb.PersistentClient(path=self.data_path)
        chroma_client = chromadb.HttpClient(host='127.0.0.1', port=8080)
        return chroma_client.get_or_create_collection(name=self.collection_name,
                                                      embedding_function=self.embedding_func,
                                                      metadata={"hnsw:space": "cosine"})


    def rag_query(self, params):
        question = params.get("question")
        results = self.get_collection().query(query_texts=[question],
                                              n_results=20)
        documents = results.get("documents")[0]
        metadatas = results.get("metadatas")[0]
        data = []
        for i in range(len(documents)):
            data.append({"source": metadatas[i].get("source"), "text": documents[i]})

        return [{"name": "question", "data": question},
                {"name": "context", "data": data}]
    



###############################################################################
## Main application initialization
###############################################################################
    
def init_app():

    # Set up UserNotepad AI Tools Provisioner
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    notepad_store_provisioner = ArangoNotepadStoreProvisioner(arango_client=arango_client, 
                                                              database_name="test_notepad_db",
                                                              notepad_collection_name="notepads",
                                                              db_username=os.getenv("ARANGO_USERNAME"),
                                                              db_password=os.getenv("ARANGO_PASSWORD"))
    notepad_tools_provisioner = UserNotepadAIToolsProvisioner(notepad_store_provisioner=notepad_store_provisioner)

    tmdb_tools_provisioner = TMDbAIToolsProvisioner(api_key=os.getenv("TMDB_READ_ACCESS_TOKEN"))

    # Set up the AI provisioner
    ai_connector_provisioner = OpenAIChatConnectorProvisioner(api_key=os.getenv("OPENAI_API_KEY"), 
                                                              model_name=os.getenv("OPENAI_MODEL_NAME"))
    ai_provisioner = AIProvisioner(ai_connector_provisioner=ai_connector_provisioner,
                                   name = "MiddleEarth CRM AI",
                                   ai_tools_provisioners = [notepad_tools_provisioner,
                                                            tmdb_tools_provisioner])
    
    # Set up the Prompt Tools provisioners
    crm_connector_provisioner = CRMConnectorProvisioner(crm_data_directory="./data")
    crm_tools_provisioner = PromptToolsProvisioner(resource_connector_provisioner = crm_connector_provisioner,
                                                   prompt_template_directory="./templates",
                                                   prompt_instructions_directory="./src/instructions",
                                                   prompt_tool_instruction_file_name="crm_prompt_tool_instructions.json") 
     
    chroma_connector_provisioner = ChromaConnectorProvisioner(collection_name="wikipedia_collection")
    chroma_tools_provisioner = PromptToolsProvisioner(resource_connector_provisioner = chroma_connector_provisioner,
                                                      prompt_template_directory="./templates",
                                                      prompt_instructions_directory="./src/instructions",
                                                      prompt_tool_instruction_file_name="rag_prompt_tool_instructions.json") 
    
    # Set up the Mechanician Web App
    return MechanicianWebApp(ai_provisioner=ai_provisioner,
                             prompt_tools_provisioners=[crm_tools_provisioner, 
                                                        chroma_tools_provisioner])


def run_app():
    load_dotenv()
    uvicorn.run(init_app(), 
                host="0.0.0.0", 
                port=8000,
                ssl_keyfile=os.getenv("SSL_KEYFILE"),
                ssl_certfile=os.getenv("SSL_CERTFILE"))


if __name__ == '__main__':
    run_app()





