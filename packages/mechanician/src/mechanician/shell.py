from mechanician import TAGAI
from mechanician.util import print_markdown
from rich.console import Console 
import logging
import subprocess

logger = logging.getLogger(__name__)
console = Console()

###############################################################################
## PREPRCOESS_PROMPT
###############################################################################

def preprocess_prompt(ai: 'TAGAI', prompt: str):

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

    elif prompt.startswith('/bye'):
        ai.RUNNING = False
        prompt = ''

    elif prompt.startswith('/$'):
        subprocess.run(prompt.replace('/$', '', 1), shell=True)
        # Return an empty prompt so that it's skipped
        return ''

    return prompt


###############################################################################
## PRINT_HEADER
###############################################################################

def print_header(name):
    print('\n\n\n')
    print_markdown(console, f"# {name}")
    print('\n\n\n')


###############################################################################
## RUN
###############################################################################

def run(ai: TAGAI):
    print_header(name=ai.name)
    # Loop while RUNNING is True, processing user input from the terminal
    ai.RUNNING = True
    try:
        while ai.RUNNING is True:
            # Get the user's prompt
            prompt = input("> ")

            # Skip empty prompts
            if prompt == '':
                continue

            print('')
            prompt = preprocess_prompt(ai, prompt)
            # If preprocessed prompt is None, we should skip it
            if prompt == '':
                continue

            resp = ai.submit_prompt(prompt)

            if not ai.streaming_connector():
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            # This should never happen with the Assistant API, just in the Chat API
            while resp == None:
                resp = ai.submit_prompt(None)

            print('\n')

        logging.info(f"Exiting {ai.name}...")
        return ai
            
    except KeyboardInterrupt:
        logging.info("Ctrl+C was pressed, exiting...")
    except EOFError:
        logging.info("Ctrl+D was pressed, exiting...")
    finally:
        ai.clean_up()
        logging.info("goodbye")

