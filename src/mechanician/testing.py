from mechanician.ux.util import print_markdown
from mechanician.ai_connectors import AIConnector
from rich.console import Console
from typing import List

console = Console()


class Test:
    prompt = None
    expected = None
    actual = None
    evaluation = None

    def __init__(self, prompt, expected):
        self.prompt = prompt
        self.expected = expected
        self.actual = None
        self.evaluation = None

    def to_dict(self):
        return {"prompt": self.prompt, "expected": self.expected, "actual": self.actual, "evaluation": self.evaluation}
    
    def __repr__(self):
        return f"Test(prompt={self.prompt}, expected={self.expected}, actual={self.actual}, evaluation={self.evaluation})"
    

###############################################################################
## RUN_TESTS
###############################################################################

def run_tests(llm_con: AIConnector, tests: List[Test]):
    # print_markdown(console, f"* MODEL_NAME: {llm_con.model['MODEL_NAME']}")
    # print_header(name=llm_con.model['ASSISTANT_NAME'])
    # Loop forever, processing user input from the terminal
    results = []
    try:
        for test in tests:
            prompt = test.prompt
            print_markdown(console, "------------------")
            print_markdown(console, "## TEST")
            print_markdown(console, f"```{prompt}```")
            resp = llm_con.submit_prompt(test.prompt)

            if llm_con.model["STREAMING"] == False:
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            while resp == None:
                resp = llm_con.submit_prompt(None)
                print('')

            # Record the response as the ACTUAL response
            test.actual = resp
            # Print the Evaluation Prompt
            eval_instructions = "Below is your response. Does it include expected answer? Respond with PASS or FAIL."
            print_markdown(console, f"* EVAL INSTRUCTIONS: ```{eval_instructions}```")
            print_markdown(console, f"* EXPECTED: ```{test.expected}```")
            print_markdown(console, f"* ACTUAL: ```{test.actual}```")
            print('\n')

            # Submit the evaluation prompt
            eval_prompt = eval_instructions
            eval_prompt += f"* EXPECTED RESPONSE: \"{test.expected}\"\n\n"
            eval_prompt += f"* ACTUAL RESPONSE: \"{test.actual}\"\n"
            resp = llm_con.submit_prompt(eval_prompt)
            test.evaluation = resp
            results.append(test)
            print()
            print_markdown(console, "------------------")
            print('\n')

        print(f"Exiting {llm_con.model['ASSISTANT_NAME']}...")
        return results
            
    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        llm_con.clean_up()
        print("goodbye")
