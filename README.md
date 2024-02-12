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

The Instructor AI is provided the AI's current set of instructions, instructions for the tools used by the AI, the transcript of interactions between the AI and a User (or Evaluator AI), assessment results for the tasks the assistant is performing, including the AI tool calls and responses.

See [Getting Started with Instruction Auto-Tuning](#getting-started-with-instruction-auto-tuning) for an example of how to use the **Instruction Auto-Tuning** (IAT) process to refine the instructions for a **Movie Database Assistant**.


## AI-Driven Testing (AIT)

See [Getting Started with AI-Driven Testing](#getting-started-with-ai-driven-testing) for an example of how to use the **AI-Driven Testing** (AIT) process to test a **Movie Database Assistant**.

## Getting Started Guide: Table of Contents

- [Tool Augmented Generation (TAG)](#tool-augmented-generation-(tag))
  - [Designing Tools for AIs to Use](#designing-tools-for-ais-to-use)
  - [Instruction Tuning (IT)](#instruction-tuning-(it))
  - [Instruction Auto-Tuning (IAT)](#instruction-auto-tuning-(iat))
  - [AI-Driven Testing (AIT)](#ai-driven-testing-(ait))
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
  - [Getting Started with Mechanician ArangoDB](#getting-started-with-mechanician-arangodb)
      - [Run ArangoDB in Docker](#run-arangodb-in-docker)
  - [Getting Started with Instruction Auto-Tuning](#getting-started-with-instruction-auto-tuning)
  - [Getting Started with AI-Driven Testing](#getting-started-with-ai-driven-testing)
    - [AI Q&A Program Tests](#ai-q&a-program-tests)
    - [AI Task Evaluations](#ai-task-evaluations)
    - [Run AI-Driven Tests](#run-ai-driven-tests)
  - [Getting Started with the TMDb Example](#getting-started-with-the-tmdb-example)
    - [Example Interaction](#example-interaction)
    - [TMDb Example Code](#tmdb-example-code)
  - [Getting Started with the Arango Movie Database Example](#getting-started-with-the-arango-movie-database-example)
    - [Arango Movie Database Example Code](#arango-movie-database-example-code)
  - [Parallel Tool Calls and Streaming Responses](#parallel-tool-calls-and-streaming-responses)
    - [Environment Variables](#environment-variables)



## Getting Started with Daring Mechanician

```bash
pip install mechanician
```

The [```examples```](https://github.com/liebke/mechanician/tree/main/examples) directory contains examples of **Tool Augmented Generative AI** projects.


### TAGAI Class

* [mechanician_tmdb/main.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/tmdb/src/mechanician_tmdb/main.py#L28)

* [examples/arango_movie_db/main.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/examples/arango_movie_db/src/main.py#L27)

* [packages/mechanician/src/mechanician/instruction_tuning.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/packages/mechanician/src/mechanician/instruction_tuning.py#L50)
   
```python
from mechanician import TAGAI
```

```python
ai = TAGAI(ai_connector=ai_connector,
           ai_instructions=ai_instructions,
           tool_instructions=tool_instructions,
           tools=tools)
```

Alternatively, you can pass an `instruction_set_directory` to the `TAGAI` constructor, and it will load the instructions from an *instruction_set* JSON file, with a default name of `instructions.json`.


```python
ai = TAGAI(ai_connector=OpenAIChatConnector(),
           instruction_set_directory="./instructions",
           tools=tools)
```

* [AIConnector](#aiconnector-classes)
* [AITools](#aitools-abstract-class)
* [Instruction Sets](#instruction-sets)
  * [AI Instructions](#ai-instructions)
  * [Tool Instructions](#tool-instructions)


### AITools Abstract Class


Examples of AITools classes:

* [tmdb_tools.py](https://github.com/liebke/mechanician/blob/main/examples/tmdb/src/mechanician_tmdb/tmdb_ai_tools.py)

* [arango_movie_db_tools.py](https://github.com/liebke/mechanician/blob/main/packages/mechanician_arangodb/src/mechanician_arangodb/document_ai_tools.py)

* [auto_tuning_ai_tools.py](https://github.com/liebke/mechanician/blob/0f5b4a9d344f384499d2ed9aa01b0115f60c2acb/packages/mechanician/src/mechanician/instruction_tuning.py#L62)



```python
from mechanician import AITools

class AutoTuningAITools(AITools):
    def tool1(self, parameters):
        ...
```

### Instruction Sets

* [Arango Movie DB Example instrucions.json](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/instructions/instructions.json)

The `instruction_set_directory` contains an **instruction set** file, with a default name of `instructions.json`.

```json
{'ai_instructions': "...",
 'tool_instructions': {...}}
```


#### AI Instructions

`
As the AI Assistant, your primary goal is to support users in maintaining a database of JSON documents... 
`

#### Tool Instructions

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

### AIConnector Classes

#### OpenAI Connectors

```bash
pip install mechanician-openai
```

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>

export OPENAI_MODEL_NAME=gpt-4-0125-preview
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

ENVIRONMENT VARIABLES FOR THE ASSISTANT

```bash
export USE_OPENAI_ASSISTANTS_API = False
export ASSISTANT_ID=<YOUR_ASSISTANT_ID_HERE>
export CREATE_NEW_ASSISTANT=False
export DELETE_ASSISTANT_ON_EXIT=False
```

or create a `.env` file with the variables.


#### Running the AI

```python
from mechanician import shell
```

```python
shell.run(ai)
```

## Getting Started with Mechanician ArangoDB

* [examples/arango_movie_db](https://github.com/liebke/mechanician/tree/main/examples/arango_movie_db)


```bash
pip install mechanician-arangodb
```

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

```bash
./run.sh
```

```bash
./test.sh
```


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

It will begin by evaluating the AI's performance and describing its errors and successes, and then creating a revised draft of the AI's instructions and the tool, and tool parameter instructions, to improve the AI's performance. If the updated instruction set is satisfactory, you can ask the *Instructor AI* to commit the changes.

```bash
> commit the revisions.
```

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


### Run AI-Driven Tests

```bash
$ python test.py
```



## Getting Started with the TMDb Example

* [examples/tmdb](https://github.com/liebke/mechanician/tree/main/examples/tmdb)

```bash
export TMDB_API_KEY=<YOUR_TMDB_API_KEY>
export TMDB_READ_ACCESS_TOKEN=<YOUR_READ_ACCESS_TOKEN>
```

```bash
./install.sh
```

```bash
./run.sh
```

```bash
./test.sh
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

### Arango Movie Database Example Code

* [```examples/arango_movie_db/main.py```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/src/main.py): TODO. 

* [```mechanician_arangodb document_ai_tools.py```](https://github.com/liebke/mechanician/blob/main/packages/mechanician_arangodb/src/mechanician_arangodb/document_ai_tools.py): are the AITools available to the AI.

* [```examples/arango_movie_db/instructions/instructions.json```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/instructions/instructions.json): is a set of instructions for the AI that inform it of the tools available to it, and describe its role as a **Movie Database Assistant** that records information on movies, their casts, and reviews.

* [```example_prompts.md```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/example_prompts.md): provides a variety of approaches to interacting with the AI.

* [```examples/arango_movie_db/test_ai.py```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/src/test_ai.py): shows how to test **Daring Mechanician** programs by having an AI-driven set of tasks. 




## Parallel Tool Calls and Streaming Responses

It currently supports [*OpenAI's Chat API*](https://platform.openai.com/docs/overview) and [*OpenAI's Assistants API*](https://platform.openai.com/docs/overview), and specifically supports [OpenAI's *Function Calling*](https://platform.openai.com/docs/guides/function-calling), a.k.a.```tool_calls```, while [*streaming responses*](https://cookbook.openai.com/examples/how_to_stream_completions) from the *Chat API*. 

Each ```tool_call``` will be executed in a [```ThreadExecutor```](https://docs.python.org/3/library/concurrent.futures.html) as soon as it has completely streamed to the client, allowing it to perform *IO-bound* calls while other ```tool_calls``` continue to stream to the client.

### Environment Variables

```bash
export CALL_TOOLS_IN_PARALLEL=True
export MAX_THREAD_WORKERS=50
```

