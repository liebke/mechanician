#!/bin/bash

# Create a Conda environment
conda create -n openai_project python=3.8 -y

conda init
# Activate the environment
conda activate openai_project

# Install OpenAI library and python-dotenv
pip install openai python-dotenv
pip install openai
pip install rich
