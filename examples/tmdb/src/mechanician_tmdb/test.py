from mechanician.testing import QandATest, run_q_and_a_evaluations
import unittest
from main import init_ai
from mechanician_openai.chat_ai_connector import OpenAIChatAIConnector
from mechanician.tagai import TAGAI
import logging

logger = logging.getLogger(__name__)

###############################################################################
## AI_EVALUATOR
###############################################################################

def ai_evaluator():
    instructions = """You are a test-evaluator for an AI assistant. You are given a question and an answer. Your job is to determine if the answer is correct. If the answer is correct, respond with PASS. If the answer is incorrect, respond with FAIL."""
    ai_connector = OpenAIChatAIConnector()
    return TAGAI(ai_connector,
                 system_instructions=instructions, 
                 name="QandA Test Evaluator")


###############################################################################
## TEST
###############################################################################

class TestTMDbAI(unittest.TestCase):

    def test_ai_responses(self):
        ai = init_ai()
        tests = [QandATest(prompt="What is the name of the actor playing the titular character in the upcoming Furiosa movie?", 
                           expected="Anya Taylor-Joy"),
                 QandATest(prompt="What is the name of the actor plays Ken in the Barbie movie?",
                           expected="Ryan Gosling"),
                 QandATest(prompt="Who played Barbie?",
                           expected="Margot Robbie"),
                 QandATest(prompt="What is the first movie that the actor that plays the titual character in the upcoming Furiosa movie?", 
                           expected="The Witch")]
        
        # AI Evaluator
        results, messages = run_q_and_a_evaluations(ai, tests, ai_evaluator())
        # AI Self-Evaluation
        # results = run_tests(ai, tests)

        for result in results:
            self.assertEqual(result.evaluation, "PASS")


if __name__ == '__main__':
    unittest.main(verbosity=2)
