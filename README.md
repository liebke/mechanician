

<img src="docs/images/daring_mechanician_banner.png" alt="Daring Mechanician"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">


[**Daring Mechanician** ](https://github.com/liebke/mechanician) is a Python library for building tools that use AI by building tools that AI use. 


# Tool Augmented Generation (TAG)

**Tool Augmented Generation** (**TAG**) describes an approach of providing AIs with external tools, databases, and interfaces to enhance their knowledge, capabilities, and interaction with other systems.

**Tool Augmented Generative AI** (**TAG AI**) describes a Generative AI that uses tools to complete tasks.

This approach leverages the "Function Calling", or "Tool Calling", capabilities of several Large Language Models and is meant to complement other approaches to augmenting Foundation Models, like **Fine Tuning** (FT) and **Retrieval Augmented Generation** (RAG). You can combine a RAG application with TAG AI to create a RAGTAG AI. :)

*Tool Augmented Generation* broadens the knowledge base of the AI beyond its initial training data and also introduces a dynamic aspect to its learning and interaction capabilities, allowing for real-time data retrieval, analysis, and interaction with a wide range of digital environments.

Foundation Models are inherently limited by the scope of their training data and the static nature of that data, *Tool Augmented Generative AI* can access up-to-date information, perform computations, generate visual content, and execute code in a controlled environment; extending Generative AIs from pure knowledge repositories to active participants in information processing and generation.

The *Tool Augmentated Generation* means that the AI can, for example, use a web browsing tool to fetch the latest news or scientific research, interact with data visualization software to create complex graphs, or utilize a code execution environment to verify programming solutions. 

This approach enhances the AI's problem-solving skills, creativity, and ability to provide accurate, up-to-date information.

## Designing Tools for AIs to Use

TAG AIs can be observed learning to use tools effectively through feedback provided by the tools themselves, so it is necessary for the tools to provide effective feedback, often through natural language, when reporting errors or providing results.

AIs will learn from their mistakes and successes, if the tools provide feedback that the AI can learn from.


# Instruction Tuning (IT)

TAG AIs can be observed learning from both feedback provided by the tools they use, and through the feedback they receive from the users.

But since TAG AIs do not necessarily undergo further training, or Fine Tuning, that provides permanent learning, they can only learn within the context window where feedback is received.

In order to make these learned behaviors persistent, they must be captured through a process of **Instruction Tuning**, where the initial instructions, or system instructions, and the feedback provided by the tools the AIs use are revised and improved.

This process starts with creating an initial set of *system instructions* and *tool feedback*, that are used to guide the AI's behavior and responses, and then iteratively refining those instructions based on the AI's performance during testing and assessment of the tasks they are required to perform.

At the start of this process, the prompting provided to the AI often consists of explict and detailed steps, but as the process proceeds, it is often discoverd that the AI does not need such detailed prompting, and that more general prompts can be used to guide the AI's behavior, and it will work out the details on its own.

In order to speed up this process, it is useful to use an **Evaluator AI** that acts as an *user surrogate*, interactively eliciting responses from the AI as the two work through multi-step tasks, with the Evaluator AI providing feedback to the AI on its performance and the quality of its responses.

## Instruction Auto-Tuning (IAT)

By observing these interactions, the developer can further refine the instructions provided to the AI, the feedback provided by the tools, and also the instructions provided to the Evaluator AI.

The question then becomes, can we create an **Instructor AI** meant to observe these interactions and improve the instructions for one or both AIs under observation?

We can provide the Instructor AI the current set of system instructions, the transcript of interactions between the AI and the Evaluator AI, the tools used by the AI, and any available objective performance metric for the tasks the assistant is performing, and then ask the Instructor AI to improve and refine the instructions for both the AI under development and the Evaluator AI.

Daring Mechanician provides tools to perform this **Instruction Auto-Tuning**.


## Getting Started

## Parallel Tool Calls and Streaming Responses

It currently supports [*OpenAI's Chat API*](https://platform.openai.com/docs/overview) and [*OpenAI's Assistants API*](https://platform.openai.com/docs/overview), and specifically supports [OpenAI's *Function Calling*](https://platform.openai.com/docs/guides/function-calling), a.k.a.```tool_calls```, while [*streaming responses*](https://cookbook.openai.com/examples/how_to_stream_completions) from the *Chat API*. 

Each ```tool_call``` will be executed in a [```ThreadExecutor```](https://docs.python.org/3/library/concurrent.futures.html) as soon as it has completely streamed to the client, allowing it to perform *IO-bound* calls while other ```tool_calls``` continue to stream to the client.

## Getting Started

The [```examples```](https://github.com/liebke/mechanician/tree/main/examples) directory contains examples of **Daring Mechanician** projects.


## The Movie Database (TMDb) Example


### Create a Virtual Environment (optional)

Using [*Conda*](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-python) for environment management:

```bash
conda create --name mechanician_tmdb_env
conda activate mechanician_tmdb_env
```

### Install Dependencies

```bash
cd examples/tmdb
./install.sh
```


### Set Environment Variables

You will need an [**OPENAI_API_KEY**](https://platform.openai.com/api-keys) and a [**TMDB_READ_ACCESS_TOKEN**](https://developers.themoviedb.org/3/getting-started/introduction) to run the example.


```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>
export TMDB_READ_ACCESS_TOKEN=<YOUR_TMDB_READ_ACCESS_TOKEN_HERE>
```

### Run the Example

```bash
./run.sh
```

### Example Interaction

```markdown
> what was the first movie that the actor that plays Furiosa in the upcoming movie Furiosa star in?

Calling external function: search_movie...
Calling external function: get_movie_by_id...
Calling external function: get_movie_credits...
Calling external function: get_actor_credits...


The first movie that Anya Taylor-Joy, the actor who plays Furiosa in the upcoming movie "Furiosa: A Mad Max Saga," starred in was "The Witch," where she played the character Thomasin. The film was released in 2015.

> 
```


### TMDb Example Code

* [```examples/tmdb/main.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/main.py): shows how to use **Daring Mechanician** to interact with *OpenAI's Chat API*, providing it with **tools** that can be used by the LLM to makes *callouts* to other programs. 

* [```tmdb_tool_schemas.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_tool_schemas.py): informs the LLM what tools are available to it.

* [```tmdb_tools.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_tools.py): is *function_handler* containing ```stub``` functions that are invoked when the LLM makes one or more ```tool_call``` requests.

* [```examples/tmdb/instructions.md```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/instructions.md): is a set of instructions for the LLM that inform it of the tools available to it, and describe its role as a **Movie Database Assistant** that answers questions about movies and their casts and crews.

* [```tmdb_example_prompts.md```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_example_prompts.md): provides a variety of approaches to interacting with the LLM.

* [```examples/tmdb/test.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/test.py): shows how to test **Daring Mechanician** programs by having the AI self-evaluate their responses given a testing rubric. 


### Import Statements

```python
from mechanician.ux.cli import run
from mechanician.openai.chat_ai_connector import OpenAIChatAIConnector
```

### Initialize The Service Connector

```python
ai = OpenAIChatAIConnector(instructions=instructions, 
                           tool_schemas=tool_schemas, 
                           tool_handler=tmdb_handler,
                           name="TMDB Assistant" )
```

### Run The AI

```python
run(ai)
```

### Tool Handler

```python
from mechanician.tool_handlers import ToolHandler
import requests

class TMDbHandler(ToolHandler):
    """Class for interacting with the TMDb API."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {'Authorization': f'Bearer {self.api_key}'}

    def search_movie(self, query_params):
        """Search for a movie by title and optionally by year."""
        query, year = query_params.get('query', None), query_params.get('year', None)
        url = f"{self.base_url}/search/movie"
        params = {
            "query": query
        }
        if year: params["year"] = year
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
```

### Tool Schemas

```json
{
   "type": "function",
   "function": {
         "name": "search_movie",
         "description": "Returns a list of movies matching the search criteria",
         "parameters": {
            "type": "object",
            "properties": {
               "query": {
                     "type": "string",
                     "description": "the search query"
               },
               "year": {
                     "type": "integer",
                     "description": "year of release"
               }
            },
            "required": ["query"]
         }
   }
}
```

### Instructions

`
You are an assistant that answers questions about movies and cast members using The Movie Database (TMDB), you have access to functions that will let you search for movies and people in movies, and you have 'get' functions that provide more details on the movies and people but you will need to get the 'id' from the search function results to pass to the 'get' functions.
`

### Environment Variables

```bash
# OPENAI API KEY
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>

# OPENAI MODEL NAME
MODEL_NAME=gpt-4-1106-preview

# ENVIRONMENT VARIABLES FOR THE ASSISTANT
ASSISTANT_ID=<YOUR_ASSISTANT_ID_HERE>
CREATE_NEW_ASSISTANT=False
DELETE_ASSISTANT_ON_EXIT=False

# ENVIRONMENT VARIABLES FOR THE STREAMING CHAT API
CALL_TOOLS_IN_PARALLEL=True
MAX_THREAD_WORKERS=10
```

## Testing AI-Drive Programs Can Be... Interesting

Testing system that require user interaction can benefit from AI-driven testing. 

An Evaluator AI can be used to interact with the AI System Under Test (AISUT), eliciting responses that can be evaluated against a rubric.

Evaluating natural language responses against a rubric can be challenging, and it helps to use an AI to evaluate the responses.

If an AI is intended to solve a task involving many steps, it can be useful to use an Evaluator AI automate the interaction with the AISUT, and to evaluate the responses against a rubric.

If the task is expected to result in structured data matching a known outcome, normal testing procedures can be applied once the strucutred output has been completed through the Evaluators AI's interaction with the AISUT.

Once automation of the interaction with the AI has been implemented, you will be able to perform prompt-engineering to refine the interactions and responses of the AI.


### AI Q and A Program Tests

```python
from mechanician.testing import QandATest, run_q_and_a_evaluations
import unittest

class TestAI(unittest.TestCase):

   def test_ai(self):
      ai = init_ai()
      evaluator_at = init_evaluator_ai()
      tests = [QandATest(prompt="What is the name of the actor playing the titular character in the upcoming Furiosa movie?", 
                        expected="Anya Taylor-Joy"),
               QandATest(prompt="What is the name of the actor plays Ken in the Barbie movie?",
                        expected="Ryan Gosling"),
               QandATest(prompt="Who played Barbie?",
                        expected="Margot Robbie"),
               QandATest(prompt="What is the first movie that the actor that plays the titual character in the upcoming Furiosa movie?", 
                        expected="The Witch")]
            
      results, messages = run_q_and_a_evaluations(ai, tests, evaluator_ai)

      for result in results:
         self.assertEqual(result.evaluation, "PASS")
```

### AI Self Evaluation Tests

TODO

### AI Task Evaluations

```python
from mechanician.testing import run_task_evaluation
import unittest

class TestAI(unittest.TestCase):

   def test_ai(self):
      ai = init_ai()
      evaluator_at = init_evaluator_ai()
      start_prompt = "START"
      evaluation, messages = run_task_evaluation(ai, start_prompt, evaluator_ai)

      self.assertEqual(evaluation, "PASS")
```


```markdown
### Run AI Self Evaluation Tests

```bash
$ python test.py

────────────────────────────────────────────────────────────────────────────────────────────────────

                                                             TEST                                                             
What is the name of the actor playing the titular character in the upcoming Furiosa movie?                                    
Calling external function: search_movie...
Calling external function: get_movie_credits...

The name of the actor playing the titular character, Furiosa, in the upcoming movie "Furiosa: A Mad Max Saga" is Anya Taylor-Joy.

 • EVAL INSTRUCTIONS: Below is your response. Does it include expected answer? Respond with PASS or FAIL.                     

 • EXPECTED: Anya Taylor-Joy                                                                                                  

 • ACTUAL: The name of the actor playing the titular character, Furiosa, in the upcoming movie "Furiosa: A Mad Max Saga" is   
   Anya Taylor-Joy.                                                                                                           


PASS
────────────────────────────────────────────────────────────────────────────────────────────────────


────────────────────────────────────────────────────────────────────────────────────────────────────

                                                             TEST                                                             
What is the name of the actor plays Ken in the Barbie movie?                                                                  
Calling external function: search_movie...
Calling external function: get_movie_credits...

The actor who plays Ken in the "Barbie" movie is Ryan Gosling.

 • EVAL INSTRUCTIONS: Below is your response. Does it include expected answer? Respond with PASS or FAIL.                     

 • EXPECTED: Ryan Gosling                                                                                                     

 • ACTUAL: The actor who plays Ken in the "Barbie" movie is Ryan Gosling.                                                     


PASS
────────────────────────────────────────────────────────────────────────────────────────────────────


────────────────────────────────────────────────────────────────────────────────────────────────────

                                                             TEST                                                             
What is the first movie that the actor that plays the titual character in the upcoming Furiosa movie?                         
Calling external function: get_actor_credits...
The first movie featuring Anya Taylor-Joy, the actor playing the titular character in the upcoming "Furiosa" movie, is "The Witch," where she played the character Thomasin.

 • EVAL INSTRUCTIONS: Below is your response. Does it include expected answer? Respond with PASS or FAIL.                     

 • EXPECTED: The Witch                                                                                                        

 • ACTUAL: The first movie featuring Anya Taylor-Joy, the actor playing the titular character in the upcoming "Furiosa" movie,
   is "The Witch," where she played the character Thomasin.                                                                   


PASS
────────────────────────────────────────────────────────────────────────────────────────────────────


Exiting TMDB AI...
goodbye
.
----------------------------------------------------------------------
Ran 1 test in 60.058s

OK
```


### AI Self Evaluation Tests Code

```python
from mechanician.openai.chat_ai_connector import OpenAIChatAIConnector
from mechanician.testing import Test, run_tests
import unittest

class TestAI(unittest.TestCase):

    def test_ai_responses(self):
        with open("./instructions.md", 'r') as file:
            instructions = file.read()

        tmdb_handler = TMDbHandler(os.getenv("TMDB_READ_ACCESS_TOKEN"))

        ai = OpenAIChatAIConnector(instructions=instructions, 
                                tool_schemas=tool_schemas, 
                                tool_handler=tmdb_handler,
                                assistant_name="TMDB AI" )

        tests = [Test(prompt="What is the name of the actor playing the titular character in the upcoming Furiosa movie?", 
                      expected="Anya Taylor-Joy"),
                Test(prompt="What is the name of the actor plays Ken in the Barbie movie?",
                     expected="Ryan Gosling"),
                Test(prompt="What is the first movie that the actor that plays the titual character in the upcoming Furiosa movie?", 
                     expected="The Witch")]

        results = run_tests(ai, tests)

        for result in results:
            self.assertEqual(result.evaluation, "PASS")
```



## Offer Management Assistant Example

The [```examples```](https://github.com/liebke/mechanician/tree/main/examples) directory contains an example **Daring Mechanician** project.

* [```examples/offer_management_assistant/main.py```](https://github.com/liebke/mechanician/blob/main/examples/offer_management_assistant/main.py): shows how to use **Daring Mechanician** to interact with *OpenAI's Chat API*, providing it with **tools** that can be used by the LLM to makes *callouts* to other programs. 

* [```tool_schemas.py```](https://github.com/liebke/mechanician/blob/main/examples/offer_management_assistant/tool_schemas.py): informs the LLM what tools are available to it.

* [```tools.py```](https://github.com/liebke/mechanician/blob/main/examples/offer_management_assistant/tools.py): is *function_handler* containing ```stub``` functions that are invoked when the LLM makes one or more ```tool_call``` requests.

* [```examples/offer_management_assistant/instructions.md```](https://github.com/liebke/mechanician/blob/main/examples/offer_management_assistant/instructions.md): is a set of instructions for the LLM that inform it of the tools available to it, and describe its role as a **Product Offer Management Assistant** that defines product offers consisting of **Bundles**, **Packages**, **Components**, **Charges**, and **Relationships** between those entities.

* [```example_prompts.md```](https://github.com/liebke/mechanician/blob/main/examples/offer_management_assistant/example_prompts.md): provides a variety of approaches to interacting with the LLM in order to construct **Product Offers**.
