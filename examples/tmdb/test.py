from mechanician.testing import Test, run_tests
from mechanician.openai.chat_ai_connector import OpenAIChatAIConnector
from mechanician.openai.assistants_ai_connector import OpenAIAssistantAIConnector
from tmdb_tools import TMDbHandler
from tmdb_tool_schemas import tool_schemas
from dotenv import load_dotenv
import os
from pprint import pprint
from mechanician.ux.util import print_markdown
from rich.console import Console



###############################################################################
## Main program execution
###############################################################################

# Load environment variables from a .env file
load_dotenv()

with open("./instructions.md", 'r') as file:
    instructions = file.read()

tmdb_handler = TMDbHandler(os.getenv("TMDB_READ_ACCESS_TOKEN"))

# Initialize the model
ai = OpenAIChatAIConnector(instructions=instructions, 
                           tool_schemas=tool_schemas, 
                           tool_handler=tmdb_handler,
                           assistant_name="TMDB AI" )

# ai = OpenAIAssistantAIConnector(instructions=instructions, 
#                                 tool_schemas=tool_schemas, 
#                                 tool_handler=tmdb_handler,
#                                 assistant_name="TMDB AI")


# RUN TESTS
tests = [{"prompt": "What is the name of the actor playing the titular character in the upcoming Furiosa movie?", 
          "expected": "Anya Taylor-Joy"},
         {"prompt": "What is the name of the actor plays Ken in the Barbie movie?", 
          "expected": "Ryan Gosling"},
         {"prompt": "What is the first movie that the actor that plays the titual character in the upcoming Furiosa movie?", 
          "expected": "The Witch"},]

tests = []
tests.append(Test(prompt="What is the name of the actor playing the titular character in the upcoming Furiosa movie?", 
                  expected="Anya Taylor-Joy"))
tests.append(Test(prompt="What is the name of the actor plays Ken in the Barbie movie?",
                  expected="Ryan Gosling"))
tests.append(Test(prompt="What is the first movie that the actor that plays the titual character in the upcoming Furiosa movie?", 
                  expected="The Witch"))

results = run_tests(ai, tests)

console = Console()
print_markdown(console, "## TEST RESULTS")
pprint([r.to_dict() for r in results])

