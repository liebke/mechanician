from pprint import pprint

def print_output(function_name, input, output):
    print('')
    print("------------------")
    print("FUNCTION CALLED")
    print(f"FUNCTION NAME: {function_name}")
    print("INPUT:")
    pprint(input)
    print("OUTPUT:")
    pprint(output)
    print("------------------")
    print('')
    return

def create_product_offer(function_name, call_id, args):
    # print("create_product called")
    resp = {
            "tool_call_id": call_id,  # use call_id directly
            "output": "product created",
    }
    print_output(function_name, args, resp)
    return resp

def create_charge(function_name, call_id, args):
    # print("create_charge called")
    resp = {
            "tool_call_id": call_id,  # use call_id directly
            "output": "charge created",
    }
    print_output(function_name, args, resp)
    return resp

def create_product_to_product_relationship(function_name, call_id, args):
    # print("create_product_to_product_relationship called")
    resp = {
            "tool_call_id": call_id,  # use call_id directly
            "output": "create_product_to_product_relationship created",
    }
    print_output(function_name, args, resp)
    return resp

def create_product_to_charge_relationship(function_name, call_id, args):
    # print("create_product_to_charge_relationship called")
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
