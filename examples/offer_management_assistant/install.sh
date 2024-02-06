#!/bin/bash

cd ../../packages/mechanician &&
./install.sh &&
cd ../mechanician_openai &&
./install.sh &&
cd ../mechanician_arangodb &&
./install.sh &&
cd ../../examples/offer_management_assistant/src &&
pip install -e .

echo "Make sure to set up your .env file, see the dot_env_example file for an example"