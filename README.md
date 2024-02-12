<img src="docs/images/daring_mechanician_banner.png" alt="Daring Mechanician"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">

[**Daring Mechanician** ](https://github.com/liebke/mechanician) is a Python library for building tools that use AI by building tools that AIs use. 

The approach of providing tools to Generative AIs to use can be described as **Tool Augmented Generation** (TAG) and the Generative AIs that use tools as **Tool Augmented Generative AIs** (TAG AIs).

*Daring Mechanician* provides tools for building, testing, and tuning *TAG AIs* and the tools that these AIs use, including support for AI-driven testing and AI-assisted *tuning* of the instruction sets given to an AI that we call **Instruction Auto-Tuning** (IAT).


# Tool Augmented Generation (TAG)

The **Tool Augmented Generation** (**TAG**) approach provides AIs with external tools, databases, and interfaces to enhance their knowledge, capabilities, and interaction with other systems.

This approach leverages the "**Function Calling**", or "**Tool Calling**", capabilities available in several Large Language Models and is meant to complement other approaches to augmenting Foundation Models, like **Fine Tuning** (FT) and **Retrieval Augmented Generation** (RAG). 

In contrast to **Retrieval Augmented Generation** (RAG), which uses a knowledge base to retrieve information and augment the prompt sent to the AI, **Tool Augmented Generation** (TAG) provides the AI with tools so that it can retrieve information itself, and also perform actions across multiple systems, databases, and interfaces.

>NOTE: You can build a RAG application using a TAG AI to create a **RAGTAG AI** Application.

Foundation Models are inherently limited by the scope of their training data and the static nature of that data, *Tool Augmented Generative AI* can access up-to-date information, perform computations, and interact with external systems; extending Generative AIs from pure knowledge repositories to active participants in information processing and generation.

This approach enhances the AI's problem-solving skills, creativity, and ability to provide accurate, up-to-date information.


## Designing Tools for AIs to Use

TAG AIs can be observed to problem solve, learning to use tools effectively through feedback provided by the tools themselves, so it is necessary for the tools to provide effective feedback, often through natural language, when reporting errors or providing results.

AIs will learn from their mistakes and successes, if the tools provide feedback that the AI can learn from.

See [Getting Started with Daring Mechanician](#getting-started-with-daring-mechanician) for an example of how to use the **Tool Augmented Generation** (TAG) approach to build a **Movie Database Assistant**.


## Instruction Tuning (IT)

In addition to learning from the feedback provided by the tools they use, TAG AIs can learn from the feedback they receive from users.

But since TAG AIs do not necessarily undergo further training, or Fine Tuning, that permanently encodes what they learned, they can only learn within the context window where feedback is received, and must start from scratch during the next session.

In order to make these learned behaviors persistent, they must be captured through a process of **Instruction Tuning**, where the initial instructions provided to the AI, the instructions provided for the tools the AI can use, and the feedback provided by those tools are revised and improved, incorporating lessons learned during interactions with users.

This process starts with creating an initial set of *AI Instructions*, *Tool Instructions*, and *Tool Feedback*, that are used to guide the AI's behavior and responses, and then iteratively refining those instructions and tool feedback based on the AI's performance during interactions with users.

At the start of this process, the prompting provided to the AI often consists of explict and detailed steps, but as the process proceeds, it is often discoverd that the AI does not need such detailed prompting, and that more general prompts can be used to guide the AI's behavior, and it will work out the details on its own.

In order to speed up this process, it is useful to use an **Evaluator AI** that acts as an *user surrogate*, interactively eliciting responses from the AI as the two work through multi-step tasks.

## Instruction Auto-Tuning (IAT)

By observing an AI's interactions with users and other AIs, an *Instructor AI* can refine and update the AI's current instructions and the instructions describing the tools the AI can use.

The Instructor AI is provided the AI's current set of instructions, instructions for the tools used by the AI, and the transcript of interactions between the AI and a User (or Evaluator AI), including the AI tool calls and responses.

See [Getting Started with Instruction Auto-Tuning](#getting-started-with-instruction-auto-tuning) for an example of how to use the **Instruction Auto-Tuning** (IAT) process to refine the instructions for a **Movie Database Assistant**.


## AI-Driven Testing

See [Getting Started with AI-Driven Testing](#getting-started-with-ai-driven-testing) for an example of how to use the **AI-Driven Testing** process to test a **Movie Database Assistant**.

## Getting Started Guide: Table of Contents

  - [Getting Started with Daring Mechanician](#getting-started-with-daring-mechanician)
    - [TAGAI Class](#tagai-class)
    - [AITools Abstract Class](#aitools-abstract-class)
    - [Instruction Sets](#instruction-sets)
      - [AI Instructions](#ai-instructions)
      - [Tool Instructions](#tool-instructions)
    - [AIConnector Classes](#aiconnector-classes)
      - [OpenAI Connectors](#openai-connectors)
      - [OpenAIChatConnector](#openaichatconnector)
      - [OpenAIAssistantsConnector](#openaiassistantsconnector)
    - [Running the AI](#running-the-ai)
  - [Getting Started with Instruction Auto-Tuning](#getting-started-with-instruction-auto-tuning)
  - [Getting Started with AI-Driven Testing](#getting-started-with-ai-driven-testing)
    - [AI Q&A Program Tests](#ai-q&a-program-tests)
    - [AI Task Evaluations](#ai-task-evaluations)
    - [Run AI-Driven Tests](#run-ai-driven-tests)
  - [Getting Started with Mechanician ArangoDB](#getting-started-with-mechanician-arangodb)
      - [Run ArangoDB in Docker](#run-arangodb-in-docker)
  - [Getting Started with the TMDb Example](#getting-started-with-the-tmdb-example)
    - [Example Interaction](#example-interaction)
    - [TMDb Example Code](#tmdb-example-code)
  - [Getting Started with the Arango Movie Database Example](#getting-started-with-the-arango-movie-database-example)
    - [Arango Movie Database Example Code](#arango-movie-database-example-code)
  - [Parallel Tool Calls and Streaming Responses](#parallel-tool-calls-and-streaming-responses)
    - [Environment Variables](#environment-variables)



## Getting Started with Daring Mechanician

**Daring Mechanician** consists of the following packages:

* [mechanician](https://github.com/liebke/mechanician/tree/main/packages/mechanician): the core package for building and running **Tool Augmented Generative AI** (TAG AI) programs.
* [mechanician-openai](https://github.com/liebke/mechanician/tree/main/packages/mechanician_openai): provides connectors to the *OpenAI Chat API* and the *OpenAI Assistants API*.
* [mechanician-arangodb](https://github.com/liebke/mechanician/tree/main/packages/mechanician_arangodb): provides tools for interacting with the ArangoDB graph database.

In the future, it will include packages for interacting with different LLM APIs and systems.

You will need to install *mechanician-openai* in order to run any of the example projects.

You can install it using pip:

```bash
pip install mechanician-openai
```

or you can clone this repo and install the latest version:

```bash
cd ./packages/mechanician-openai
./scripts/install.sh
```


The [```examples```](https://github.com/liebke/mechanician/tree/main/examples) directory contains examples of **Tool Augmented Generative AI** projects.

* [examples/tmdb](https://github.com/liebke/mechanician/tree/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/tmdb) is an example of a **Movie Database Assistant** that uses the *OpenAI Chat API* to answer questions about movies and their casts and crews.

* [examples/arango_movie_db](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/arango_movie_db) is an example of a **Movie Database Assistant** that uses the *ArangoDB* to record information on movies, their casts, and reviews.


### TAGAI Class

The TAGAI class is used to create instance of a **Tool Augmented Generative AI** (TAG AI).

```python
from mechanician import TAGAI

ai = TAGAI(ai_connector=ai_connector,
           ai_instructions=ai_instructions,
           tool_instructions=tool_instructions,
           tools=tools)
```

Alternatively, you can pass an `instruction_set_directory` to the constructor, and it will load the the *ai_instructions* and *tool_instructions* from the designated directory. 


```python
ai = TAGAI(ai_connector=OpenAIChatConnector(),
           instruction_set_directory="./instructions",
           tools=tools)
```


The `TAGAI` class takes the following parameters:

* [AIConnector](#aiconnector-classes): Provides a connection to a LLM API, such as the OpenAI Chat API or the OpenAI Assistants API.
* [AITools](#aitools-abstract-class): Provides a set of tools that the AI can use to interact with other systems, databases, and interfaces.
* [Instruction Set Directory](#instruction-sets): The directory containing the instruction for the TAG AI, describing its role and behaviors, and the instructions for the tools used by the AI.


Here are some examples of how to use the `TAGAI` class:

* [mechanician_tmdb/main.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/tmdb/src/mechanician_tmdb/main.py#L17): a TAG AI that uses `TMDbAITools` for interacting with the The Movie Database (TMDb) API, the `OpenAIChatConnector` to connect to the OpenAI Chat API.

* [examples/arango_movie_db/main.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/arango_movie_db/src/main.py#L16): a TAG AI that uses `DocumentManagerAITools` from the `mechanician-arangodb` package to interact with the ArangoDB graph database and the `OpenAIChatConnector` to connect to the OpenAI Chat API.

* [mechanician/instruction_tuning.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/packages/mechanician/src/mechanician/instruction_tuning.py#L43): an Instructor AI that uses `AutoTuningAITools` for tuning and updating the instructions for another AI, and the `OpenAIChatConnector` to connect to the OpenAI Chat API.
   


### AITools Abstract Class

The `AITools` class is the base class used to create AI tools.

```python
from mechanician import AITools

class ExampleAITools(AITools):
    def example_tool1(self, parameters):
        ...
```

Each tool method intended to be called by an AI takes a single parameter, a dict of input parameters, and returns a JSON serializable object.

These methods should fail gracefully, returning an error message if the tool call fails, and should provide detailed feedback to the AI about the results of the tool call.

Examples of AITools classes:

* [tmdb_tools.py](https://github.com/liebke/mechanician/blob/main/examples/tmdb/src/mechanician_tmdb/tmdb_ai_tools.py): `AITools` for interacting with The Movie Database (TMDb) API.

* [arango_movie_db_tools.py](https://github.com/liebke/mechanician/blob/main/packages/mechanician_arangodb/src/mechanician_arangodb/document_ai_tools.py): `AITools` for interacting with the ArangoDB graph database.

* [auto_tuning_ai_tools.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/packages/mechanician/src/mechanician/instruction_tuning.py#L62): `AITools` for tuning and updating the instructions for another AI.




### Instruction Sets

If you pass an `instruction_set_directory` to the `TAGAI` constructor, it will load the the *ai_instructions* and *tool_instructions* from the designated directory. 

```python
ai = TAGAI(ai_connector=OpenAIChatConnector(),
           instruction_set_directory="./instructions",
           tools=tools)
```

The default name and location of the directory is **./instructions**, and the default names for the instruction files are **ai_instructions.md** and **tool_instructions.json**.

Alternatively, you can pass the *ai_instructions* and *tool_instructions* directly to the `TAGAI` constructor.

```python
ai = TAGAI(ai_connector=ai_connector,
           ai_instructions=ai_instructions,
           tool_instructions=tool_instructions,
           tools=tools)
```

The advantage of storing the instruction in the `instruction_set_directory` is that it allows you to use the **Instruction Auto-Tuning** (IAT) process to refine the instructions for the AI.

* The `ai_instructions.json` file contains the instructions for the AI, defining its role and behaviors.

* The `tool_instructions.json` file contains the instructions for the tools used by the AI. In the case of the OpenAI Connectors, it contains JSON Schema describing the tools and their parameters.

```json
{
   "tool1": {
      "name": "tool1",
      "description": "Tool 1 Description",
      "parameters": {
         "parameter1": {
            "name": "parameter1",
            "description": "Parameter 1 Description"
         }
      }
   }
}
```

Some example instruction sets:

* [Arango Movie DB Example instructions.json](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/instructions)
* [TMDb Example instructions.json](https://github.com/liebke/mechanician/blob/main/examples/tmdb/instructions)


### AIConnector Classes

The `AIConnector` class is used to create a connection to a LLM API. There are currently connectors for OpenAI's Chat API and OpenAI's Assistants API. 

The roadmap includes connectors to other LLM APIs that support function calling, including connectors for local LLMs.


#### OpenAI Connectors

```bash
pip install mechanician-openai
```

```bash
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>
OPENAI_MODEL_NAME=gpt-4-0125-preview
```

#### OpenAIChatConnector

* [OpenAIChatConnector](https://github.com/liebke/mechanician/blob/main/packages/mechanician_openai/src/mechanician_openai/chat_ai_connector.py)


```python
from mechanician_openai import OpenAIChatConnector
```

#### OpenAIAssistantsConnector

* [OpenAIAssistantsConnector](https://github.com/liebke/mechanician/blob/main/packages/mechanician_openai/src/mechanician_openai/assistants_ai_connector.py)


```python
from mechanician_openai import OpenAIAssistantsConnector
```

```bash
export USE_OPENAI_ASSISTANTS_API = True
export ASSISTANT_ID=<YOUR_ASSISTANT_ID_HERE>
export CREATE_NEW_ASSISTANT=False
export DELETE_ASSISTANT_ON_EXIT=False
```

or create a `.env` file with the variables.


### Running the AI

```python
from mechanician import shell
```

```python
shell.run(ai)
```


## Getting Started with Instruction Auto-Tuning

See the [arango_movie_db example](https://github.com/liebke/mechanician/tree/main/examples/arango_movie_db) to see how to use the **Instruction Auto-Tuning** (IAT) process to refine the instructions for a **Movie Database Assistant**.

Use the TAGAI's `save_tuning_session` method to save the current tuning session, and then use the `auto_tune.sh` script to run the *Instructor AI* and start the an interactive instruction auto-tuning process. 

```python
ai.save_tuning_session()
```

```bash
./script/auto_tune.sh
```

Use the `/file` chat command to load the tuning session into the *Instructor AI*.

```bash
> /file ./tuning_sessions/tuning_session.json
```

It will begin by evaluating the AI's performance and describing its errors and successes, and then creating a revised draft of the AI's instructions and the tool, and tool parameter instructions, to improve the AI's performance. If the updated instruction set is satisfactory, you can ask the *Instructor* to commit the changes.

```bash
> commit the revisions.
```

The *Instructor's* evaluations of the *Assistant's* performance can be really useful, as are it's recommended changes to the instructions, but sometimes its revisions will only include instructions covering the errors it determined the *Assistant* made, and you may want to add additional instructions to cover other cases; you can do this by manually editing the draft instructions before commiting them or by asking the *Instructor* to make further revisions.

You can edit the draft instructions before commiting them, and you can also ask the *Instructor AI* to make further revisions. 


## Getting Started with AI-Driven Testing

### AI Q&A Program Tests

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

Examples of AI-Driven Q&A Tests:
* [examples/tmdb/test.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/tmdb/src/mechanician_tmdb/test.py)


### AI Task Evaluations

```python
from mechanician.testing import run_task_evaluation
import unittest

class TestAI(unittest.TestCase):

   def test_ai(self):
      ai = init_ai()
      evaluator_at = init_evaluator_ai()
      evaluation, messages = run_task_evaluation(ai, evaluator_ai)

      self.assertEqual(evaluation, "PASS")
```

Examples of AI-Driven Task Evaluations:

* [examples/arango_movie_db/test_ai.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/arango_movie_db/src/test_ai.py)


### Run AI-Driven Tests

```bash
$ python test.py
```



## Getting Started with mechanician-arangodb


### 
```python
from mechanician_arangodb import DocumentManagerAITools
from arango import ArangoClient
```

```python
arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
doc_tools = DocumentManagerAITools(arango_client, database_name=database_name)
```

```python
ai = TAGAI(ai_connector=ai_connector, 
           instruction_set_directory="./instructions",
           tools=doc_tools,
           name="Movie Document Manager AI")
```


Example project:
* [examples/arango_movie_db](https://github.com/liebke/mechanician/tree/main/examples/arango_movie_db)


Install the mechanician-arangodb, mechanician-openai packages, and example project using pip:

```bash
pip install mechanician-arangodb
pip install mechanician-openai
pip install -e .
```

Set up your environment variables or create a `.env` file with the following variables:

```bash
ARANGO_ROOT_PASSWORD=<YOUR_ARANGO_DATABASE_PASSWORD>
ARANGO_HOST=http://localhost:8529
```

#### Run ArangoDB in Docker

```bash
docker pull arangodb/arangodb
```

```bash
docker run -e ARANGO_ROOT_PASSWORD=${ARANGO_ROOT_PASSWORD} -p 8529:8529 -d --name arangodb-instance arangodb/arangodb
```

```bash
docker stop arangodb-instance
```

```bash
docker start arangodb-instance
```

#### Run the interactive TAG AI shell:

```bash
./run.sh
```

### Run the AI-Driven tests:

```bash
./test.sh
```


### Arango Movie Database Example Code

* [```examples/arango_movie_db/main.py```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/src/main.py): TODO. 

* [```mechanician_arangodb document_ai_tools.py```](https://github.com/liebke/mechanician/blob/main/packages/mechanician_arangodb/src/mechanician_arangodb/document_ai_tools.py): are the AITools available to the AI.

* [```examples/arango_movie_db/instructions/instructions.json```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/instructions/instructions.json): is a set of instructions for the AI that inform it of the tools available to it, and describe its role as a **Movie Database Assistant** that records information on movies, their casts, and reviews.

* [```example_prompts.md```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/example_prompts.md): provides a variety of approaches to interacting with the AI.

* [```examples/arango_movie_db/test_ai.py```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/src/test_ai.py): shows how to test **Daring Mechanician** programs by having an AI-driven set of tasks. 




## Getting Started with the TMDb Example

* [examples/tmdb](https://github.com/liebke/mechanician/tree/main/examples/tmdb)

Install Mechanician OpenAI and the example project using pip:

```bash
pip install mechanician-openai
pip install -e .
```

or install all the dependencies from a cloned mechanician repo:

```bash
./install.sh
```

Set up your environment variables or create a `.env` file with the following variables:

```bash
TMDB_API_KEY=<YOUR_TMDB_API_KEY>
TMDB_READ_ACCESS_TOKEN=<YOUR_READ_ACCESS_TOKEN>
```

Run the interactive TAG AI shell:

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


Run the AI-Driven tests:

```bash
./test.sh
```





### TMDb Example Code

* [```examples/tmdb/main.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/main.py): shows how to use **Daring Mechanician** to interact with *OpenAI's Chat API*, providing it with **tools** that can be used by the LLM to makes *callouts* to other programs. 

* [```tmdb_tool_schemas.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_tool_schemas.py): informs the LLM what tools are available to it.

* [```tmdb_tools.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_tools.py): is *function_handler* containing ```stub``` functions that are invoked when the LLM makes one or more ```tool_call``` requests.

* [```examples/tmdb/instructions.md```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/instructions.md): is a set of instructions for the LLM that inform it of the tools available to it, and describe its role as a **Movie Database Assistant** that answers questions about movies and their casts and crews.

* [```tmdb_example_prompts.md```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_example_prompts.md): provides a variety of approaches to interacting with the LLM.

* [```examples/tmdb/test.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/test.py): shows how to test **Daring Mechanician** programs by having the AI self-evaluate their responses given a testing rubric. 



## Getting Started with the Arango Movie Database Example

* [examples/arango_movie_db](https://github.com/liebke/mechanician/tree/main/examples/arango_movie_db)


```bash
./install.sh
```

```bash
./run.sh
```

```bash
./test.sh
```


## Parallel Tool Calls and Streaming Responses

It currently supports [*OpenAI's Chat API*](https://platform.openai.com/docs/overview) and [*OpenAI's Assistants API*](https://platform.openai.com/docs/overview), and specifically supports [OpenAI's *Function Calling*](https://platform.openai.com/docs/guides/function-calling), a.k.a.```tool_calls```, while [*streaming responses*](https://cookbook.openai.com/examples/how_to_stream_completions) from the *Chat API*. 

Each ```tool_call``` will be executed in a [```ThreadExecutor```](https://docs.python.org/3/library/concurrent.futures.html) as soon as it has completely streamed to the client, allowing it to perform *IO-bound* calls while other ```tool_calls``` continue to stream to the client.

### Environment Variables

```bash
export CALL_TOOLS_IN_PARALLEL=True
export MAX_THREAD_WORKERS=50
```

