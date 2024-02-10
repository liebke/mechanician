from mechanician import AITools
from mechanician.util import print_markdown
from rich.console import Console
import json
import os
from arango import ArangoClient
from mechanician_arangodb.document_manager import DocumentManager
import logging
import traceback

logger = logging.getLogger(__name__)

console = Console()

def print_output(function_name, input, output):
    # input_str = input
    try:
        input_str = json.dumps(input, indent=4)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON input: {input}")
    
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


class OfferManagementAITools(AITools):

    def __init__(self, database_name="offer_mgmt_db"):
        try:
            self.database_name = database_name
            self.client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
            self.doc_mgr = DocumentManager(self.client)
            self.database = self.doc_mgr.create_database(self.database_name)
            self.product_collection_name = 'products'
            self.charge_collection_name = 'charges'
            self.charge_link_collection_name = 'charge_to_offer_relationships'
            self.product_link_collection_name = 'product_relationships'
            self.product_collection = self.doc_mgr.create_document_collection(self.database, self.product_collection_name)
            self.charge_collection = self.doc_mgr.create_document_collection(self.database, self.charge_collection_name)
            self.product_link_collection = self.doc_mgr.create_link_collection(self.database, self.product_link_collection_name)
            self.charge_link_collection = self.doc_mgr.create_link_collection(self.database, self.charge_link_collection_name)
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.error(resp)
            return resp


    def load_db(self, db_filename):
        # with open(db_filename, 'r') as file:
        #     self.db = json.load(file)

        # print(f"Loaded DB from {db_filename}")
        # pprint(self.db)
        # return
        pass


    def create_product_offer(self, product_offer):
        try:
            if product_offer is None:
                resp = "No Product Offer found in request body"
                logging.info(resp)
                return resp
            else:
                business_id = product_offer.get("business_id")
                product_offer_type = product_offer.get("product_offer_type")
                name = product_offer.get("name")

                if business_id is None:
                    resp = "No business_id found in request body"
                    logging.info(resp)
                    return resp
                elif product_offer_type is None:
                    resp = "No product_offer_type found in request body"
                    logging.info(resp)
                    return resp
                elif name is None:
                    resp = "No name found in request body"
                    logging.info(resp)
                    return resp
                
                if product_offer_type.lower() not in ("bundle", "package", "component"):
                    resp = "Invalid product_offer_type"
                    logging.info(resp)
                    return resp
                
                self.doc_mgr.create_document(self.database, self.product_collection_name, business_id, product_offer)
                resp = f"Product Offer created: name = {name}, ID = {business_id}"

            print_output("create_product_offer", product_offer, resp)
            return resp
        except Exception as e:
            message = str(e)
            logging.error("EXCEPTION:")
            traceback.print_exc()
            resp = f"ERROR: {message}"
            logging.error(resp)
            return resp


    def create_charge(self, charge):
        try:
            if charge is None:
                resp = "No Charge found in request body"
                logging.info(resp)
                return resp
            else:
                charge_id = charge.get("charge_id")
                name = charge.get("name")
                if charge_id is None:
                    resp = "No charge_id found in request body"
                    logging.info(resp)
                    return resp
                elif name is None:
                    resp = "No name found in request body"
                    logging.info(resp)
                    return resp

                self.doc_mgr.create_document(self.database, self.charge_collection_name, charge_id, charge)
                resp = f"Charge created: name = {name}, ID = {charge_id}"
            print_output("create_charge", charge, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.info(resp)
            return resp


    def create_product_to_product_relationship(self, relationship):
        try:
            if relationship is None:
                resp = "No Product to Product relationship found in request body"
                logging.info(resp)
                return resp
            else:
                parent_id = relationship.get("parent_product_offer")
                child_id = relationship.get("child_product_offer")
                if parent_id is None or child_id is None:
                    resp = "No parent or child found in request body"
                    logging.info(resp)
                    return resp
                
                self.doc_mgr.link_documents(self.database,
                                            self.product_collection_name, 
                                            child_id,
                                            self.product_collection_name, 
                                            parent_id, 
                                            self.product_link_collection_name,
                                            link_attributes={'relation': 'child_of'})
                resp = f"Product to Product relationship created: {relationship}"
            print_output("create_product_to_product_relationship", relationship, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.info(resp)
            return resp


    def create_product_to_charge_relationship(self, relationship):
        try:
            if relationship is None:
                resp = "No Product to Charge relationship found in request body"
                logging.info(resp)
                return resp
            else:
                product_id = relationship.get("product_id")
                charge_id = relationship.get("charge_id")

            self.doc_mgr.link_documents(self.database,
                                        self.charge_collection_name, 
                                        charge_id, 
                                        self.product_collection_name, 
                                        product_id,
                                        self.charge_link_collection_name,
                                        link_attributes={'relation': 'charge_of'})
            resp = f"Product to Charge relationship created: {relationship}"
            print_output("create_product_to_charge_relationship", relationship, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.info(resp)
            return resp


    def get_product_offer(self, query):
        try:
            if query is None:
                resp = "No query found in request body"
                logging.info(resp)
                return resp
            else:
                business_id = query.get("business_id")
                resp = self.doc_mgr.get_document(self.database, self.product_collection_name, business_id)
                if resp is None:
                    resp = "No Product Offer found for {}".format(business_id)
            print_output("get_product_offer", business_id, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.info(resp)
            return resp
    

    def get_charge(self, query):
        try:
            if query is None:
                resp = "No query found in request body"
                logging.info(resp)
                return resp
            else:
                charge_id = query.get("charge_id")
                resp = self.doc_mgr.get_document(self.database, self.charge_collection_name, charge_id)
                if resp is None:
                    resp = "No Charge found for {}".format(charge_id)
            print_output("get_charge", charge_id, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.info(resp)
            return resp
    
    
    def list_child_products(self, query):
        try:
            if query is None:
                resp = "No query found in request body"
                logging.info(resp)
                return resp
            else:
                parent_business_id = query.get("parent_business_id")
                resp = self.doc_mgr.list_documents_linked_to(self.database,
                                                            self.product_collection_name,
                                                            parent_business_id,
                                                            self.product_collection_name,
                                                            self.product_link_collection_name)
                
                if resp is None:
                    resp = "No child products found for {}".format(parent_business_id)
            print_output("list_child_products", parent_business_id, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.info(resp)
            return resp
    

    def list_parent_products(self, query):
        try:
            if query is None:
                resp = "No query found in request body"
                logging.info(resp)
                return resp
            else:
                child_business_id = query.get("child_business_id")
                resp = self.doc_mgr.list_documents_linked_from(self.database,
                                                self.product_collection_name,
                                                child_business_id,
                                                self.product_collection_name,
                                                self.product_link_collection_name)
                if resp is None:
                    resp = "No parent products found for {}".format(child_business_id)
            print_output("list_parent_products", child_business_id, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            logging.info(resp)
            return resp


    def list_related_charges(self, query):
        try:
            if query is None:
                resp = "No query found in request body"
                print(resp)
                return resp
            else:
                business_id = query.get("business_id")
                resp = self.doc_mgr.list_documents_linked_to(self.database,
                                                self.product_collection_name,
                                                business_id,
                                                self.charge_collection_name,
                                                self.charge_link_collection_name)
                if resp is None:
                    resp = "No related Charges found for {}".format(business_id)
            print_output("list_related_charges", business_id, resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            print(resp)
            return resp
        

    def list_product_offers(self, params=None):
        try:
            resp = self.doc_mgr.list_documents(self.database, self.product_collection_name)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            print(resp)
            return resp
        

    def list_charges(self, params=None):
        try:
            resp = self.doc_mgr.list_documents(self.database, self.charge_collection_name)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            print(resp)
            return resp
        

    def list_product_relationships(self, params=None):
        try:
            resp = self.doc_mgr.list_links(self.database, self.product_link_collection_name)
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            print(resp)
            return resp
        

    def list_charge_relationships(self, params=None):
        try:
            resp = self.doc_mgr.list_links(self.database, self.charge_link_collection_name)
            return resp
        except Exception as e:
            message = str(e)
            resp = f"ERROR: {message}"
            print(resp)
            return resp
