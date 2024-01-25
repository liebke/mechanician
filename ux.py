from util import print_markdown
from apis.model_api import ModelAPI
from apis.streaming_model_api import StreamingModelAPI

# Import Markdown and Console from rich library for pretty terminal outputs
from rich.console import Console

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
    print('\n\n\n')


###############################################################################
## RUN_MODEL
###############################################################################

def run_model(api: ModelAPI):
    print_header()
    # Loop forever, processing user input from the terminal
    try:
        while True:
            # Get the user's prompt
            prompt = input("> ")

            # Skip empty prompts
            if prompt == '':
                continue

            prompt = preprocess_prompt(prompt)
            response = api.submit_prompt(prompt)
            
            print('')
            print_markdown(console, response)
            print('')

    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        api.clean_up()
        print("goodbye")


###############################################################################
## RUN_STREAMING_MODEL
###############################################################################

def run_streaming_model(api: StreamingModelAPI):
    print_header()
    # Loop forever, processing user input from the terminal
    try:
        while True:
            # Get the user's prompt
            prompt = input("> ")

            # Skip empty prompts
            if prompt == '':
                continue

            prompt = preprocess_prompt(prompt)
            stream = api.get_stream(prompt)
            resp = api.process_stream(stream)
            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            while resp == None:
                stream = api.get_stream("")
                resp = api.process_stream(stream)
            
    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        api.clean_up()
        print("goodbye")

