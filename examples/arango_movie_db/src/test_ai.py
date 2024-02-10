from mechanician import TAGAI
from mechanician_openai import OpenAIChatConnector
from mechanician.testing import run_task_evaluation
from main import init_ai
import unittest
import os
from dotenv import load_dotenv
import pprint
import logging

from mechanician.training import InstructionAutoTuning

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

###############################################################################
## AI_EVALUATOR
###############################################################################

instructions = """

      Your specific role is to act like a movie reviewer creating documents representing the details of movies, directors, cast member, and reviews of each.
      You NEED to record each document in a document database with help of an AI Document Manager Assistant that RECORD your movie reviews.

        Below you will find a list of movies that you have watched and would like to review and RECORD into a database with the help of the Document Manager AI assistant.

        Ask the assistant to create documents for each movie 
         * then review the documents to ensure that the AI assistant has correctly recorded ALL the movie details you specified.

        You will ask the assistant to LINK each Credit to the correct movie
         * then review the documents to ensure that the AI assistant has correctly recorded the cast member details correctly.

        You will then ask the assistant to LINK your review of movie.
          * then review the documents to ensure that the AI assistant has correctly recorded the review details correctly.

        You will ask the assistant to LINK a review to each Credit
         * review the documents to ensure that the AI assistant has correctly recorded the review details correctly.

        Perform one step at a time.

        Verify after each step, documents should contain ALL the information you provided the ASSISTANT, MAKE SURE the assistant added all the requested FIELDS in each document.

        One you have completed creating ALL the data below and have validated that all the information has been created correctly by the AI Assistant, you will respond with a ONLY A SINGLE WORD, "PASS".

        BUT if NOT ALL THE INFORMATION has been CORRECTLY created by the AI Assistant, you will start your response with the word, "FAIL" and then explain why the AI Assistant has FAILED.

        You will receive a prompt with a single word: "START".

      [MOVIE REVIEW DATA]

      Create documents for each of the following movies, include attributes about the movie like its title, genre, release year, a summary;

      Then create documents for the directors of each movie;
       
      Then create documents for the top three cast members of each movie,
       
         and then provide reviews for the movies, the directors, and the cast members you selected.

      * The Matrix (1999) - Science Fiction

     [END MOVIE REVIEW DATA]

      """

#       * Inception (2010) - Science Fiction


def ai_evaluator():
     ai_connector = OpenAIChatConnector(api_key=os.getenv("OPENAI_API_KEY"), 
                                          model_name=os.getenv("OPENAI_MODEL_NAME"))
     return TAGAI(ai_connector,
                  ai_instructions=instructions, 
                  name="Task Evaluator")
                                    



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

            # Initialize AI
            ai = init_ai("test_db")
            logger.info("\n")
            
            # Run Task Evaluation
            evaluation, messages = run_task_evaluation(ai, ai_evaluator())
            logger.info("\n\n")
            logger.info(f"EVALUATION: {evaluation}")
            
            # Write Results to File
            with open(test_messages_path, 'w') as file:
                file.writelines(f"{message}\n" for message in messages)

            ## Evaluate Results
            self.assertEqual(evaluation, "PASS")

        finally:
            iat = InstructionAutoTuning(OpenAIChatConnector(api_key=os.getenv("OPENAI_API_KEY"), 
                                                              model_name=os.getenv("OPENAI_MODEL_NAME")))
            logger.info("Generating Instruction Auto Tuning...")
            training_transcript_path = os.path.join(dir_path, "training_transcript.json")
            iat.write_training_session_data(training_transcript_path)

            iat_prompt_path = os.path.join(dir_path, "iat_prompt.txt")
            iat.write_iat_prompt(training_transcript_path, iat_prompt_path)

            logger.info(f"\n\n\nDocument Collections:")
            doc_collections = ai.tools.list_document_collections()
            
            logger.info(pprint.pformat(doc_collections))
            logger.info(f"\n\n\nLink Collections:")
            link_collections = ai.tools.list_link_collections()
            logger.info(pprint.pformat(link_collections))
            
            logger.info(f"\n\n\nDocument Data:")
            for collection in doc_collections:
                resp = ai.tools.list_documents({"collection_name": collection})
                logger.info(pprint.pformat(resp))
            logger.info(f"\n\n\nLink Data:")
            for collection in link_collections:
                resp = ai.tools.list_links({"link_collection_name": collection})
                logger.info(pprint.pformat(resp))
            # CLEAN UP
            ai.tools.doc_mgr.delete_database("test_db")


if __name__ == '__main__':
    unittest.main(verbosity=2)
