from mechanician.testing import run_task_evaluation
import unittest
from main import ai_connector
from mechanician.openai.chat_ai_connector import OpenAIChatAIConnector
import os

from document_tool_handler import DocumentManagerToolHandler
from arango import ArangoClient

from dotenv import load_dotenv
from pprint import pprint

###############################################################################
## AI_EVALUATOR
###############################################################################

def ai_evaluator():
     instructions = """
      Your role is to act like a movie reviewer that has access to an AI assistant that can help you record your movie reviews.

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

      Movie: id: matrix, title: "The Matrix", year: 1999, genre: "Science Fiction".
      Cast: id: keanu_reeves, name: "Keanu Reeves", role: "Neo".
      Cast: id: laurence_fishburne, name: "Laurence Fishburne", role: "Morpheus".
      Cast: id: carrie_anne_moss, name: "Carrie-Anne Moss", role: "Trinity".
      Review: id: matrix_review, movie_id: matrix, rating: 5, review: "This is a great movie!".
      Review: id: keanu_reeves_review, cast_id: keanu_reeves, rating: 5, review: "Keanu Reeves is a great actor!".
      Review: id: laurence_fishburne_review, cast_id: laurence_fishburne, rating: 5, review: "Laurence Fishburne is a great actor!".
      Review: id: carrie_anne_moss_review, cast_id: carrie_anne_moss, rating: 5, review: "Carrie-Anne Moss is a great actor!".

      Movie: id: inception, title: "Inception", year: 2010, genre: "Science Fiction".
      Cast: id: leonardo_dicaprio, name: "Leonardo DiCaprio", role: "Cobb".
      Cast: id: ellen_page, name: "Ellen Page", role: "Ariadne".
      Review: id: inception_review, movie_id: inception, rating: 5, review: "This is a great movie!".
      Review: id: leonardo_dicaprio_review, cast_id: leonardo_dicaprio, rating: 5, review: "Leonardo DiCaprio is a great actor!".
      Review: id: elliot_page_review, cast_id: elliot_page, rating: 5, review: "Elliot Page is a great actor!".
      
     [MOVIE REVIEW DATA]

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
        try:
                
            load_dotenv()

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
            # Define the directory and file paths
            dir_path = "./test_results"
            test_messages_path = os.path.join(dir_path, "test_messages.txt")

            # Create the directory if it doesn't exist
            os.makedirs(dir_path, exist_ok=True)

            with open(test_messages_path, 'w') as file:
                file.writelines(f"{message}\n" for message in messages)

            ## Evaluate Results
            self.assertEqual(evaluation, "PASS")

            print(f"\n\n\nDocument Collections:")
            doc_collections = doc_tool_handler.doc_mgr.list_document_collections(doc_tool_handler.database)
            pprint(doc_collections)
            print(f"\n\n\nLink Collections:")
            link_collections = doc_tool_handler.doc_mgr.list_link_collections(doc_tool_handler.database)
            pprint(link_collections)

            print(f"\n\n\nDocument Data:")
            for collection in doc_collections:
                pprint(doc_tool_handler.doc_mgr.list_documents(doc_tool_handler.database, collection))
            print(f"\n\n\Link Data:")
            for collection in link_collections:
                pprint(doc_tool_handler.doc_mgr.list_links(doc_tool_handler.database, collection))


        finally:
            doc_tool_handler.doc_mgr.delete_database("test_db")


if __name__ == '__main__':
    unittest.main(verbosity=2)
