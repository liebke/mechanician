import csv
import json
import os
from mechanician.resources import ResourceConnector, ResourceConnectorProvisioner
from mechanician.tools import AITools, MechanicianToolsProvisioner
from pprint import pprint

###############################################################################
## ProductCatalogConnectorProvisioner
###############################################################################
    
class ProductCatalogConnectorProvisioner(ResourceConnectorProvisioner):
        
        def __init__(self, 
                     data_directory="./data", 
                     product_catalog_filename="product_catalog.csv"):
            self.data_directory = data_directory
            self.product_catalog_data = product_catalog_filename

    

        def create_connector(self, context: dict={}):
            # Use the context to control access to resources provided by the connector.
            # ...
            return ProductCatalogConnector(data_directory=self.data_directory,
                                           product_catalog_filename=self.product_catalog_data)


###############################################################################
## ProductCatalogConnector
###############################################################################

class ProductCatalogConnector(ResourceConnector):

    def __init__(self, data_directory="./data", product_catalog_filename="product_catalog.csv"):
        self.data_directory = data_directory
        self.product_catalog_data = product_catalog_filename
        self.product_catalog_path = os.path.join(data_directory, product_catalog_filename)
        self.product_catalog_data = self._csv_to_json(self.product_catalog_path)


    def _csv_to_json(self, file_path):
        # Open the CSV file
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            # Create a CSV reader object
            csv_reader = csv.reader(csv_file)
            
            # Read the headers (first row), modify them to be JSON safe
            headers = next(csv_reader)
            json_safe_headers = [header.lower().replace(' ', '_') for header in headers]
            
            # Initialize a list to hold all JSON objects
            json_objects = []
            
            # Process each row after the header
            for row in csv_reader:
                # Create a dictionary for the current row
                row_data = {json_safe_headers[i]: row[i] for i in range(len(row))}
                # Add the dictionary to the list of JSON objects
                json_objects.append(row_data)
            
            # Optionally, convert the list to a JSON string
            # json_data = json.dumps(json_objects, indent=4)
            return json_objects

    
    def list_products(self, params={}):
        return self.product_catalog_data
    

    def list_products_by_brand(self, params={}):
        brand = params.get("brand")
        return [product for product in self.product_catalog_data if product["brand"] == brand]
    

    def add_product(self, params={}):
        product = params.get("product")
        self.product_catalog_data.append(product)
        print("add_product called:")
        pprint(product)
        # with open(self.product_catalog_path, mode='w', encoding='utf-8') as json_file:
        #     json_file.write(self.product_catalog_data)
        return True
    

    def create_product_offer(self, params={}):
        brand = params.get("brand")
        product_family = params.get("product_family")
        products = self.list_products_by_brand({"brand": brand})
        return [{"name": "brand", "data": brand}, 
                {"name": "product_family", "data": product_family}, 
                {"name": "products", "data": products}]
    

###############################################################################
## CatalogAIToolsProvisioner
###############################################################################
    
class CatalogAIToolsProvisioner(MechanicianToolsProvisioner):
        
        def __init__(self, 
                     catalog_connector_provisioner, 
                     tool_instructions_file_name="catalog_ai_tool_instructions.json",
                     ai_instructions_file_name="catalog_ai_instructions.md",
                     instruction_set_directory="./src/instructions"):
            print("CatalogAIToolsProvisioner.__init__")
            self.catalog_connector_provisioner = catalog_connector_provisioner
            self.tool_instructions_file_name = tool_instructions_file_name
            self.ai_instructions_file_name = ai_instructions_file_name
            self.instruction_set_directory = instruction_set_directory
    

        def create_tools(self, context: dict={}):
            print("CatalogAIToolsProvisioner.create_tools")
            # Use the context to control access to resources provided by the connector.
            # ...
            catalog_connector = self.catalog_connector_provisioner.create_connector(context)
            return CatalogAITools(catalog_connector=catalog_connector,
                                  tool_instructions_file_name=self.tool_instructions_file_name,
                                  ai_instructions_file_name=self.ai_instructions_file_name,
                                  instruction_set_directory=self.instruction_set_directory)


###############################################################################
## CatalogAITools
###############################################################################

class CatalogAITools(AITools):

    def __init__(self,
                 catalog_connector,
                 tool_instructions_file_name="catalog_ai_tool_instructions.json",
                 ai_instructions_file_name="catalog_ai_instructions.md",
                 instruction_set_directory="./src/instructions"):
        print("CatalogAITools.__init__")
        self.catalog_connector = catalog_connector
        self.tool_instructions_file_name = tool_instructions_file_name
        self.ai_instructions_file_name = ai_instructions_file_name
        self.instruction_set_directory = instruction_set_directory


    def create_product_offer(self, params={}):
        missing_param = "__missing__"
        product = {'allowance_type': params.get("allowance_type", missing_param),
                   'allowance_unit': params.get("allowance_unit", missing_param),
                   'base_allowance': params.get("base_allowance", missing_param),
                   'base_nrc': params.get("base_nrc", missing_param),
                   'base_rc': params.get("base_rc", missing_param),
                   'brand': params.get("brand", missing_param),
                   'business_id': params.get("business_id", missing_param),
                   'category': params.get("category", missing_param),
                   'commercial_name': params.get("commercial_name", missing_param),
                   'final_nrc': params.get("final_nrc", missing_param),
                   'final_rc': params.get("final_rc", missing_param),
                   'product': params.get("product", missing_param),
                   'product_line': params.get("product_line", missing_param),
                   'promo_allowance': params.get("promo_allowance", missing_param)}
        # identify missing parameters in product
        missing_params = [key for key, value in product.items() if value == missing_param]
        if missing_params:
            error = {"error": f"You must include all the required parameters. Missing parameters: {missing_params}"}
            print("ERROR:")
            pprint(error)
            return error
        
        print("create_product_offer called:")
        pprint(product)
        
        return self.catalog_connector.add_product({"product": product})
        