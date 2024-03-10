import logging
from typing import List
import re
import os

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


###############################################################################
## TEMPLATES
###############################################################################

def generate_prompt(template_str: str, resources: List['PromptResource']):
    missing_fields = check_template_fields(template_str, resources)
    if missing_fields:
        return f"The PromptResources used by the Prompt Template are missing fields: {', '.join(missing_fields)}"

    resource_collection = {resource.name: resource.data for resource in resources}

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
        return str(value)

    out = re.sub(r'\{\{([^}]+)\}\}', replacer, template_str)
    return out


def check_template_fields(template_str: str, resources: list):
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



def read_prompt_template(template_filename, template_directory="./templates"):
    template_path = os.path.join(template_directory, template_filename)
    with open(template_path, 'r') as file:
        return file.read()
    


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


class PromptResourceCollection:
    def __init__(self, resources: List[PromptResource]):
        self.resources = {resource.name: resource for resource in resources}

    def __getattr__(self, resource_attr):
        resource_name, attr = resource_attr.split(".", 1)
        if resource_name not in self.resources:
            raise AttributeError(f"Resource not found: {resource_name}")
        else:
            return getattr(self.resources[resource_name], attr)
        
