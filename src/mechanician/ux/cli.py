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

def run(llm_con: AIConnector):
    print_markdown(console, f"* MODEL_NAME: {llm_con.model['MODEL_NAME']}")
    print_header(name=llm_con.model['ASSISTANT_NAME'])
    # Loop forever, processing user input from the terminal
    llm_con.model["RUNNING"] = True
    try:
        while llm_con.model["RUNNING"] is True:
            # Get the user's prompt
            prompt = input("> ")

            # Skip empty prompts
            if prompt == '':
                continue

            print('')
            prompt = preprocess_prompt(prompt)
            resp = llm_con.submit_prompt(prompt)

            if llm_con.model["STREAMING"] == False:
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            # This should never happen with the Assistant API, just in the Chat API
            while resp == None:
                resp = llm_con.submit_prompt(None)

            print('\n')

        print(f"Exiting {llm_con.model['ASSISTANT_NAME']}...")
        return llm_con
            
    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        llm_con.clean_up()
        print("goodbye")


###############################################################################
## RUN_TEST
###############################################################################

def run_tests(llm_con: AIConnector, tests):
    print_markdown(console, f"* MODEL_NAME: {llm_con.model['MODEL_NAME']}")
    print_header(name=llm_con.model['ASSISTANT_NAME'])
    # Loop forever, processing user input from the terminal
    llm_con.model["RUNNING"] = True
    try:
        for test in tests:
            prompt = test["prompt"]
            print_markdown(console, f"## {prompt}")
            resp = llm_con.submit_prompt(test["prompt"])

            if llm_con.model["STREAMING"] == False:
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            while resp == None:
                resp = llm_con.submit_prompt(prompt)
                print('\n')

            # Record the response as the ACTUAL response
            test["actual"] = resp
            # Print the Evaluation Prompt
            print('\n\n')
            eval_instructions = "Below is your response. Does it include expected answer? Respond with PASS or FAIL\n\n"
            print_markdown(console, f"``` \n{eval_instructions}\n ```\n")
            print_markdown(console, f"* EXPECTED: ```{test['expected']}```\n")
            print('\n')
            print_markdown(console, f"* ACTUAL: \n\"{test['actual']}\"\n")
            print('\n')

            # Submit the evaluation prompt
            eval_prompt = eval_instructions
            eval_prompt += f"* EXPECTED RESPONSE: \"{test['expected']}\"\n\n"
            eval_prompt += f"* ACTUAL RESPONSE: \"{test['actual']}\"\n"
            resp = llm_con.submit_prompt(eval_prompt)

            print('\n\n')


        print(f"Exiting {llm_con.model['ASSISTANT_NAME']}...")
        return llm_con
            
    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        llm_con.clean_up()
        print("goodbye")

