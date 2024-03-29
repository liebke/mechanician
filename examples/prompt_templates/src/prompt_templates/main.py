from mechanician_openai import OpenAIChatConnectorProvisioner
import os
import logging
from dotenv import load_dotenv
from mechanician.resources import ResourceConnector, ResourceConnectorProvisioner
from mechanician_ui import MechanicianWebApp
import uvicorn
from mechanician.ai_tools.notepads import UserNotepadAIToolsProvisioner
from mechanician_arangodb.notepad_store import ArangoNotepadStoreProvisioner
from arango import ArangoClient
from .middle_earth_crm import MiddleEarthCRM

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
## Main application initialization
###############################################################################
    
def init_app():
    database_name="test_notepad_db"
    notepad_collection_name="notepads"
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    notepad_store_provisioner = ArangoNotepadStoreProvisioner(arango_client=arango_client, 
                                                              database_name=database_name,
                                                              notepad_collection_name=notepad_collection_name,
                                                              db_username=os.getenv("ARANGO_USERNAME"),
                                                              db_password=os.getenv("ARANGO_PASSWORD"))
    notepad_tools_provisioner = UserNotepadAIToolsProvisioner(notepad_store_provisioner=notepad_store_provisioner)
    ai_connector_provisioner = OpenAIChatConnectorProvisioner(api_key=os.getenv("OPENAI_API_KEY"), 
                                                              model_name=os.getenv("OPENAI_MODEL_NAME"))
    crm_connector_provisioner = CRMConnectorProvisioner(crm_data_directory="./data")

    return MechanicianWebApp(ai_connector_provisioner=ai_connector_provisioner,
                             ai_tools_provisioner=[notepad_tools_provisioner],
                             resource_connector_provisioner=crm_connector_provisioner,
                             prompt_template_directory="./templates",
                             name="MiddleEarth CRM AI")


def run_app():
    load_dotenv()
    uvicorn.run(init_app(), 
                host="0.0.0.0", 
                port=8000,
                ssl_keyfile=os.getenv("SSL_KEYFILE"),
                ssl_certfile=os.getenv("SSL_CERTFILE"))


if __name__ == '__main__':
    run_app()





