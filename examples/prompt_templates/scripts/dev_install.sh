#!/bin/bash

cd ../../packages/mechanician &&
./scripts/install.sh &&
cd ../mechanician_openai &&
./scripts/install.sh &&
cd ../../examples/prompt_templates &&
pip install -e .

echo "Make sure to set up your .env file, see the dot_env_example file for an example"