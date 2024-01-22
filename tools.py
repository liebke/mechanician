from pprint import pprint
from pprint import pformat
# Import Markdown and Console from rich library for pretty terminal outputs
from rich.markdown import Markdown
from rich.console import Console
import json

console = Console()

def print_output(function_name, input, output):
    input_str = input
    try:
        # Try to load JSON data from input
        input_json = json.loads(input)
        input_str = json.dumps(input_json, indent=4)
    except json.JSONDecodeError:
        print(f"Invalid JSON input: {input}")
    
    output_str = json.dumps(output, indent=4)
    # print(f"INPUT TYPE: {type(input)}") # string

    print('')
    console.print(Markdown("------------------"))
    console.print(Markdown("## FUNCTION CALLED"))
    console.print(Markdown(f"* FUNCTION NAME: **{function_name}**"))
    console.print(Markdown("## INPUT"))
    console.print(Markdown(f"```\n {input_str}\n ```"))
    console.print(Markdown("## OUTPUT"))
    console.print(Markdown(f"``` \n{output_str}\n ```"))
    console.print(Markdown("------------------"))
    print('')
    return

def create_product_offer(function_name, call_id, args):
    resp = {
            "tool_call_id": call_id,  # use call_id directly
            "output": "product created",
    }
    print_output(function_name, args, resp)
    return resp

def create_charge(function_name, call_id, args):
    resp = {
            "tool_call_id": call_id,  # use call_id directly
            "output": "charge created",
    }
    print_output(function_name, args, resp)
    return resp

def create_product_to_product_relationship(function_name, call_id, args):
    resp = {
            "tool_call_id": call_id,  # use call_id directly
            "output": "create_product_to_product_relationship created",
    }
    print_output(function_name, args, resp)
    return resp

def create_product_to_charge_relationship(function_name, call_id, args):
    resp = {
            "tool_call_id": call_id,  # use call_id directly
            "output": "create_product_to_charge_relationship created",
    }
    print_output(function_name, args, resp)
    return resp


# Create a dictionary that maps parameter values to functions
dispatch_dict = {
    'createProductOffer': create_product_offer,
    'createCharge': create_charge,
    'createProductToProductRelationship': create_product_to_product_relationship,
    'createProductToChargeRelationship': create_product_to_charge_relationship,
}

def call_function(function_name, call_id, args):
    if function_name not in dispatch_dict:
        return f"Unknown Function: {function_name}"
    else:
        return dispatch_dict.get(function_name)(function_name, call_id, args)
