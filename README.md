# DandyHare

## Overview

DandyHare is a Python library for interacting with Large Language Model APIs, currently only *OpenAI's Chat API* and *OpenAI's Assistants API*, and specifically supports ```tool_calls``` while streaming responses from the *Chat API*. 

Each ```tool_call``` will be executed in a ```ThreadExecutor``` as soon as it has completely streamed to the client, allowing it to perform IO-bound calls while other ```tool_calls``` continue to stream to the client.


## Prerequisites

- Conda (for environment management)
- Python 3.8

## Setup
1. **Clone the Repository**: Clone this repository to your local machine.

2. **Environment Setup**:
   - ```conda create --name dandyhare_env```
   - ```conda activate dandyhare_env```
   - ```pip install .``` or ```pip install -e .``` installs the dandyhare package in editable mode, which means you can modify the code in the dandyhare package without having to reinstall it.

3. **Environment Variables**:
   - You will need an **OPENAI_API_KEY**.
   - See ```dot_env_example``` for examples of the environment variables you will need to set.
   - Create a `.env` file in the project root directory.


## Examples

The ```examples``` directory contains an example **DandyHare** project that shows how to:

* ```examples/offer_management_assistant/main.py```: shows how to use **DandyHare** to interact with *OpenAI's Chat API*, providing it with **tools** that can be used by the LLM to makes *callouts* to other programs. 

* ```tool_schemas.py```: informs the LLM what tools are available to it.

* ```tools.py```: is *function_handler* containing ```stub``` functions that are invoked when the LLM makes one or more ```tool_call``` requests.

* ```examples/offer_management_assistant/instructions.md```: is a set of instructions for the LLM that inform it of the tools available to it, and describe its role as a **Product Offer Management Assistant** that defines product offers consisting of **Bundles**, **Packages**, **Components**, **Charges**, and **Relationships** between those entities.

* ```example_prompts.md```: provides a variety of approaches to interacting with the LLM in order to construct **Product Offers**.
