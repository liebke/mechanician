from mechanician.ux.util import print_markdown
from mechanician.ai_connectors import AIConnector
from rich.console import Console  
import logging

logger = logging.getLogger('mechanician.ux.cli')
logger.setLevel(level=logging.INFO)

console = Console()

###############################################################################
## PREPRCOESS_PROMPT
###############################################################################

def preprocess_prompt(ai, prompt):

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
        ai.model["RUNNING"] = False
        prompt = ''

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

def run(ai: AIConnector):
    # print_markdown(console, f"* MODEL_NAME: {llm_con.model['MODEL_NAME']}")
    print_header(name=ai.model['ASSISTANT_NAME'])
    # Loop forever, processing user input from the terminal
    ai.model["RUNNING"] = True
    try:
        while ai.model["RUNNING"] is True:
            # Get the user's prompt
            prompt = input("> ")

            # Skip empty prompts
            if prompt is '':
                continue

            print('')
            prompt = preprocess_prompt(ai, prompt)
            # If preprocessed prompt is None, we should skip it
            if prompt is '':
                continue

            resp = ai.submit_prompt(prompt)

            if ai.STREAMING == False:
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            # This should never happen with the Assistant API, just in the Chat API
            while resp == None:
                resp = ai.submit_prompt(None)

            print('\n')

        logging.info(f"Exiting {ai.model['ASSISTANT_NAME']}...")
        return ai
            
    except KeyboardInterrupt:
        logging.info("Ctrl+C was pressed, exiting...")
    except EOFError:
        logging.info("Ctrl+D was pressed, exiting...")
    finally:
        ai.clean_up()
        logging.info("goodbye")


