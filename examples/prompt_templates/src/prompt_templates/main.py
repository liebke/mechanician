from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector
import os
import logging
from dotenv import load_dotenv
import traceback

import json
from mechanician.prompting.templates import PromptTemplate
from mechanician.prompting.tools import PromptTools
from pprint import pprint

logger = logging.getLogger(__name__)

###############################################################################
## INIT AI
###############################################################################

def init_ai():

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")
    ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)
    ai = TAGAI(ai_connector=ai_connector, 
               name="MiddleEartch CRM AI")
    return ai


###############################################################################
## Main program execution
###############################################################################

def main():
    ai = None
    try: 
        load_dotenv()
        ai = init_ai()
        prompt_tools = MiddleEarthCRMPromptTools()
        shell.run(ai, prompt_tools=prompt_tools)

    except Exception as e:
        logger.error(e)
        traceback.print_exc()
    finally:
        if ai:
            ai.save_tuning_session()


class MiddleEarthCRM():

    def __init__(self, crm_data_filename="crm_data.json"):
        self.crm_data_filename = crm_data_filename
        self.crm_data = self.load_crm_data()


    def load_crm_data(self):
        with open(self.crm_data_filename, 'r') as file:
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


    def list_products(self):
        return {"product": self.crm_data.get("products", [])}

    

class MiddleEarthCRMPromptTools(PromptTools):
    def __init__(self, prompt_template_directory="./templates"):
        self.prompt_template_directory = prompt_template_directory
        self.crm = MiddleEarthCRM()


    def event_invite(self, params):
        prompt_template_name = params.get("template")
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
        prompt_template_name = params.get("template")

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
        prompt_template_name = params.get("template")

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
    

if __name__ == '__main__':
    main()
