# Import necessary libraries
from dotenv import load_dotenv
from models.openai.assistants import init_model, submit_prompt, clean_up
# from pprint import pprint
# import os
import json
from util import print_markdown

# Import Markdown and Console from rich library for pretty terminal outputs
# from rich.markdown import Markdown
from rich.console import Console

# Load environment variables from a .env file
load_dotenv()
# Create a Console object for pretty terminal outputs
console = Console()


###############################################################################
## PREPRCOESS_PROMPT
###############################################################################

def preprocess_prompt(prompt):

    if prompt.startswith('/file'):
        filename = prompt.replace('/file ', '', 1)

        with open(filename, 'r') as file:
            prompt = file.read()
            print('')
            print_markdown(console, "------------------")
            print_markdown(console, "## INPUT FILE")
            print_markdown(console, f"``` \n{prompt}\n ```")
            print_markdown(console, "------------------")
            print('')

    return prompt


###############################################################################
## PRINT_HEADER
###############################################################################

def print_header():
    print('\n\n\n')
    print_markdown(console, """# Product Offer AI Assistant (Proof of Concept)""")
    print_markdown(console, """Hello! I'm your virtual assistant designed to help you create new product offers. 
                    With my assistance, you can efficiently build product hierarchies, define pricing 
                    entities, and establish relationships between products and associated charges or 
                    other products. Whether you are crafting bundles, packages, promotions, or any other 
                    product-related entities within Hansen Catalog Manager, I'm here to guide you through 
                    the process and provide support wherever needed. If you have any tasks in mind, 
                    please let me know, and we can get started on creating a new product offer together! 
                    \n\n"""
                )
    print('\n\n\n')


###############################################################################
## RUN_REPL
###############################################################################

def run_repl():
    # Loop forever, processing user input from the terminal
    try:
        while True:
            prompt = input("> ")
            # Skip empty prompts
            if prompt == '':
                continue

            prompt = preprocess_prompt(prompt)
            response = submit_prompt(model, prompt)
            
            print('')
            print_markdown(console, response)
            print('')

    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        clean_up(model)
        print("goodbye")


###############################################################################
## Main program execution
###############################################################################

model = init_model()
print_header()
run_repl()

###############################################################################
# End of file
