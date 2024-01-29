from mechanician.testing import Test, run_tests, run_evaluation
import unittest
from main import ai_connector
from mechanician.openai.chat_ai_connector import OpenAIChatAIConnector
import json

###############################################################################
## AI_EVALUATOR
###############################################################################

def ai_evaluator():
     instructions = """
      Your role is to act like a product manager that has access to an AI assistant that can create Product Offers on your behalf.
        Below you will find CSV data representing Product Offers that have not yet been created and that you would like to create with the help of the AI assistant.
        The AI assistant will start by offering to help you create a bundle of product offers.
        Be CONCISE and SPECIFIC in your instructions to the AI assistant.

        The Product Offers in the DATA HAS NOT BEEN CREATED YET, so you will need to instruct the AI assistant to create them. 
     
        Once all the Product Offers have been created, ask the AI assistant to retrieve all objects from the database and respond with the database data and printn a report containing all the objects created.
       
       ONCE YOU ARE SATISFIED BY THE FINAL REPORT, RESPOND WITH ONE A SINGLE COMMAND: /bye

      [PRODUCT OFFER DATA]
      """
     
     with open("./resources/bundle_test_data.csv", 'r') as file:
        instructions += file.read()

     instructions += """
          [END OF PRODUCT OFFER DATA]
      """

     return OpenAIChatAIConnector(instructions=instructions, 
                                  tool_schemas=None, 
                                  tool_handler=None,
                                  assistant_name="Test Evaluator")


###############################################################################
## TEST
###############################################################################

class TestAI(unittest.TestCase):
     def test_ai_responses(self):
          ai = ai_connector()
          seed_prompt = "Can you help me create a bundle of product offers. Please be concise and specific in your instructions."
          print("\n")
          results = run_evaluation(ai, seed_prompt, ai_evaluator())
          print("\n\n")
          print("DATABASE DATA:")
          print(json.dumps(ai.tool_handler.db, indent=4))


if __name__ == '__main__':
    unittest.main(verbosity=2)
