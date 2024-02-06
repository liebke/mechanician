from mechanician.testing import run_task_evaluation
import unittest
from offer_mgmt.main import ai_connector
from mechanician_openai.chat_ai_connector import OpenAIChatAIConnector
import json
import os


def compare_dicts_ignore_order(dict1, dict2):
     if isinstance(dict1, dict) and isinstance(dict2, dict):
          if dict1.keys() != dict2.keys():
               print(f"dict1.keys() != dict2.keys(): {dict1.keys()} != {dict2.keys()}")
               return False
          for key in dict1:
               if not compare_dicts_ignore_order(dict1[key], dict2[key]):
                    print(f"not compare_dicts_ignore_order(dict1[key], dict2[key]): {dict1[key]} != {dict2[key]}")
                    return False
     elif isinstance(dict1, list) and isinstance(dict2, list):
          if len(dict1) != len(dict2):
               print(f"len(dict1) != len(dict2): {len(dict1)} != {len(dict2)}") 
               return False
          for item in dict1:
               if not any(compare_dicts_ignore_order(item, other_item) for other_item in dict2):
                    print(f"not any(compare_dicts_ignore_order(item, other_item) for other_item in dict2): {item} != {dict2}")
                    return False
     else:
          return dict1 == dict2
     return True


###############################################################################
## AI_EVALUATOR
###############################################################################

def ai_evaluator():
     instructions = """
      Your role is to act like a product manager that has access to an AI assistant that can create Product Offers, Charges, and Relationships on your behalf.
        
        Below you will find CSV data representing a Bundle that includes Packages of Product Offers, Components of Product Offers, Charges associated with Product Offers, and Relationship that have not yet been created and that you would like to create with the help of the AI assistant.
        
        You will receive a prompt with a single word: "START".

        Once you have received the START prompt, you will need to instruct the AI assistant to create the Product Offers, Charges, and Relationships in the CSV data.

        You should work through the CSV data ONE ROW AT A TIME, DO NOT SKIP ANY ROWS.

        ONLY REQUEST THE AI TO CREATE ONE OBJECT AT A TIME, and then wait for the AI assistant to respond with the object created and the database data, and verify that the object was created correctly.

        For every Product Offer, make sure to request the creation of all Charges associated with the Product Offer, and ENSURE that any Relationships associated with the offer are also created.

        * When you request the creation of a PACKAGE you MUST ALSO create the relationship to its parent BUNDLE.
        * When you request the creation of a COMPONENT you MUST ALSO create the relationship to its parent PACKAGE OR COMPONENT if it exists.
        * For every Charge, make sure to ALWAYS CREATE Relationship to the associated Product Offers.

        If the object WAS NOT created correctly, meaning any attribute has a different name or value, an attribute is missing, or an extra attribute has been added, RESPOND with a single word: FAIL

        Be CONCISE and SPECIFIC in your instructions to the AI assistant.

        The Product Offers, Charges, and Relationships in the DATA HAS NOT BEEN CREATED YET, so you will need to instruct the AI assistant to create them. 
     
        Once all the Product Offers, Charges, and Relationships have been created, ask the AI assistant to retrieve all objects from the database and respond with the database data and print a report containing all the objects created.
       
       Once you have seen the final report, evaulate it to make sure it contains ALL THE OBJECTS you requested and respond with only a single word: PASS.

       If the final report DOES NOT contain ALL THE OBJECTS you requested, start your response with the word 'FAIL' followed by an explanation of why the final report is incorrect.

      [PRODUCT OFFER DATA]
      """
     
     with open("./resources/bundle2_test_data.csv", 'r') as file:
        instructions += file.read()

     instructions += """
          [END OF PRODUCT OFFER DATA]
      """

     return OpenAIChatAIConnector(instructions=instructions, 
                                  assistant_name="Task Evaluator")


###############################################################################
## TEST
###############################################################################

class TestOfferMgmtAI(unittest.TestCase):

     # maxDiff is set to None, so the full difference will be shown when an assertEqual assertion fails.
     maxDiff = None

     def test_ai_responses(self):
          ai = ai_connector()
          start_prompt = "START"
          print("\n")
          evaluation, messages = run_task_evaluation(ai, start_prompt, ai_evaluator())
          print("\n\n")
          print(f"EVALUATION: {evaluation}")
          

          # Write Results to File
          # Define the directory and file paths
          dir_path = "./test_results"
          generated_db_path = os.path.join(dir_path, "generated_db.txt")
          test_messages_path = os.path.join(dir_path, "test_messages.txt")

          # Create the directory if it doesn't exist
          os.makedirs(dir_path, exist_ok=True)

          print("DATABASE DATA:")
          print(json.dumps(ai.tool_handler.db, indent=4))
          # Now you can write to the file
          with open(generated_db_path, 'w') as file:
               file.write(json.dumps(ai.tool_handler.db, indent=4))

          with open(test_messages_path, 'w') as file:
               file.writelines(f"{message}\n" for message in messages)

          ## Evaluate Results
          self.assertEqual(evaluation, "PASS")

          with open("./resources/db2.json", 'r') as file:
               db_expected = json.loads(file.read())

          self.assertEqual(compare_dicts_ignore_order(ai.tool_handler.db, db_expected), True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
