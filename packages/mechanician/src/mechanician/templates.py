import logging
from typing import List
import re
import os
import json
from mechanician.resources import PromptResource


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


###############################################################################
## PROMPT TEMPLATE
###############################################################################

class PromptTemplate:
    def __init__(self, 
                 template_str:str=None, 
                 template_filename:str=None, 
                 template_directory:str="./templates", 
                 resources: List['PromptResource']=[]):
    
        if template_filename is None:
           self.template_str = template_str
        else:
           self.template_str = self.read_prompt_template(template_filename=template_filename, 
                                                         template_directory=template_directory)
        self.resources = resources


    def generate_prompt(self):
        missing_fields = self._check_template_fields(self.template_str, self.resources)
        if missing_fields:
            error_msg = f"The PromptResources used by the Prompt Template are missing fields: {', '.join(missing_fields)}"
            raise ValueError(error_msg)

        resource_collection = {resource.name: resource.data for resource in self.resources}

        def replacer(match):
            # Stripping the matched key to remove any leading/trailing whitespace
            keys = match.group(1).strip().split('.')
            value = resource_collection
            for key in keys:
                if '[' in key and ']' in key:  # check if key contains an array index
                    key_name, index = key[:-1].split('[')  # split the key into the name and index
                    if isinstance(value, dict):
                        value = value.get(key_name, [])[int(index)]  # get the element at the index
                    elif isinstance(value, list):
                        value = value[int(key_name)]  # get the element at the index
                else:
                    value = value.get(key, '') if isinstance(value, dict) else ''
                if not value:
                    break

            # Pretty-print JSON values
            if isinstance(value, (dict, list)):
                return json.dumps(value, indent=4)
            else:
                return str(value)

        # Updated regex to handle optional whitespace around the variable names
        out = re.sub(r'\{\{\s*([^}]+?)\s*\}\}', replacer, self.template_str)
        return out


    def _check_template_fields(self, template_str: str, resources: list):
        resource_collection = {resource.name: resource.data for resource in resources}
        missing_fields = []

        def check_field(field):
            # Strip any leading or trailing whitespace from the whole field string
            keys = field.strip().split('.')
            value = resource_collection
            for key in keys:
                clean_key = key.strip()  # Strip whitespace around each key part
                if '[' in clean_key and ']' in clean_key:  # Check if key contains an array index
                    key_name, index = clean_key[:-1].split('[')  # Split the key into the name and index
                    index = index.strip()  # Strip any spaces around the index
                    if isinstance(value, dict):
                        value = value.get(key_name.strip(), [])  # Ensure to strip spaces from key_name
                    if isinstance(value, list) and len(value) > int(index):
                        value = value[int(index)]  # Access the element at the index
                    else:
                        return key_name
                else:
                    value = value.get(clean_key, '')
                if not value:
                    return clean_key
            return None

        # Update the regex to handle arbitrary whitespace around the variable names
        matches = re.findall(r'\{\{\s*([^}]+?)\s*\}\}', template_str)
        for match in matches:
            missing_field = check_field(match)
            if missing_field is not None:
                missing_fields.append(missing_field)

        return missing_fields


    def read_prompt_template(self, template_filename=None, template_directory="./templates"):
        template_path = os.path.join(template_directory, template_filename)
        with open(template_path, 'r') as file:
            self.template_str = file.read()

        return self.template_str
        

    def add_resource(self, resource_name: str, resource_data: dict):
        self.resources.append(PromptResource(resource_name, resource_data))


    def add_resources(self, resources: List[dict]):
        for resource in resources:
            resource_name = resource.get('name')
            if resource_name is None:
                raise ValueError("Resource name is required")
            resource_data = resource.get('data')
            if resource_data is None:
                raise ValueError("Resource data is required")
            self.resources.append(PromptResource(resource_name, resource_data))
        

