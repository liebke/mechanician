# DandyHare

<img src="https://github.com/liebke/dandyhare/tree/main/docs/images/dandyhare.jpg" alt="DandyHare" width="200" height="200">

## Overview

[**DandyHare** ](https://github.com/liebke/dandyhare) is a Python library for interacting with Large Language Model APIs, currently only [*OpenAI's Chat API*](https://platform.openai.com/docs/overview) and [*OpenAI's Assistants API*](https://platform.openai.com/docs/overview), and specifically supports [OpenAI's *Function Calling*](https://platform.openai.com/docs/guides/function-calling), a.k.a.```tool_calls```, while [*streaming responses*](https://cookbook.openai.com/examples/how_to_stream_completions) from the *Chat API*. 

Each ```tool_call``` will be executed in a [```ThreadExecutor```](https://docs.python.org/3/library/concurrent.futures.html) as soon as it has completely streamed to the client, allowing it to perform *IO-bound* calls while other ```tool_calls``` continue to stream to the client.


## Prerequisites

- [*Conda*](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-python) (for environment management)
- [*Python*](https://www.python.org) >= 3.8

## Setup
1. **Clone the Repository**: Clone this repository to your local machine.

2. **Environment Setup**:
   - ```conda create --name dandyhare_env```
   - ```conda activate dandyhare_env```
   - ```pip install .``` or ```pip install -e .``` installs the dandyhare package in editable mode, which means you can modify the code in the dandyhare package without having to reinstall it.

3. **Environment Variables**:
   - You will need an [**OPENAI_API_KEY**](https://platform.openai.com/api-keys).
   - See ```dot_env_example``` for examples of the environment variables you will need to set.
   - Create a `.env` file in the project root directory.


## Examples

The [```examples```](https://github.com/liebke/dandyhare/tree/main/examples) directory contains an example **DandyHare** project that shows how to:

* [```examples/offer_management_assistant/main.py```](https://github.com/liebke/dandyhare/blob/main/examples/offer_management_assistant/main.py): shows how to use **DandyHare** to interact with *OpenAI's Chat API*, providing it with **tools** that can be used by the LLM to makes *callouts* to other programs. 

* [```tool_schemas.py```](https://github.com/liebke/dandyhare/blob/main/examples/offer_management_assistant/tool_schemas.py): informs the LLM what tools are available to it.

* [```tools.py```](https://github.com/liebke/dandyhare/blob/main/examples/offer_management_assistant/tools.py): is *function_handler* containing ```stub``` functions that are invoked when the LLM makes one or more ```tool_call``` requests.

* [```examples/offer_management_assistant/instructions.md```](https://github.com/liebke/dandyhare/blob/main/examples/offer_management_assistant/instructions.md): is a set of instructions for the LLM that inform it of the tools available to it, and describe its role as a **Product Offer Management Assistant** that defines product offers consisting of **Bundles**, **Packages**, **Components**, **Charges**, and **Relationships** between those entities.

* [```example_prompts.md```](https://github.com/liebke/dandyhare/blob/main/examples/offer_management_assistant/example_prompts.md): provides a variety of approaches to interacting with the LLM in order to construct **Product Offers**.
