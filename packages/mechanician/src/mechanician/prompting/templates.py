import logging
from typing import List
import re
import os
import json


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
            return f"The PromptResources used by the Prompt Template are missing fields: {', '.join(missing_fields)}"

        resource_collection = {resource.name: resource.data for resource in self.resources}

        def replacer(match):
            keys = match.group(1).split('.')
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

        out = re.sub(r'\{\{([^}]+)\}\}', replacer, self.template_str)
        return out


    def _check_template_fields(self, template_str: str, resources: list):
        resource_collection = {resource.name: resource.data for resource in resources}
        missing_fields = []

        def check_field(field):
            keys = field.split('.')
            value = resource_collection
            for key in keys:
                if '[' in key and ']' in key:  # check if key contains an array index
                    key_name, index = key[:-1].split('[')  # split the key into the name and index
                    if isinstance(value, dict):
                        value = value.get(key_name, [])  # get the value at the key
                    if isinstance(value, list) and len(value) > int(index):
                        value = value[int(index)]  # get the element at the index
                    else:
                        return key
                else:
                    value = value.get(key, '')
                if not value:
                    return key
            return None

        matches = re.findall(r'\{\{([^}]+)\}\}', template_str)
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
        


###############################################################################
## RESOURCES
###############################################################################

class PromptResource:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data

    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
        else:
            raise AttributeError(f"'PromptResource' object has no attribute '{attr}'")
