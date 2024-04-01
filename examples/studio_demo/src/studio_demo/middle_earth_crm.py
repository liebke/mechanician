import json
import os

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
