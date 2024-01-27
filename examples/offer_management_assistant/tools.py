# Import Markdown and Console from rich library for pretty terminal outputs
from mechanician.util import print_markdown
from mechanician.apis.tool_handler import ToolHandler
# from rich.markdown import Markdown
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


# # Create a dictionary that maps parameter values to functions
# dispatch_dict = {
#     'createProductOffer': create_product_offer,
#     'createCharge': create_charge,
#     'createProductToProductRelationship': create_product_to_product_relationship,
#     'createProductToChargeRelationship': create_product_to_charge_relationship,
# }

# def call_function(function_name, call_id, args):
#     if function_name not in dispatch_dict:
#         print(f"Unknown Function: {function_name}")
#         return f"Unknown Function: {function_name}"
#     else:
#         return dispatch_dict.get(function_name)(function_name, call_id, args)
