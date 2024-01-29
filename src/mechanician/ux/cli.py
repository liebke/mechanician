from mechanician.ux.util import print_markdown
from mechanician.ai_connectors import AIConnector
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
            if prompt == '':
                continue

            print('')
            prompt = preprocess_prompt(prompt)
            resp = ai.submit_prompt(prompt)

            if ai.model["STREAMING"] == False:
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            # This should never happen with the Assistant API, just in the Chat API
            while resp == None:
                resp = ai.submit_prompt(None)

            print('\n')

        print(f"Exiting {ai.model['ASSISTANT_NAME']}...")
        return ai
            
    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        ai.clean_up()
        print("goodbye")


