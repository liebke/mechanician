

<img src="docs/images/daring_mechanician_banner.png" alt="Daring Mechanician"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">


[**Daring Mechanician** ](https://github.com/liebke/mechanician) is a Python library for building tools that use AI by building tools that AI use. 


### Tool Augmented Generation (TAG)

We describe an approach of providing AIs with external tools, databases, and interfaces to enhance their knowledge, capabilities, and interaction with other systems as **Tool Augmented Generation** (**TAG**); and a Generative AI that uses tools as a **Tool Augmented Generative AI** (**TAG AI**).

This approach leverages the "Function Calling" or "Tool Calling" capabilities of several Large Language Models and is meant to complement other approaches to augmenting Foundation Models, like **Fine Tuning** (FT) and **Retrieval Augmented Generation** (RAG).

This strategy broadens the knowledge base of the AI beyond its initial training data and also introduces a dynamic aspect to its learning and interaction capabilities, allowing for real-time data retrieval, analysis, and interaction with a wide range of digital environments.

Foundation Models are limited by the scope of their training data and the static nature of that data, Tool Augmented Generative AI can access up-to-date information, perform computations, generate visual content, and execute code in a controlled environment; extending Generative AIs from pure knowledge repositories to active participants in information processing and generation.

The Tool Augmentation means that the AI can, for example, use a web browsing tool to fetch the latest news or scientific research, interact with data visualization software to create complex graphs, or utilize a code execution environment to verify programming solutions. 

This approach enhances the AI's problem-solving skills, creativity, and ability to provide accurate, up-to-date information.


## Dual AI Co-Development (DACD)

* Dueling AIs Development Process (DADP)
* Dueting AIs Development Process (DADP)
* Collaborating AIs Development Process (CADP)

Daring Mechanician supports an approach to development and testing of *Tool Augmented Generative AIs* involving the use of an **Evaluator AI** that interacts with and evaluates the *AI under development* in order to enhance the efficiency and effectiveness of AI training and refinement processes. 

The Evaluator AI is designed to assess, critique, and potentially guide the development of another AI (the AI under development). This creates an interactive feedback loop that can speed up the iterative process of AI enhancement.

----
This approach integrates a secondary AI system, referred to as the Evaluator AI, into the development cycle of a primary AI system (the AI under development). The Evaluator AI's role is to assess the responses and behaviors of the primary AI, providing feedback that can be used to identify areas for improvement, refine the AI's responses to prompts, and optimize its interaction models. This process facilitates a more efficient and targeted development cycle by automating the evaluation phase.

**Facilitate the Discover of Bugs and Inaccuracies**: The Evaluator AI can systematically test the AI under development, identifying bugs, inaccuracies, or areas lacking in the AI's capabilities. This automated evaluation process accelerates the identification of issues, reducing the need for manual review and enabling quicker iterations.

**Facilitate the Discover of Emergent Behaviors**: The Evaluator AI can identify emergent behaviors in the AI under development, providing insights into how the AI processes prompts and generates responses. This information can guide the refinement of the AI's interaction models and prompt engineering strategies.

**Automated Evaluation**: The Evaluator AI automates the process of testing and evaluation, enabling quicker identification of bugs, inaccuracies, or areas lacking in the AI under development. This reduces the need for manual review and accelerates iterations.

**Prompt Engineering Feedback**: By interacting with the AI under development, the Evaluator AI provides direct feedback on how well the AI responds to various prompts. This information is crucial for refining prompt engineering strategies, aiming to enhance the accuracy and relevance of the AI’s responses.

**Synergistic Development Process**: The development of both the Evaluator AI and the AI under development should proceed in parallel, ensuring that improvements in one are reflected in the testing and evaluation methodologies of the other. This synergy is essential for the effective evolution of both systems.

**Interaction Model Insights**: The feedback loop between the two AIs offers insights into the effectiveness of the AI under development's interaction model. This includes how it processes and understands prompts, which can inform adjustments to make its interactions more natural and effective.

### Implementation Considerations
* Developers should ensure that the criteria used by the Evaluator AI for assessment are comprehensive and align with the goals of the AI under development.

* It's important to continuously update the evaluation metrics and methods to reflect the evolving capabilities of the AI under development and to capture a broad range of interaction scenarios.

* Data generated from the evaluations should be systematically analyzed to guide the refinement process, focusing on both enhancing strengths and addressing weaknesses.

----

### Synergistic Development

The concurrent development of the AI under development and the Evaluator AI necessitates a synergistic approach, ensuring that both AIs evolve in tandem to support each other’s improvement. This synergy can lead to innovations in AI interaction models, making them more robust and versatile.




## Tool Types

* Data Retrieval Tools (DRT)

* Data Management Tools (DMT)

* Information Modeling Tools (IMT)

* Data Transformation Tools (DTT)

* Data Analysis Tools (DAT)

* Data Visualization Tools (DVT)

* Data Reporting Tools (DRT)

* Data Security Tools (DST)

* Data Quality Tools (DQT)

* Data Governance Tools (DGT)

* Data Integration Tools (DIT)

* Data Storage Tools (DST)

* Data Processing Tools (DPT)

* Data Orchestration Tools (DOT)

* Data Monitoring Tools (DMT)

* Data Testing Tools (DTT)

* Data Evaluation Tools (DET)

* Data Training Tools (DTT)

* Data Deployment Tools (DDT)


## Learning within the Context Window

* **Like the Evaluator AI used in DACD, well written tools can provide essential feedback to the AI so it can learn how to use them effectively.**

**Watching as the AI learns to use the tools effectively, within a context window, through mistakes and errors can be used to improve the prompts and the tools themselves.**

By designing tools that can offer structured feedback, AIs are equipped to interpret the outcomes of their actions, understand the ramifications of errors, and recognize the success of correct executions. This feedback, especially when provided in a format that AI systems can parse and learn from, becomes a cornerstone for iterative learning.

### Adaptive Behavior and Problem Solving

The capacity for AI to learn (within the context window) from tool feedback paves the way for more adaptive problem-solving strategies. As AIs engage with a variety of tools, they accumulate experience that informs their future interactions. This experience enables the AI to choose the most effective tool for a given task, apply tools in novel combinations to solve complex problems, and even identify when no existing tool is adequate, potentially signaling the need for new tool development.

**Again all of this learning only occurs within a given context window, and it must be captured by improved instructions through prompt engineering and tool development in order to be retained and utilized in future interactions**


### Error Handling and Correction

Well-crafted error messages from tools serve a dual purpose: they highlight the nature of the mistake and guide the AI towards the correct course of action. This feedback is crucial for developing robust error handling and correction mechanisms within AI systems. Over time, AIs can learn to anticipate potential errors before they occur, apply learned corrections to similar future scenarios, and develop more nuanced understandings of task requirements and constraints.

### Conclusion

Incorporating feedback mechanisms within tools transforms them from static instruments into dynamic agents of learning in the AI ecosystem.

The Evaluator AI is primarily used during a testing process of an another AI, the responses from that evaluation process can be used to improve the instructions provided to the AI Under Development and the Evaluator AI. Since the LLMs are not undergoing training, they will only learn within the context window where feedback is received by them from either the evaluator or the tools they use. The long term learning is indirect through the learning process of the developer observing the interactions of the two AIs, and capturing and improving the instructions for both AIs.

**This begs the question, in addition to an evaluator AI meant to act the role of a human user of the AI system, can we create an Instructor AI meant to observe the interaction and improve the instructions for one or both AIs under observation? If so, how do we create the instructions for that Instructor AI?**




## Create Tool Sets that be orchstrated by AI-Driven Programs 



* AIs can take structured output from search-oriented tools and reason over it providing natural language responses to users.

* Write tools that provide natural language error messages to the AI so it can learn from its mistakes and correct its reasoning.

* Write tools that provide sufficient feedback even during non-error responses so the AI can learn from its successes as well as its mistakes, allowing it to improve its understanding of how the tools work.

* Discover how an AI can reason across multiple tools, and how to write tools that provide feedback to the AI so it can learn from its mistakes.

* Build tool combinations that an AI can orchestrate to solve multi-step tasks.


## Evaluator AIs to Test AI-Driven Programs

* Using an Evaluator AI to evaluate natural-language responses from a Q & A oriented AI-Driven Program

* Using an Evaluator AI to automate the interaction with a task-oriented AI-Driven Program

* Using an Evaluator AI to speed up the process of Prompt Engineering for an AI-Driven Programs
  
  * Prompt Engineering is the process of refining the prompts used to interact with an AI-Driven Program to improve the quality of the responses.

  * Will end up refining the prompts for both the Evaluator AI and the AI-Driven Program, improving your understanding of the task and the AI's understanding of the task.

  * Apply normal testing procedures to the program output once the AI-Driven Program has been refined through the Evaluator AI's interaction with it.


## Development Process

* Interactive prompting with the AI-Driven Program to refine the prompts used to interact with the AI-Driven Program.

* Create an Evaluator AI to automate the interaction with the AI-Driven Program, and to evaluate the responses against a rubric.

* Apply normal testing procedures to the program output once the AI-Driven Program has been refined through the Evaluator AI's interaction with it.

* Use the Evaluator to speed up the process of Prompt Engineering for the AI-Driven Program.

* Use the Evaluator to discover changes to the underlying models that effect the program's effectiveness and performance.


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
