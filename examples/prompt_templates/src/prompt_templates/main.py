from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector, OpenAIChatConnectorFactory
import os
import logging
from dotenv import load_dotenv
import traceback

import json
from mechanician.templates import PromptTemplate
from mechanician.tools import PromptTools, MechanicianToolsFactory
from pprint import pprint

from mechanician_ui import MechanicianWebApp
import uvicorn

from mechanician.ai_tools.notepads import UserNotepadAIToolsFactory
from mechanician_arangodb.notepad_store import ArangoNotepadStoreFactory
from arango import ArangoClient


logger = logging.getLogger(__name__)


###############################################################################
## MiddleEarthCRM
###############################################################################

class MiddleEarthCRM():

    def __init__(self, 
                 crm_data_filename="crm_data.json",
                 crm_data_directory="./data"):
        self.crm_data_filename = crm_data_filename
        self.crm_data_directory = crm_data_directory
        self.crm_data_path = os.path.join(crm_data_directory, crm_data_filename)
        self.crm_data = self.load_crm_data()


    def load_crm_data(self):
        with open(self.crm_data_path, 'r') as file:
            return json.loads(file.read())


    def lookup_contact_by_name(self, contact_name):
        contact_name = contact_name.lower().strip()
        for contact in self.crm_data.get("contacts", []):
            first_name = contact.get("name", "").get("first", "").lower().strip()
            last_name = contact.get("name", "").get("last", "").lower().strip()
            full_name = f"{first_name} {last_name}"
            if contact_name == first_name or contact_name == last_name or contact_name == full_name:
                return contact
        print("Contact not found.")
        return None
    

    def lookup_event_by_title(self, event_title):
        event_query = event_title.lower().strip()
        for event in self.crm_data.get("events", []):
            event_title = event.get("title", "").lower().strip()
            if event_query in event_title:
                return event
        print("Event not found.")
        return None
    

    def list_customer_inventory(self, customer_id):
        customer_inventories = self.crm_data.get("customer_inventories", [])
        for inventory in customer_inventories:
            if inventory.get("customer_id") == customer_id:
                print(f"customer_id: {customer_id} == {inventory.get('customer_id')}")
                return inventory
        return {}
    

    def lookup_customer_case(self, case_id):
        customer_cases = self.crm_data.get("customer_cases", [])
        for case in customer_cases:
            if case.get("case_id") == case_id:
                return case
        return {}
    
    def lookup_customer_cases_by_name(self, customer_name):
        customer_cases = self.crm_data.get("customer_cases", [])
        cases = []
        for case in customer_cases:
            if case.get("customer_name") == customer_name:
                cases.append(case)
        return cases


    def list_products(self):
        return {"product": self.crm_data.get("products", [])}

    

###############################################################################
## MiddleEarthCRMPromptToolsFactory
###############################################################################
    
class MiddleEarthCRMPromptToolsFactory(MechanicianToolsFactory):
        def __init__(self, 
                    prompt_template_directory="./templates",
                    crm_data_directory="./data"):
            self.prompt_template_directory = prompt_template_directory
            self.crm = MiddleEarthCRM(crm_data_directory=crm_data_directory)
    

        def create_tools(self, context: dict={}):
            print(f"MiddleEarthCRMPromptToolsFactory.create_tools called with context: {context}")
            return MiddleEarthCRMPromptTools(prompt_template_directory=self.prompt_template_directory,
                                             crm_data_directory=context.get("crm_data_directory", "./data"))


###############################################################################
## MiddleEarthCRMPromptTools
###############################################################################

class MiddleEarthCRMPromptTools(PromptTools):

    def __init__(self, 
                 prompt_template_directory="./templates",
                 crm_data_directory="./data"):
        self.prompt_template_directory = prompt_template_directory
        self.crm = MiddleEarthCRM(crm_data_directory=crm_data_directory)


    def get_prompt_template(self, prompt_template_name:str):
        print(f"MiddleEarthCRMPromptTools.get_prompt_template called with prompt_template_name: {prompt_template_name}")
        template = PromptTemplate(template_filename=prompt_template_name, 
                                  template_directory=self.prompt_template_directory)
        print(f"MiddleEarthCRMPromptTools.get_prompt_template: template.template_str: {template.template_str}")
        return template.template_str    
    
    def save_prompt_template(self, prompt_template_name:str, prompt_template:str):
        pass

    def event_invite(self, params):
        prompt_template_name = params.get("template") or "event_invite.md"
        event_title = params.get("event")
        contact_name = params.get("contact")
        contact = self.crm.lookup_contact_by_name(contact_name)
        if contact is None:
            return f"Contact not found: {contact_name}"
        
        event = self.crm.lookup_event_by_title(event_title)
        if event is None:
            return f"Event not found: {event_title}"
        
        print("\n\n")
        print(f"Event: {event}")
        print(f"Contact: {contact}")
        print("\n\n")

        prompt_template = PromptTemplate(template_filename=prompt_template_name, 
                                         template_directory=self.prompt_template_directory)
        prompt_template.add_resource("contact", contact)
        prompt_template.add_resource("event", event)
        return prompt_template.generate_prompt()
    

    def sales_email(self, params):
        prompt_template_name = params.get("template") or "sales_email.md"

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
        
        print("\n\n")
        print(f"Sender: {sender}")
        print(f"Contact: {contact}")
        print("\n\n")

        prompt_template = PromptTemplate(template_filename=prompt_template_name, 
                                         template_directory=self.prompt_template_directory)
        prompt_template.add_resource("contact", contact)
        prompt_template.add_resource("sender", sender)
        prompt_template.add_resource("products", products)
        prompt_template.add_resource("customer_inventory", customer_inventory)
        generated_prompt = prompt_template.generate_prompt()
        return generated_prompt
    


    def customer_service_message(self, params):
        prompt_template_name = params.get("template") or "customer_service_message.md"

        care_agent_name = params.get("care_agent")
        care_agent = self.crm.lookup_contact_by_name(care_agent_name)
        if care_agent is None:
            return f"care_agent not found: {care_agent}"
        care_agent["company"] = "Barad-dûr Jewelery Supply"

        case_id = params.get("case_id")
        case = self.crm.lookup_customer_case(case_id)
        if case is None:
            return f"Contact not found: {case_id}"
        
        print("\n\n")
        print(f"Care Agent: {care_agent}")
        print(f"Case: {case}")
        print("\n\n")

        prompt_template = PromptTemplate(template_filename=prompt_template_name, 
                                         template_directory=self.prompt_template_directory)
        prompt_template.add_resource("customer_care_agent", care_agent)
        prompt_template.add_resource("customer_case", case)
        generated_prompt = prompt_template.generate_prompt()
        return generated_prompt
    

    def product_newsletter(self, params):
        prompt_template_name = params.get("template") or "product_newsletter.md"
        company_name = params.get("company")
        company = {"name": company_name}

        products = self.crm.list_products()
        
        prompt_template = PromptTemplate(template_filename=prompt_template_name, 
                                         template_directory=self.prompt_template_directory)
        prompt_template.add_resource("company", company)
        prompt_template.add_resource("products", products)
        generated_prompt = prompt_template.generate_prompt()
        return generated_prompt
    

    def customer_summarization(self, params):
        prompt_template_name = params.get("template") or "customer_summarization.md"

        customer_name = params.get("customer")
        customer = self.crm.lookup_contact_by_name(customer_name)
        if customer is None:
            return f"Contact not found: {customer_name}"
        
        customer_inventory = self.crm.list_customer_inventory(customer_name)
        cases = self.crm.lookup_customer_cases_by_name(customer_name)

        prompt_template = PromptTemplate(template_filename=prompt_template_name, 
                                         template_directory=self.prompt_template_directory)
        prompt_template.add_resource("customer", customer)
        prompt_template.add_resource("cases", cases)
        prompt_template.add_resource("customer_inventory", customer_inventory)
        generated_prompt = prompt_template.generate_prompt()
        return generated_prompt
    


###############################################################################
## INIT AI
###############################################################################

def init_ai():

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")
    ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)

    # ArangoDB notepad store
    database_name="test_notepad_db"
    notepad_collection_name="notepads"
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    arango_notepad_store_factory = ArangoNotepadStoreFactory(arango_client=arango_client, 
                                                             database_name=database_name,
                                                             notepad_collection_name=notepad_collection_name,
                                                             db_username=os.getenv("ARANGO_USERNAME"),
                                                             db_password=os.getenv("ARANGO_PASSWORD"))
    arango_notepad_tools_factory = UserNotepadAIToolsFactory(notepad_store_factory=arango_notepad_store_factory)
    # END ArangoDB notepad store

    ai = TAGAI(ai_connector=ai_connector, 
               name="MiddleEarth CRM AI",
               ai_tools=[arango_notepad_tools_factory])
    return ai


###############################################################################
## Main program execution
###############################################################################

def main():
    ai = None
    try: 
        load_dotenv()
        ai = init_ai()
        print(f"main: Current working directory: {os.getcwd()}")
        prompt_tools = MiddleEarthCRMPromptTools(crm_data_directory="./data")
        shell.run(ai, prompt_tools=prompt_tools)

    except Exception as e:
        logger.error(e)
        traceback.print_exc()
    finally:
        if ai:
            ai.save_tuning_session()



###############################################################################
## Main application initialization
###############################################################################
    
def init_app():
    # ArangoDB notepad store
    database_name="test_notepad_db"
    notepad_collection_name="notepads"
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    arango_notepad_store_factory = ArangoNotepadStoreFactory(arango_client=arango_client, 
                                                            database_name=database_name,
                                                            notepad_collection_name=notepad_collection_name,
                                                            db_username=os.getenv("ARANGO_USERNAME"),
                                                            db_password=os.getenv("ARANGO_PASSWORD"))
    arango_notepad_tools_factory = UserNotepadAIToolsFactory(notepad_store_factory=arango_notepad_store_factory)
    # END ArangoDB notepad store

    ai_connector_factory = OpenAIChatConnectorFactory(api_key=os.getenv("OPENAI_API_KEY"), 
                                                      model_name=os.getenv("OPENAI_MODEL_NAME"))
    prompt_tools_factory = MiddleEarthCRMPromptToolsFactory(crm_data_directory="./data")    
    return MechanicianWebApp(ai_connector_factory=ai_connector_factory,
                             ai_tools_factory=[arango_notepad_tools_factory],
                             prompt_tools_factory=[prompt_tools_factory],
                             name="MiddleEarth CRM AI")

    



def run_app():
    load_dotenv()
    uvicorn.run(init_app(), 
                host="0.0.0.0", 
                port=8000,
                ssl_keyfile=os.getenv("SSL_KEYFILE"),
                ssl_certfile=os.getenv("SSL_CERTFILE"))


if __name__ == '__main__':
    # main()
    run_app()





