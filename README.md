# OpenAI Assistant Project

## Overview
This project demonstrates how to interact with the OpenAI Assistant API using Python. It includes a script for setting up the environment, a Python module to handle API interactions, and an example usage script. The project uses the OpenAI Python library and manages API keys securely using environment variables.

## Features
- Interacts with OpenAI Assistant API using function calling
- Securely manages API keys using environment variables
- Includes example usage of translating text

## Prerequisites
- Conda (for environment management)
- Python 3.8

## Setup
1. **Clone the Repository**: Clone this repository to your local machine.

2. **Environment Setup**:
   - Run the `env_setup.sh` script to create and activate a Conda environment and install necessary packages.
     ```bash
     bash env_setup.sh
     ```

3. **Environment Variables**:
   - Create a `.env` file in the project root directory.
   - Add your OpenAI API key and Assistant ID to the `.env` file as follows:
     ```
     OPENAI_API_KEY=your_api_key_here
     OPENAI_ASSISTANT_ID=your_assistant_id_here
     ```
   - Replace `your_api_key_here` and `your_assistant_id_here` with your actual API key and Assistant ID.

## Usage
To use the project, run the `example_usage.py` script:

```bash
python example_usage.py
