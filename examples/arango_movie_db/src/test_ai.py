from mechanician.testing import run_task_evaluation
import unittest
from main import ai_connector
from mechanician_openai.chat_ai_connector import OpenAIChatAIConnector
import os
from mechanician_arangodb.document_tool_handler import DocumentManagerToolHandler
from arango import ArangoClient
from dotenv import load_dotenv
from pprint import pprint
import logging

from mechanician.training.instruction_auto_tuning import InstructionAutoTuning

logger = logging.getLogger('mechanician_arangodb.test_ai')
logger.setLevel(level=logging.INFO)

###############################################################################
## AI_EVALUATOR
###############################################################################

instructions = """

      For this training session, your specific role is to act like a movie reviewer that has access to an AI assistant that can help you record your movie reviews.

        Below you will find a list of movies that you have watched and would like to review with the help of the AI assistant.

        Ask the assistant to create documents for each movie 
         * then review the documents to ensure that the AI assistant has correctly recorded the movie details correctly.

        You will ask the assistant to LINK a Credit to the movie
         * then review the documents to ensure that the AI assistant has correctly recorded the cast member details correctly.

        You will then ask the assistant to LINK your review of movie.
          * then review the documents to ensure that the AI assistant has correctly recorded the review details correctly.

        You will ask the assistant to LINK a review to each Credit
         * review the documents to ensure that the AI assistant has correctly recorded the review details correctly.

        Perform one step at a time.

        Verify after each step.

        One you have completed creating ALL the data below and have validated that all the information has been created correctly by the AI Assistant, you will respond with a ONLY A SINGLE WORD, "PASS".

        BUT if NOT ALL THE INFORMATION has been CORRECTLY created by the AI Assistant, you will start your response with the word, "FAIL" and then explain why the AI Assistant has FAILED.

        You will receive a prompt with a single word: "START".

      [MOVIE REVIEW DATA]

      Create documents for each of the following movies, include attributes about the movie like its title, genre, release year, a summary;

      Then create documents for the directors of each movie;
       
      Then create documents for the top three cast members of each movie,
       
         and then provide reviews for the movies, the directors, and the cast members you selected.

      * The Matrix (1999) - Science Fiction
      * Inception (2010) - Science Fiction

     [END MOVIE REVIEW DATA]

      """

def ai_evaluator():
     return OpenAIChatAIConnector(instructions=instructions, 
                                  assistant_name="Task Evaluator")


###############################################################################
## TEST
###############################################################################

class TestOfferMgmtAI(unittest.TestCase):
     # maxDiff is set to None, so the full difference will be shown when an assertEqual assertion fails.
     maxDiff = None

     def test_ai_responses(self):
        try:
                
            load_dotenv()
            # Define the directory and file paths
            dir_path = "./test_results"
            test_messages_path = os.path.join(dir_path, "test_messages.txt")
            # Create the directory if it doesn't exist
            os.makedirs(dir_path, exist_ok=True)

            arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
            # Initialize the model
            doc_tool_handler = DocumentManagerToolHandler(arango_client, database_name="test_db")
            ai = ai_connector(doc_tool_handler)
            start_prompt = "START"
            print("\n")
            evaluation, messages = run_task_evaluation(ai, start_prompt, ai_evaluator())
            print("\n\n")
            print(f"EVALUATION: {evaluation}")
            

            # Write Results to File
            with open(test_messages_path, 'w') as file:
                file.writelines(f"{message}\n" for message in messages)

            ## Evaluate Results
            self.assertEqual(evaluation, "PASS")

        finally:
            iat = InstructionAutoTuning(ai)
            print("Generating Instruction Auto Tuning...")
            # print("#################################")
            # print(iat.get_training_session_data())
            training_transcript_path = os.path.join(dir_path, "training_transcript.json")
            iat.write_training_session_data(training_transcript_path)

            iat_prompt_path = os.path.join(dir_path, "iat_prompt.txt")
            iat.write_iat_prompt(training_transcript_path, iat_prompt_path)
            # print("#################################")

            logging.info(f"\n\n\nDocument Collections:")
            doc_collections = doc_tool_handler.doc_mgr.list_document_collections(doc_tool_handler.database)
            logging.info(doc_collections)
            logging.info(f"\n\n\nLink Collections:")
            link_collections = doc_tool_handler.doc_mgr.list_link_collections(doc_tool_handler.database)
            logging.info(link_collections)

            logging.info(f"\n\n\nDocument Data:")
            for collection in doc_collections:
                logging.info(doc_tool_handler.doc_mgr.list_documents(doc_tool_handler.database, collection))
            logging.info(f"\n\n\Link Data:")
            for collection in link_collections:
                logging.info(doc_tool_handler.doc_mgr.list_links(doc_tool_handler.database, collection))
            # CLEAN UP
            doc_tool_handler.doc_mgr.delete_database("test_db")


if __name__ == '__main__':
    unittest.main(verbosity=2)
