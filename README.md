
<!-- 
<h1 style="margin-bottom: 0; font-family: 'Copperplate', serif; color: black;">Daring Mechanician</h1>

<p style="margin-top: 0; font-family: 'Didot', serif; color: darkgrey;">Building tools that use AI and building tools that AIs use.</p>
-->

<!-- <img src="docs/images/mechanician.png" alt="Daring Mechanician" width="200" height="200">
 -->
<img src="docs/images/daring_mechanician3.png" alt="Daring Mechanician"  style="max-width: 100%; height: auto float: right;">

<!--
<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">"...if they could only have found the point of application for it, they would have constructed a lever capable of raising the earth and rectifying its axis. It was just this deficiency which baffled these <b>daring mechanicians</b>." -Jules Verne</p>
-->

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">

## Overview

[**Daring Mechanician** ](https://github.com/liebke/mechanician) is a Python library for building tools that use AI and building tools that AIs use. 

It currently supports [*OpenAI's Chat API*](https://platform.openai.com/docs/overview) and [*OpenAI's Assistants API*](https://platform.openai.com/docs/overview), and specifically supports [OpenAI's *Function Calling*](https://platform.openai.com/docs/guides/function-calling), a.k.a.```tool_calls```, while [*streaming responses*](https://cookbook.openai.com/examples/how_to_stream_completions) from the *Chat API*. 

Each ```tool_call``` will be executed in a [```ThreadExecutor```](https://docs.python.org/3/library/concurrent.futures.html) as soon as it has completely streamed to the client, allowing it to perform *IO-bound* calls while other ```tool_calls``` continue to stream to the client.

## Getting Started

The [```examples```](https://github.com/liebke/mechanician/tree/main/examples) directory contains examples of **Daring Mechanician** projects.


## The Movie Database (TMDb) Example


### Create a Virtual Environment (optional)

Using [*Conda*](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-python) for environment management:

```bash
conda create --name mechanician_env
conda activate mechanician_env
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
python main.py
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
