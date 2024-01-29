# Import Markdown and Console from rich library for pretty terminal outputs
from mechanician.ux.util import print_markdown
from mechanician.tool_handlers import ToolHandler
# from rich.markdown import Markdown
from rich.console import Console
import json
from pprint import pprint

console = Console()

def print_output(function_name, input, output):
    # input_str = input
    try:
        input_str = json.dumps(input, indent=4)
    except json.JSONDecodeError:
        print(f"Invalid JSON input: {input}")
    
    output_str = json.dumps(output, indent=4)

    print('')
    print_markdown(console, "------------------")
    print_markdown(console, "## FUNCTION CALLED")
    print_markdown(console, f"* FUNCTION NAME: **{function_name}**")
    print_markdown(console, "## INPUT")
    print_markdown(console, f"```json \n {input_str}\n ```")
    print_markdown(console, "## OUTPUT")
    print_markdown(console, f"```json \n{output_str}\n ```")
    print_markdown(console, "------------------")
    print('')
    return


class OfferManagementToolHandler(ToolHandler):

    db = {}

    def __init__(self):
        self.db['product_offers'] = {}
        self.db['charges'] = {}
        self.db['parent_to_child_relationships'] = {}
        self.db['child_to_parent_relationships'] = {}
        self.db['product_to_charge_relationships'] = {}
        self.db['charge_to_product_relationships'] = {}


    def load_db(self, db_filename):
        with open(db_filename, 'r') as file:
            self.db = json.load(file)

        print(f"Loaded DB from {db_filename}")
        pprint(self.db)
        return


    def create_product_offer(self, product_offer):
        if product_offer is None:
            resp = "No Product Offer found in request body"
        else:
            business_id = product_offer.get("business_id")
            self.db['product_offers'][business_id] = product_offer
            resp = f"Product Offer created: {business_id}"
        print_output("create_product_offer", product_offer, resp)
        return resp


    def create_charge(self, charge):
        if charge is None:
            resp = "No Charge found in request body"
        else:
            charge_id = charge.get("charge_id")
            self.db['charges'][charge_id] = charge
            resp = f"Charge created: {charge_id}"
        print_output("create_charge", charge, resp)
        return resp


    def create_product_to_product_relationship(self, relationship):
        if relationship is None:
            resp = "No Product to Product relationship found in request body"
        else:
            parent = relationship.get("parent_product_offer")
            child = relationship.get("child_product_offer")
            if parent not in self.db['parent_to_child_relationships']:
                self.db['parent_to_child_relationships'][parent] = [child]
            else:
                self.db['parent_to_child_relationships'][parent].append(child)

            if child not in self.db['child_to_parent_relationships']:
                self.db['child_to_parent_relationships'][child] = [parent]
            else:
                self.db['child_to_parent_relationships'][child].append(parent)

            resp = f"Product to Product relationship created: {relationship}"
        print_output("create_product_to_product_relationship", relationship, resp)
        return resp


    def create_product_to_charge_relationship(self, relationship):
        if relationship is None:
            resp = "No Product to Charge relationship found in request body"
        else:
            product = relationship.get("product_id")
            charge = relationship.get("charge_id")
            if product not in self.db.get('product_to_charge_relationships'):
                self.db['product_to_charge_relationships'][product] = [charge]
            else:
                self.db['product_to_charge_relationships'][product].append(charge)

            if charge not in self.db['charge_to_product_relationships']:
                self.db['charge_to_product_relationships'][charge] = [product]
            else:
                self.db['charge_to_product_relationships'][charge].append(product)

        resp = f"Product to Charge relationship created: {relationship}"
        print_output("create_product_to_charge_relationship", relationship, resp)
        return resp


    def get_product_offer(self, query):
        if query is None:
            resp = "No query found in request body"
        else:
            business_id = query.get("business_id")
            resp = self.db['product_offers'].get(business_id)
            if resp is None:
                resp = "No Product Offer found for {}".format(business_id)
        print_output("get_product_offer", business_id, resp)
        return resp
    

    def get_charge(self, query):
        if query is None:
            resp = "No query found in request body"
        else:
            charge_id = query.get("charge_id")
            resp = self.db['charges'].get(charge_id)
            if resp is None:
                resp = "No Charge found for {}".format(charge_id)
        print_output("get_charge", charge_id, resp)
        return resp
    
    
    def get_child_relationships(self, query):
        if query is None:
            resp = "No query found in request body"
        else:
            parent_business_id = query.get("parent_business_id")
            resp = self.db['parent_to_child_relationships'].get(parent_business_id)
            if resp is None:
                resp = "No child relationships found for {}".format(parent_business_id)
        print_output("get_child_relationships", parent_business_id, resp)
        return resp
    

    def get_parent_relationships(self, query):
        if query is None:
            resp = "No query found in request body"
        else:
            child_business_id = query.get("child_business_id")
            resp = self.db['child_to_parent_relationships'].get(child_business_id)
            if resp is None:
                resp = "No parent relationships found for {}".format(child_business_id)
        print_output("get_parent_relationship", child_business_id, resp)
        return resp


    def get_charge_relationships(self, query):
        if query is None:
            resp = "No query found in request body"
        else:
            business_id = query.get("business_id")
            resp = self.db['product_to_charge_relationships'].get(business_id)
            if resp is None:
                resp = "No Charge relationships found for {}".format(business_id)
        print_output("get_charge_relationships", business_id, resp)
        return resp
