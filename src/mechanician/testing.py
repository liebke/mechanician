from mechanician.ux.util import print_markdown
from mechanician.ai_connectors import AIConnector
from rich.console import Console
from typing import List

###############################################################################
## TEST CLASS
###############################################################################

class QandATest:
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
        return f"QandATest(prompt={self.prompt}, expected={self.expected}, actual={self.actual}, evaluation={self.evaluation})"
    

###############################################################################
## RUN_TESTS
###############################################################################

def run_q_and_a_evaluations(ai: AIConnector, tests: List[QandATest], ai_evaluator=None):
    # If ai_evaluator is None, have the ai self-evaluate
    if ai_evaluator is None:
        ai_evaluator = ai

    results = []
    console = Console()

    try:
        for test in tests:
            prompt = test.prompt
            print_markdown(console, "------------------")
            print_markdown(console, "## TEST")
            print_markdown(console, f"```{prompt}```")
            resp = ai.submit_prompt(test.prompt)

            if ai.model["STREAMING"] == False:
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            while resp == None:
                resp = ai.submit_prompt(None)
                print('')

            # Record the response as the ACTUAL response
            test.actual = resp
            eval_instructions = """Below is an EXPECTED response to a question and an ACTUAL response given by a test taker to the same question. Does the ACTUAL response provide the expected answer? Respond with PASS or FAIL only."""

            print_markdown(console, f"* EVAL INSTRUCTIONS: ```{eval_instructions}```")
            print_markdown(console, f"* EXPECTED: ```{test.expected}```")
            print_markdown(console, f"* ACTUAL: ```{test.actual}```")
            print('\n')

            # Submit the evaluation prompt
            eval_prompt = eval_instructions
            eval_prompt += f"* EXPECTED RESPONSE: \"{test.expected}\"\n\n"
            eval_prompt += f"* ACTUAL RESPONSE: \"{test.actual}\"\n"
            # submit evaluation prompt to ai_evaluator
            resp = ai_evaluator.submit_prompt(eval_prompt)
            test.evaluation = resp
            results.append(test)
            print()
            print_markdown(console, "------------------")
            print('\n')

        print(f"Examinee Exiting ({ai.model['ASSISTANT_NAME']})...")
        print(f"Evaluator Exiting ({ai_evaluator.model['ASSISTANT_NAME']})...")

        return results
            
    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        ai.clean_up()
        print("goodbye")





###############################################################################
## RUN_EVALUATION
###############################################################################

def run_task_evaluation(ai: AIConnector, start_prompt, ai_evaluator):
    messages = []
    console = Console()
    prompt = start_prompt
    RUNNING = True
    print(f"START PROMPT > {start_prompt}")
    EVALUATION = None
    try:
        while RUNNING is True:
            print("\n\n")
            print("EVALUATOR:")
            eval_resp = ai_evaluator.submit_prompt(prompt)
            messages.append(f"EVALUATOR: {eval_resp}")
            print("\n\n")

            # Exit if the evaluator says "/bye"
            if eval_resp.startswith("PASS"):
                RUNNING = False
                EVALUATION = "PASS"
            elif eval_resp.startswith("FAIL"):
                RUNNING = False
                EVALUATION = "FAIL"

            print("ASSISTANT:")
            assist_resp = ai.submit_prompt(eval_resp)
            messages.append(f"ASSISTANT: {assist_resp}")

            if ai.model["STREAMING"] == False:
                print_markdown(console, resp)
                print('')

            # resp = None, tool_calls were processed and we need to get a new stream to see the model's response
            while assist_resp == None:
                assist_resp = ai.submit_prompt(None)
                print('')

            print('\n')
            messages.append(f"ASSISTANT: {assist_resp}")
            print("\n\n")
        
            prompt = assist_resp
            
        return EVALUATION, messages
    
    except KeyboardInterrupt:
        print("Ctrl+C was pressed, exiting...")
    except EOFError:
        print("Ctrl+D was pressed, exiting...")
    finally:
        ai.clean_up()
        print("goodbye")
